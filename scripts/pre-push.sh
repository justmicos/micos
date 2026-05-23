#!/usr/bin/env bash
#
# absorb-osp — Git Pre-Push Hook
#
# Blocks pushes that contain privacy leaks or broken files.
# Install: ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  🔒 Pre-Push Privacy & Integrity Check   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Privacy check
echo "📋 Step 1/3: Scanning for privacy leaks..."
if command -v python3 &>/dev/null; then
    python3 "$REPO_ROOT/scripts/privacy-check.py" "$REPO_ROOT/absorb-osp/" || exit 1
elif command -v python &>/dev/null; then
    python "$REPO_ROOT/scripts/privacy-check.py" "$REPO_ROOT/absorb-osp/" || exit 1
else
    echo "⚠️  Python not found — skipping privacy scan. Install Python 3 to enable."
fi

# 2. File integrity check
echo ""
echo "📋 Step 2/3: Verifying file integrity..."
errors=0
while IFS= read -r f; do
    if [ ! -f "$REPO_ROOT/$f" ]; then
        echo "❌ MISSING: $f"
        errors=$((errors + 1))
    fi
done < <(cat <<'FILES'
absorb-osp/claude/SKILL.md
absorb-osp/claude/WORKFLOW_SPEC.md
absorb-osp/claude/rules/absorb-workflow.md
absorb-osp/templates/analysis_report.md
absorb-osp/templates/usage_log.md
absorb-osp/templates/instinct.md
absorb-osp/shared/INDEX.md
absorb-osp/shared/reject_log.md
absorb-osp/shared/defer_log.md
absorb-osp/install.sh
absorb-osp/install.ps1
absorb-osp/LICENSE
absorb-osp/README.md
FILES
)
if [ "$errors" -gt 0 ]; then
    echo "❌ $errors file(s) missing — push blocked."
    exit 1
fi
echo "✅ All required files present."

# 3. Bash syntax check
echo ""
echo "📋 Step 3/3: Checking script syntax..."
bash -n "$REPO_ROOT/absorb-osp/install.sh" && echo "✅ install.sh syntax OK"

echo ""
echo "✅ All checks passed — push allowed."
echo ""
