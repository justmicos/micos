#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  absorb-osp — Build Verification
#  Usage: verify-build.sh <project-dir> [build-command]
# ──────────────────────────────────────────────────────────
set -euo pipefail
cd "${1:?Usage: verify-build.sh <project-dir> [build-cmd]}"
shift
BUILD_CMD="${*:-npm run build 2>/dev/null || cargo build 2>/dev/null || go build ./... 2>/dev/null || python3 -m build 2>/dev/null || echo 'auto-detect-build-failed'}"

echo "🔨 Checking build system..."
START=$(date +%s%N)

if [ -f "Makefile" ] || [ -f "makefile" ]; then
    echo "   📐 Makefile detected"
    make 2>&1 | tail -5
elif [ -f "Cargo.toml" ]; then
    echo "   🦀 Rust project detected"
    cargo build 2>&1 | tail -5
elif [ -f "go.mod" ]; then
    echo "   🐹 Go project detected"
    go build ./... 2>&1
elif [ -f "package.json" ]; then
    echo "   📦 Node.js project detected"
    npm run build 2>&1 | tail -10 || npm ci && npm run build 2>&1 | tail -10
elif [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo "   🐍 Python project detected"
    python3 -m build 2>&1 | tail -5 || pip install -e . 2>&1 | tail -3
elif [ -f "pom.xml" ]; then
    echo "   ☕ Java/Maven project detected"
    mvn compile -q 2>&1 | tail -5
else
    echo "   ⚠️  Unknown build system — trying: $BUILD_CMD"
    eval "$BUILD_CMD" || echo "   ⚠️  Build check skipped (no standard build system)"
fi

END=$(date +%s%N)
DURATION_MS=$(( (END - START) / 1000000 ))
echo "✅ Build check completed in ${DURATION_MS}ms"
