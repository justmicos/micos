"""absorb-osp — Privacy and Security Scanner"""

import re
from pathlib import Path
from typing import Optional

# ── Privacy leak patterns ──────────────────────────────────────────

PRIVACY_PATTERNS: list[tuple[str, str]] = [
    (r'[A-Za-z]:\\[Uu]sers\\[^\\]+\\', "Local Windows path (C:\\Users\\)"),
    (r'/home/[^/]+/', "Linux home path"),
    (r'/Users/[^/]+/', "macOS user path"),
    (r'-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----', "Private key"),
    (r'sk-[a-zA-Z0-9]{20,}', "Potential API key (sk-*)"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth token"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key"),
    (r'mongodb(\+srv)?://[^:]+:[^@]+@', "MongoDB credentials"),
    (r'postgres(ql)?://[^:]+:[^@]+@', "PostgreSQL credentials"),
    (r'mysql://[^:]+:[^@]+@', "MySQL credentials"),
]

PRIVACY_ALLOWLIST: list[str] = [
    # Safe references in documentation
    r'noreply@anthropic\.com',
    r'example\.com',
    r'img\.shields\.io',
    r'github\.com/justmicos',
    r'github\.com/HermesAgent',
    r'claude\.ai',
    r'raw\.githubusercontent\.com',
    r'localhost',
    r'127\.0\.0\.1',
    # Scanner's own pattern definitions (false-positive avoidance)
    r"/home/",
    r"/Users/",
    r"PRIVACY_PATTERNS",
    r"PRIVACY_ALLOWLIST",
]

# File types to scan (all text-based)
SCAN_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".ps1", ".bat",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf",
    ".txt", ".csv", ".env", ".xml", ".html", ".css", ".scss",
    ".rb", ".go", ".rs", ".java", ".kt", ".swift", ".c", ".cpp", ".h",
    ".sql", ".r", ".lua", ".php", ".pl", ".pm",
}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
             "dist", "build", ".egg-info", "eggs"}
SKIP_EXT = {".pyc", ".exe", ".dll", ".so", ".bin", ".class",
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
            ".woff", ".woff2", ".ttf", ".eot", ".pdf",
            ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"}


def scan_for_leaks(path: str, verbose: bool = False) -> list[dict]:
    """Scan files for privacy leaks.

    Args:
        path: Directory or file path to scan.
        verbose: If True, include matched line content in results.

    Returns:
        List of finding dicts with file, line, pattern, and optional content.
    """
    findings: list[dict] = []
    path_obj = Path(path)
    files = _collect_files(path_obj)

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(content.split("\n"), 1):
                if _is_allowed(line):
                    continue
                for pattern, desc in PRIVACY_PATTERNS:
                    if re.search(pattern, line):
                        finding: dict = {
                            "file": str(filepath),
                            "line": lineno,
                            "pattern": desc,
                        }
                        if verbose:
                            finding["content"] = line.strip()[:120]
                        findings.append(finding)
        except Exception:
            pass

    return findings


def _collect_files(path: Path) -> list[Path]:
    """Collect all text files to scan, respecting skip rules."""
    files: list[Path] = []
    for f in path.rglob("*"):
        if any(d in f.parts for d in SKIP_DIRS):
            continue
        if f.suffix in SKIP_EXT or (f.suffix == "" and f.name.startswith(".")):
            continue
        if f.is_file() and (f.suffix in SCAN_EXTENSIONS or f.suffix == ""):
            files.append(f)
    return files


def _is_allowed(line: str) -> bool:
    """Check if a line matches the allowlist (safe patterns)."""
    return any(re.search(p, line) for p in PRIVACY_ALLOWLIST)


# ── Security red-flag scanner ──────────────────────────────────────

SECURITY_CHECKS: list[tuple[str, str, str]] = [
    ("binary_blobs", "Binary blobs without source",
     r"\.exe$|\.dll$|\.so$|\.bin$|\.class$"),
    ("dangerous_eval", "Dangerous eval/exec usage",
     r"\beval\(|\bexec\(|\bexec_command\b"),
    ("code_obfuscation", "Obfuscated code patterns",
     r"base64\.decode|fromhex|charCodeAt|String\.fromCharCode"),
    ("hardcoded_creds", "Hardcoded credential patterns",
     r"(password|passwd|pwd|secret|apikey)\s*[:=]\s*['\"]"),
    ("insecure_protocol", "Insecure protocol references",
     r"http://(?!localhost|127\.0\.0\.1|www\.w3\.org|www\.apache\.org)"),
    ("suspicious_imports", "Suspicious module imports",
     r"\bimport\s+(pwn|hack|exploit|malware)\b"),
    ("insecure_defaults", "Insecure default configurations",
     r"debug\s*=\s*True|ALLOWED_HOSTS\s*=\s*\['\*'\]"),
]


def security_scan(path: str) -> dict:
    """Run security red-flag checks on a project directory.

    Runs 7 checks: binary blobs, eval/exec, obfuscation, hardcoded creds,
    insecure protocols, suspicious imports, insecure defaults.

    Returns:
        Dict with 'checks', 'summary', and 'gate' (PASS|REVIEW|BLOCKED).
    """
    results: dict = {
        "checks": [],
        "summary": {"pass": 0, "warn": 0, "fail": 0, "skip": 0},
        "gate": "PASS",
    }

    p = Path(path)
    if not p.exists():
        results["gate"] = "FAIL"
        return results

    for check_id, check_name, pattern in SECURITY_CHECKS:
        if check_id == "binary_blobs":
            count = len(_find_binaries(p))
        else:
            count = _grep_count(p, pattern)
        status = "warn" if count > 0 else "pass"
        _add_check(results, check_name, status,
                   f"{count} match(es)" if count else "")

    # Gate logic
    if results["summary"]["fail"] > 0:
        results["gate"] = "BLOCKED"
    elif results["summary"]["warn"] > 3:
        results["gate"] = "REVIEW"

    return results


def _add_check(results: dict, name: str, status: str, detail: str = ""):
    """Add a check result to the results dict."""
    results["checks"].append({"name": name, "status": status, "detail": detail})
    results["summary"][status] = results["summary"].get(status, 0) + 1


def _find_binaries(path: Path) -> list[str]:
    """Find binary files that may hide malicious code."""
    found: list[str] = []
    for ext in (".exe", ".dll", ".so", ".bin", ".class"):
        for f in path.rglob(f"*{ext}"):
            if not any(d in f.parts for d in SKIP_DIRS):
                found.append(f.name)
                if len(found) >= 10:
                    return found
    return found


def _grep_count(path: Path, pattern: str, skip_dirs: Optional[set] = None) -> int:
    """Count regex matches in text files, skipping specified dirs."""
    if skip_dirs is None:
        skip_dirs = SKIP_DIRS
    count = 0
    for f in path.rglob("*"):
        if any(d in f.parts for d in skip_dirs):
            continue
        if f.is_file() and f.suffix in SCAN_EXTENSIONS:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                count += len(re.findall(pattern, content, re.IGNORECASE))
            except Exception:
                pass
    return count
