"""
absorb-osp — Daemon Mode

Runs in the background to:
1. Listen for webhooks on a configurable port (POST /absorb)
2. Watch a directory for URL files (drop *.url files to trigger)
3. Log all events for audit
"""

import json
import logging
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

from . import __version__
from .lib.workflow import WorkflowEngine

logger = logging.getLogger("absorb-osp-daemon")


def start_daemon(port: int = 8765, watch_dir: Optional[str] = None):
    """Start the absorb-osp daemon.

    Args:
        port: Port for webhook listener (HTTP POST /absorb).
        watch_dir: Directory to watch for *.url files.
    """
    _setup_logging()
    engine = WorkflowEngine()

    print(f"\n🚀 absorb-osp daemon v{__version__} starting...")
    print(f"   Webhook port: {port}")
    print(f"   Watch directory: {watch_dir or 'not set'}")
    print(f"   Working dir: {engine.absorbed_dir}")
    print(f"\n📋 Available endpoints:")
    print(f"   POST http://localhost:{port}/absorb  — Trigger absorption")
    print(f"   GET  http://localhost:{port}/status  — Daemon status")
    print(f"   GET  http://localhost:{port}/health  — Health check")
    print("")

    if watch_dir:
        _watch_directory(watch_dir, engine)

    _start_webhook_server(port, engine)


def _setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def _start_webhook_server(port: int, engine: WorkflowEngine):
    """Start a minimal HTTP webhook server with CORS support."""
    try:

        class AbsorbHandler(BaseHTTPRequestHandler):
            """HTTP request handler for the daemon webhook."""

            def _set_cors(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def do_OPTIONS(self):
                """Handle CORS preflight."""
                self.send_response(204)
                self._set_cors()
                self.end_headers()

            def do_POST(self):
                if self.path == "/absorb":
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length).decode()
                    try:
                        data = json.loads(body)
                        url = data.get("url", "")
                        if not url:
                            self._respond(400, {"status": "error",
                                                "message": "Missing 'url' field"})
                            return
                        logger.info(f"Received absorption request: {url}")
                        result = engine.run(url)
                        self._respond(200, {
                            "status": "ok",
                            "url": url,
                            "success": result.success,
                            "report": result.report_path,
                        })
                    except json.JSONDecodeError:
                        self._respond(400, {"status": "error",
                                            "message": "Invalid JSON body"})
                    except Exception as e:
                        logger.error(f"Workflow failed: {e}")
                        self._respond(500, {"status": "error", "message": str(e)})
                else:
                    self._respond(404, {"status": "not_found"})

            def do_GET(self):
                if self.path == "/health":
                    self._respond(200, {"status": "healthy", "version": __version__})
                elif self.path == "/status":
                    projects = engine.list_absorbed()
                    self._respond(200, {
                        "status": "running",
                        "version": __version__,
                        "absorbed_count": len(projects),
                        "projects": [p["name"] for p in projects],
                    })
                else:
                    self._respond(404, {"status": "not_found"})

            def _respond(self, code: int, data: dict):
                body = json.dumps(data).encode()
                self.send_response(code)
                self._set_cors()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, fmt, *args):
                logger.info(f"{self.client_address[0]} - {fmt % args}")

        server = HTTPServer(("0.0.0.0", port), AbsorbHandler)
        logger.info(f"Webhook server listening on port {port}")
        server.serve_forever()

    except OSError as e:
        logger.error(f"Failed to start server on port {port}: {e}")
        if "10013" in str(e):
            logger.error(f"Port {port} is already in use. Try a different port with --port.")
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user")
        print("\n👋 Daemon stopped.")


def _watch_directory(watch_dir: str, engine: WorkflowEngine):
    """Watch a directory for new *.url files in a background thread.

    Each .url file should contain a GitHub URL as its first line.
    After processing, files are renamed to .processed.
    """

    def watcher():
        path = Path(watch_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Watching directory: {watch_dir}")

        seen: set = set()
        while True:
            try:
                for f in sorted(path.glob("*.url")):
                    if f.name in seen:
                        continue
                    seen.add(f.name)
                    try:
                        url = f.read_text(encoding="utf-8").strip()
                        if not url or not ("github.com" in url or url.startswith("http")):
                            logger.warning(f"Skipping invalid URL in {f.name}: {url}")
                            continue
                        logger.info(f"Detected URL file: {f.name} → {url}")
                        engine.run(url)
                        processed = f.with_suffix(".processed")
                        f.rename(processed)
                        logger.info(f"Processed: {f.name} → {processed.name}")
                    except Exception as e:
                        logger.error(f"Failed to process {f.name}: {e}")
            except Exception as e:
                logger.error(f"Watcher error: {e}")
            time.sleep(2)

    t = threading.Thread(target=watcher, daemon=True)
    t.start()
