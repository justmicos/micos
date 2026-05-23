#!/usr/bin/env python3
"""
absorb-osp — Privacy Leak Scanner

Scans files for potential privacy leaks before publication.
Blocks commits that contain local paths, usernames, emails, or secrets.

Usage:
    python scripts/privacy-check.py <path>
    python scripts/privacy-check.py absorb-osp/
    python scripts/privacy-check.py . --verbose
"""

import os
import re
import sys
import argparse

# ── Privacy leak patterns (BLOCK if matched) ───────────────────────

BLOCK_PATTERNS = [
    # Local filesystem paths
    (r'[A-Za-z]:\\[Uu]sers\\[^\\]+\\', "Local Windows user path (C:\\Users\\<user>\\)"),
    (r'/home/[^/]+/', "Local Linux home path (/home/<user>/)"),
    (r'/Users/[^/]+/', "Local macOS user path (/Users/<user>/)"),

    # Private SSH keys
    (r'-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----', "Private key detected"),

    # API keys and tokens
    (r'sk-[a-zA-Z0-9]{20,}', "Potential API key (sk-*)"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth token"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key"),
    (r'rk_live_[a-zA-Z0-9]{24,}', "Stripe live key"),
    (r'sk_live_[a-zA-Z0-9]{24,}', "Stripe secret key"),

    # Database URLs with credentials
    (r'mongodb(\+srv)?://[^:]+:[^@]+@', "MongoDB URL with credentials"),
    (r'postgres(ql)?://[^:]+:[^@]+@', "PostgreSQL URL with credentials"),
    (r'mysql://[^:]+:[^@]+@', "MySQL URL with credentials"),

    # IP addresses (private/internal)
    (r'(10\.\d{1,3}\.\d{1,3}\.\d{1,3})', "Private IP address (10.x.x.x)"),
    (r'(172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})', "Private IP address (172.16-31.x.x)"),
    (r'(192\.168\.\d{1,3}\.\d{1,3})', "Private IP address (192.168.x.x)"),

    # Email addresses
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email address"),
]

# ── ALLOWLIST: patterns that are EXEMPT from blocking ──────────────

ALLOWLIST = [
    # Placeholder emails in documentation
    r'noreply@anthropic\.com',
    r'user@example\.com',
    r'example\.com',

    # Public documentation IPs
    r'localhost',
    r'127\.0\.0\.1',
    r'0\.0\.0\.0',

    # GitHub badges and URLs
    r'img\.shields\.io',
    r'github\.com/justmicos',
    r'github\.com/HermesAgent',
    r'claude\.ai',
    r'raw\.githubusercontent\.com',

    # Code examples using placeholder IPs
    r'http://localhost:\$',
    r'http://localhost:',

    # Common false positives
    r'10\.0\.0\.\d+',  # Documentation examples
    r'192\.168\.\d+\.\d+',  # Documentation examples

    # Scanner pattern definitions (false positives)
    r'/home/',
    r'/Users/',
    r'mysql://',
    r'PRIVACY_PATTERNS',
    r'PRIVACY_ALLOWLIST',
    r'BLOCK_PATTERNS',
    r'ALLOWLIST',
]

def load_allowlist():
    """Compile allowlist regex patterns."""
    return [re.compile(p) for p in ALLOWLIST]

def is_allowed(line, allowlist):
    """Check if a line is exempt from blocking."""
    for pattern in allowlist:
        if pattern.search(line):
            return True
    return False

def scan_file(filepath, allowlist, verbose=False):
    """Scan a single file for privacy leaks."""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                if is_allowed(line, allowlist):
                    continue
                for pattern, description in BLOCK_PATTERNS:
                    if re.search(pattern, line):
                        findings.append({
                            "line": lineno,
                            "pattern": description,
                            "content": line.strip()[:120],  # Truncate for display
                        })
    except Exception as e:
        findings.append({
            "line": 0,
            "pattern": "IO_ERROR",
            "content": str(e),
        })

    return findings

def should_skip(filepath):
    """Skip binary files, git internals, and other non-text files."""
    skip_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']
    for d in skip_dirs:
        if f'/{d}/' in filepath or filepath.startswith(f'{d}/'):
            return True

    skip_ext = ['.pyc', '.exe', '.dll', '.so', '.bin', '.png', '.jpg', '.gif', '.ico', '.zip', '.tar.gz']
    for ext in skip_ext:
        if filepath.endswith(ext):
            return True

    return False

def main():
    parser = argparse.ArgumentParser(description="absorb-osp Privacy Leak Scanner")
    parser.add_argument("path", nargs="?", default=".", help="File or directory to scan")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    allowlist = load_allowlist()
    all_findings = {}
    files_scanned = 0
    files_with_issues = 0

    path = args.path
    if os.path.isfile(path):
        files_to_check = [path]
    elif os.path.isdir(path):
        files_to_check = []
        for root, dirs, files in os.walk(path):
            # Skip common non-text directories
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build')]
            for f in files:
                full_path = os.path.join(root, f)
                if not should_skip(full_path):
                    files_to_check.append(full_path)
    else:
        print(f"❌ Invalid path: {path}")
        sys.exit(1)

    for filepath in sorted(files_to_check):
        findings = scan_file(filepath, allowlist, args.verbose)
        files_scanned += 1
        if findings:
            files_with_issues += 1
            all_findings[filepath] = findings
            if args.verbose:
                for f in findings:
                    print(f"  ⚠️  Line {f['line']}: {f['pattern']}")
                    print(f"      {f['content']}")

    # Output
    if args.json:
        print(json.dumps({
            "files_scanned": files_scanned,
            "files_with_issues": files_with_issues,
            "findings": {k: v for k, v in all_findings.items()},
        }, indent=2))
        sys.exit(0 if files_with_issues == 0 else 1)

    print(f"\n{'='*60}")
    print(f"  absorb-osp Privacy Leak Scan Report")
    print(f"{'='*60}")
    print(f"  Files scanned:    {files_scanned}")
    print(f"  Files with leaks: {files_with_issues}")

    if not all_findings:
        print(f"\n  ✅ PASS — No privacy leaks detected.")
        print(f"{'='*60}\n")
        sys.exit(0)

    print(f"\n  ❌ FAIL — Privacy leaks detected:")
    print(f"  ─────────────────────────────────────────────")
    for filepath, findings in sorted(all_findings.items()):
        rel_path = os.path.relpath(filepath, path) if os.path.isdir(path) else filepath
        print(f"\n  📄 {rel_path}:")
        for f in findings:
            print(f"     ⚠️  Line {f['line']:>5}: {f['pattern']}")
            print(f"                {f['content']}")

    print(f"\n{'='*60}")
    print(f"  ❌ BLOCKED: {files_with_issues} file(s) with privacy leaks.")
    print(f"  Fix issues above before committing to public repository.")
    print(f"{'='*60}\n")
    sys.exit(1)

if __name__ == "__main__":
    main()
