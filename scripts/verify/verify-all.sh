#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  absorb-osp — Full Verification Suite
#  Runs all checks on an absorbed project.
#  Usage: verify-all.sh <project-dir> [health-url]
# ──────────────────────────────────────────────────────────
set -euo pipefail

DIR="${1:?Usage: verify-all.sh <project-dir> [health-url]}"
HEALTH_URL="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  absorb-osp  Full Verification Suite     ║"
echo "║  Target: $DIR"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. File integrity
echo "📋 [1/4] File integrity..."
if [ -d "$DIR" ]; then
    echo "   ✅ Project directory exists"
    PASS=$((PASS + 1))
else
    echo "   ❌ Project directory not found"
    FAIL=$((FAIL + 1))
fi

# 2. Build check
echo "📋 [2/4] Build verification..."
if "$SCRIPT_DIR/check-build.sh" "$DIR" 2>&1 | tail -1 | grep -q "completed"; then
    PASS=$((PASS + 1))
else
    FAIL=$((FAIL + 1))
fi

# 3. Health check (optional)
echo "📋 [3/4] Health check..."
if [ -n "$HEALTH_URL" ]; then
    if "$SCRIPT_DIR/check-health.sh" "$HEALTH_URL" 2>&1 | tail -1 | grep -q "PASSED"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
    fi
else
    echo "   ⏭️  Skipped (no health URL provided)"
fi

# 4. Resource check
echo "📋 [4/4] Resource check..."
if [ -n "$HEALTH_URL" ]; then
    PORT=$(echo "$HEALTH_URL" | grep -oP ':\K\d+' || echo "")
    if [ -n "$PORT" ]; then
        echo "   Checking port $PORT..."
        "$SCRIPT_DIR/check-resource.sh" "$PORT" 3 2>&1 | tail -1 | grep -q "complete" && PASS=$((PASS + 1)) || true
    else
        echo "   ⏭️  Skipped (no port in URL)"
    fi
else
    echo "   ⏭️  Skipped (no health URL provided)"
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Results:  ✅ $PASS passed  |  ❌ $FAIL failed"
echo "╚══════════════════════════════════════════╝"
[ $FAIL -eq 0 ] && exit 0 || exit 1
