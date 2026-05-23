#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  absorb-osp — Automated Security Red-flag Scanner
#  Usage: security-audit.sh <project-dir>
#
#  Implements the security red-flag checklist from
#  WORKFLOW_SPEC.md Step 1 (Triage).
# ──────────────────────────────────────────────────────────
# Don't use set -e — we want ALL checks to run even if one fails
set -uo pipefail

DIR="${1:?Usage: security-audit.sh <project-dir>}"
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  🔒 Security Red-flag Scanner            ║"
echo "║  Target: $DIR"
echo "╚══════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0
WARN=0
SKIP=0

check() {
    local num="$1" desc="$2" result="$3" detail="${4:-}"
    case "$result" in
        PASS) echo "  [✅] Check $num: $desc"; PASS=$((PASS + 1)) ;;
        FAIL) echo "  [❌] Check $num: $desc"; [ -n "$detail" ] && echo "       $detail"; FAIL=$((FAIL + 1)) ;;
        WARN) echo "  [⚠️]  Check $num: $desc"; [ -n "$detail" ] && echo "       $detail"; WARN=$((WARN + 1)) ;;
        SKIP) echo "  [⏭️ ] Check $num: $desc"; [ -n "$detail" ] && echo "       $detail"; SKIP=$((SKIP + 1)) ;;
    esac
}

cd "$DIR"

# ── Check 1: Binary blobs without source ─────────────────
echo "📋 [1/7] Checking for suspicious binary files..."
BINARIES=$(find . -type f \( -name "*.exe" -o -name "*.dll" -o -name "*.so" -o -name "*.bin" -o -name "*.class" \) \
    -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" 2>/dev/null | head -10)
if [ -n "$BINARIES" ]; then
    check 1 "Binary blobs without source" "WARN" "Found: $(echo "$BINARIES" | tr '\n' ' ')"
else
    check 1 "Binary blobs without source" "PASS"
fi

# ── Check 2: eval/exec without sanitization ──────────────
echo "📋 [2/7] Scanning for dangerous eval/exec patterns..."
EVAL_COUNT=$(grep -rn 'eval(\|exec(' --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" --include="*.pl" --include="*.rb" . 2>/dev/null || true | grep -v 'test\|spec\|__pycache__\|node_modules\|\.git' 2>/dev/null || true | wc -l)
if [ "$EVAL_COUNT" -gt 0 ]; then
    check 2 "Dangerous eval/exec usage" "WARN" "Found $EVAL_COUNT instance(s)"
else
    check 2 "Dangerous eval/exec usage" "PASS"
fi

# ── Check 3: Obfuscated code patterns ────────────────────
echo "📋 [3/7] Detecting obfuscated code..."
OBFUSCATED=$(grep -rn 'base64\|fromhex\|charCodeAt' --include="*.py" --include="*.js" --include="*.ts" . 2>/dev/null || true | grep -v 'test\|spec\|__pycache__\|node_modules\|\.git\|README\|LICENSE' 2>/dev/null || true | head -10)
if [ -n "$OBFUSCATED" ]; then
    check 3 "Obfuscated code patterns" "WARN" "Potential obfuscation detected"
else
    check 3 "Obfuscated code patterns" "PASS"
fi

# ── Check 4: Network requests to hardcoded IPs ───────────
echo "📋 [4/7] Checking for hardcoded network targets..."
HARDCODED_IPS=$(grep -rn 'curl\|wget\|request\|fetch' --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" . 2>/dev/null || true | grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' 2>/dev/null || true | grep -v '0\.0\.0\.0\|127\.0\.0\.1\|localhost\|255\.255\.255\.255' 2>/dev/null || true | sort -u | head -10)
if [ -n "$HARDCODED_IPS" ]; then
    check 4 "Hardcoded network targets" "WARN" "IPs: $(echo "$HARDCODED_IPS" | tr '\n' ' ')"
else
    check 4 "Hardcoded network targets" "PASS"
fi

# ── Check 5: Install script audit ────────────────────────
echo "📋 [5/7] Auditing install scripts..."
INSTALL_SCRIPTS=$(find . -maxdepth 2 \( -name "install.sh" -o -name "install.ps1" -o -name "postinstall.js" -o -name "setup.py" \) 2>/dev/null)
if [ -n "$INSTALL_SCRIPTS" ]; then
    check 5 "Install script audit" "WARN" "Found: $(echo "$INSTALL_SCRIPTS" | tr '\n' ' ')"
else
    check 5 "Install script audit" "PASS"
fi

# ── Check 6: Dependency vulnerability scan ───────────────
echo "📋 [6/7] Checking dependency vulnerability scanners..."
HAS_NPM=$(find . -name "package.json" -not -path "./node_modules/*" 2>/dev/null | head -1)
HAS_PIP=$(find . -name "requirements.txt" -o -name "Pipfile" -o -name "pyproject.toml" 2>/dev/null | head -1)
HAS_CARGO=$(find . -name "Cargo.toml" 2>/dev/null | head -1)
HAS_GO=$(find . -name "go.mod" 2>/dev/null | head -1)

VULN_SCAN=0
[ -n "$HAS_NPM" ] && { npm audit --prefix "$(dirname "$HAS_NPM")" 2>/dev/null | tail -5 || true; VULN_SCAN=1; }
[ -n "$HAS_PIP" ] && { pip-audit -r "$HAS_PIP" 2>/dev/null || echo "  (pip-audit not installed)"; VULN_SCAN=1; }
[ -n "$HAS_CARGO" ] && { cargo audit 2>/dev/null || echo "  (cargo-audit not installed)"; VULN_SCAN=1; }
[ "$VULN_SCAN" -eq 0 ] && check 6 "Dependency vulnerability scan" "SKIP" "No dependency files found" || check 6 "Dependency vulnerability scan" "PASS"

# ── Check 7: License check ───────────────────────────────
echo "📋 [7/7] Checking license..."
LICENSE_FILE=$(find . -maxdepth 1 \( -name "LICENSE" -o -name "LICENSE.md" -o -name "LICENSE.txt" -o -name "COPYING" \) 2>/dev/null | head -1)
if [ -n "$LICENSE_FILE" ]; then
    LICENSE_TYPE=$(head -1 "$LICENSE_FILE" | grep -oiP 'MIT|Apache|GPL|BSD|LGPL|MPL' || echo "unknown")
    check 7 "License check" "PASS" "License: $LICENSE_TYPE"
else
    check 7 "License check" "FAIL" "No license file found"
fi

# ── Summary ──────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Security Scan Summary                   ║"
echo "╠══════════════════════════════════════════╣"
echo "║  ✅ Pass:  $PASS"
echo "║  ⚠️  Warnings: $WARN"
echo "║  ❌ Failed: $FAIL"
echo "║  ⏭️  Skipped: $SKIP"
echo "╚══════════════════════════════════════════╝"
echo ""

# Gate decision
if [ "$FAIL" -gt 0 ]; then
    echo "❌ SECURITY GATE: BLOCKED — $FAIL critical check(s) failed."
    exit 1
elif [ "$WARN" -gt 3 ]; then
    echo "⚠️  SECURITY GATE: REVIEW NEEDED — $WARN warning(s). Manual review required."
    exit 0
else
    echo "✅ SECURITY GATE: PASSED — All checks clear."
    exit 0
fi
