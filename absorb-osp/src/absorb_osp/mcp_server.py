"""
absorb-osp — MCP Protocol Server

Exposes the absorption workflow as MCP tools for AI agent integration.
Compatible with Claude Code, Hermes Agent, and any MCP client.

Tools:
    absorb_project(url, depth)     — Run 12-step absorption on a GitHub URL
    list_projects()                — List all absorbed projects
    get_project_status(name)       — Get detailed project information
    check_privacy(path)            — Run privacy leak scan
    validate_report(file)          — Validate an analysis report
    system_status()                — Get system health and info
"""

import json
import sys
from pathlib import Path

from . import __version__
from .lib.scanner import scan_for_leaks, security_scan
from .lib.workflow import WorkflowEngine

try:
    from mcp.server import FastMCP
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def create_server():
    """Create the MCP server if the mcp package is available."""
    if not HAS_MCP:
        return None

    mcp = FastMCP(
        "absorb-osp",
        description="Open-source project absorption workflow — 12-step closed-loop flywheel",
    )

    engine = WorkflowEngine()

    @mcp.tool()
    def absorb_project(url: str, depth: str = "auto") -> str:
        """Run the 12-step absorption workflow on a GitHub URL.

        Args:
            url: GitHub repository URL to absorb.
            depth: Absorption depth (auto/L1/L2/L3/L4/L5). Default 'auto' lets the judge decide.

        Returns:
            JSON string with workflow results including analysis report path.
        """
        try:
            result = engine.run(url)
            return json.dumps({
                "success": result.success,
                "project": result.project.name if result.project else "unknown",
                "report_path": result.report_path,
                "steps_completed": len([s for s in result.steps if s.status == "passed"]),
                "error": result.error,
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            }, indent=2)

    @mcp.tool()
    def list_projects() -> str:
        """List all previously absorbed projects from the index.

        Returns:
            JSON string with list of projects (name, type, depth, status, date).
        """
        projects = engine.list_absorbed()
        return json.dumps(projects, indent=2)

    @mcp.tool()
    def get_project_status(name: str) -> str:
        """Get detailed status of an absorbed project.

        Args:
            name: Name of the absorbed project to check.

        Returns:
            JSON string with project status details.
        """
        projects = engine.list_absorbed()
        for p in projects:
            if p["name"].lower() == name.lower():
                return json.dumps(p, indent=2)
        return json.dumps({"error": f"Project '{name}' not found"}, indent=2)

    @mcp.tool()
    def check_privacy(path: str = ".") -> str:
        """Run a privacy leak scan on the specified path.

        Args:
            path: Directory path to scan for privacy leaks.

        Returns:
            JSON string with scan results.
        """
        try:
            findings = scan_for_leaks(path)
            return json.dumps({
                "findings_count": len(findings),
                "findings": findings[:20],
                "pass": len(findings) == 0,
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "pass": False}, indent=2)

    @mcp.tool()
    def validate_report(file: str) -> str:
        """Validate an absorption analysis report file.

        Args:
            file: Path to the analysis report markdown file.

        Returns:
            JSON string with validation result.
        """
        path = Path(file)
        if not path.exists():
            return json.dumps({"valid": False, "error": "File not found"})
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            if content.startswith("---"):
                parts = content.split("---", 2)
                valid = len(parts) >= 3
                sections = len(parts[2].split("## ")) - 1 if valid else 0
                return json.dumps({
                    "valid": valid,
                    "sections": sections,
                    "has_frontmatter": True,
                }, indent=2)
            return json.dumps({"valid": False, "error": "Missing frontmatter"})
        except Exception as e:
            return json.dumps({"valid": False, "error": str(e)}, indent=2)

    @mcp.tool()
    def system_status() -> str:
        """Get system health and configuration information.

        Returns:
            JSON string with system status.
        """
        projects = engine.list_absorbed()
        return json.dumps({
            "version": __version__,
            "absorbed_count": len(projects),
            "projects": [p["name"] for p in projects],
            "absorbed_dir": str(Path(engine.absorbed_dir).resolve()),
        }, indent=2)

    return mcp


def start_mcp_server():
    """Start the MCP server for agent integration."""
    server = create_server()
    if server is None:
        print("❌ MCP server requires the 'mcp' package:")
        print("   pip install mcp")
        sys.exit(1)

    print(f"🚀 Starting absorb-osp MCP server v{__version__}...")
    print("   Compatible with: Claude Code, Hermes Agent, any MCP client")
    print("   Tools:")
    print("     absorb_project  — Run 12-step absorption workflow")
    print("     list_projects   — List absorbed projects")
    print("     get_project_status — Project details")
    print("     check_privacy   — Privacy leak scan")
    print("     validate_report — Validate analysis report")
    print("     system_status   — System health and info")
    server.run()
