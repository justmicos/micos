"""absorb-osp — Project Analyzer (GitHub metadata, tech stack, URL parsing)"""

import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from .models import ProjectInfo

# ── GitHub URL parsing ──────────────────────────────────────────────

_GITHUB_URL_PATTERNS = [
    re.compile(r"github\.com/([^/]+)/([^/]+)"),
    re.compile(r"git@github\.com:([^/]+)/([^/]+)"),
]


def parse_github_url(url: str) -> tuple[str, str]:
    """Parse a GitHub URL into (owner, repo)."""
    url = url.strip().rstrip("/")
    for p in _GITHUB_URL_PATTERNS:
        m = p.search(url)
        if m:
            return m.group(1), m.group(2).replace(".git", "")
    raise ValueError(f"Invalid GitHub URL: {url}")


# ── GitHub API client (curl-based, no python package needed) ────────

_CURL_AVAILABLE: Optional[bool] = None
_API_CACHE: dict[str, Optional[dict]] = {}


def _curl_available() -> bool:
    """Check if curl is installed (cache result)."""
    global _CURL_AVAILABLE
    if _CURL_AVAILABLE is None:
        _CURL_AVAILABLE = shutil.which("curl") is not None
    return _CURL_AVAILABLE


def _fetch_json(url: str, timeout: int = 10) -> Optional[dict]:
    """Fetch JSON from a URL using curl with timeout and error handling."""
    if not _curl_available():
        return None
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 2,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data if isinstance(data, dict) and "id" in data else None
    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        return None


def analyze_github_url(url: str) -> ProjectInfo:
    """Analyze a GitHub URL to extract project metadata.

    Uses curl to fetch GitHub API data; returns basic URL-derived info
    if curl is unavailable or the API call fails.
    """
    owner, repo = parse_github_url(url)

    info = ProjectInfo(
        github_url=f"https://github.com/{owner}/{repo}",
        name=repo,
    )

    cache_key = f"{owner}/{repo}"
    if cache_key in _API_CACHE:
        api_data = _API_CACHE[cache_key]
    else:
        api_data = _fetch_github_api(owner, repo)
        _API_CACHE[cache_key] = api_data

    if api_data:
        info.stars = api_data.get("stargazers_count", 0)
        info.license_type = (api_data.get("license") or {}).get("spdx_id", "Unknown")
        info.description = api_data.get("description", "") or ""
        info.language = api_data.get("language", "") or ""
        info.last_commit = api_data.get("updated_at", "") or ""
        info.open_issues = api_data.get("open_issues_count", 0)
        info.contributors = _count_contributors(owner, repo)

    return info


def _fetch_github_api(owner: str, repo: str) -> Optional[dict]:
    """Fetch project data from GitHub API with retry."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    for attempt in range(2):
        data = _fetch_json(url, timeout=10)
        if data is not None:
            return data
        if attempt == 0:
            time.sleep(1)  # brief pause before retry
    return None


def _count_contributors(owner: str, repo: str) -> int:
    """Estimate contributor count via GitHub API Link header."""
    if not _curl_available():
        return 0
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true"
    try:
        result = subprocess.run(
            ["curl", "-s", "-I", "--max-time", "8", url],
            capture_output=True, text=True, timeout=10,
        )
        m = re.search(r'page=(\d+)>; rel="last"', result.stdout)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0


# ── Tech stack detection ────────────────────────────────────────────

def detect_tech_stack(path: str) -> dict:
    """Detect technology stack from a project directory."""
    tech: dict = {
        "language": None,
        "framework": None,
        "build_system": None,
        "dependencies": [],
        "has_docker": False,
        "has_ci": False,
    }

    p = Path(path)
    if not p.exists():
        return tech

    # Language detection (most-specific first)
    if (p / "Cargo.toml").exists():
        tech["language"] = "Rust"
        tech["build_system"] = "cargo"
    elif (p / "go.mod").exists():
        tech["language"] = "Go"
        tech["build_system"] = "go"
    elif (p / "package.json").exists():
        tech["language"] = "JavaScript/TypeScript"
        tech["build_system"] = "npm"
        tech["framework"] = _detect_js_framework(p)
    elif (p / "pyproject.toml").exists():
        tech["language"] = "Python"
        tech["build_system"] = "pip"
    elif (p / "setup.py").exists():
        tech["language"] = "Python"
        tech["build_system"] = "pip"
    elif (p / "pom.xml").exists():
        tech["language"] = "Java"
        tech["build_system"] = "maven"
    elif (p / "build.gradle").exists() or (p / "build.gradle.kts").exists():
        tech["language"] = "Java"
        tech["build_system"] = "gradle"
    elif (p / "Gemfile").exists():
        tech["language"] = "Ruby"
        tech["build_system"] = "bundler"
    elif (p / "Cargo.toml").exists():
        tech["language"] = "Rust"
        tech["build_system"] = "cargo"
    elif list(p.glob("*.swift")):
        tech["language"] = "Swift"
    elif list(p.glob("*.kt")) or list(p.glob("*.kts")):
        tech["language"] = "Kotlin"

    # Docker
    if (p / "Dockerfile").exists() or (p / "docker-compose.yml").exists():
        tech["has_docker"] = True

    # CI
    if (p / ".github" / "workflows").exists():
        tech["has_ci"] = True
    if (p / ".gitlab-ci.yml").exists():
        tech["has_ci"] = True
    if (p / "Jenkinsfile").exists():
        tech["has_ci"] = True

    return tech


def _detect_js_framework(path: Path) -> Optional[str]:
    """Detect JavaScript framework from package.json."""
    pkg_file = path / "package.json"
    if not pkg_file.exists():
        return None
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "next" in deps:
            return "Next.js"
        if "nuxt" in deps:
            return "Nuxt.js"
        if "react" in deps:
            return "React"
        if "vue" in deps:
            return "Vue"
        if "svelte" in deps or "sveltekit" in deps:
            return "Svelte"
        if "@angular/core" in deps:
            return "Angular"
        if "solid-js" in deps:
            return "Solid.js"
    except Exception:
        pass
    return None
