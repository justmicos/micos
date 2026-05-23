#!/usr/bin/env bash
#
# absorb-osp — Installer for Unix/macOS
#
# Usage:
#   ./install.sh                     # Install for Claude Code (default: ~/.claude)
#   ./install.sh --prefix=~/.claude  # Custom Claude Code directory
#   ./install.sh --hermes            # Also install for Hermes Agent
#
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/SATPROTOCOL/micos"

# Detect target directory
TARGET_DIR="${CLAUDE_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME}/.claude}"

INSTALL_HERMES=false
for arg in "$@"; do
  case "$arg" in
    --prefix=*) TARGET_DIR="${arg#*=}" ;;
    --hermes) INSTALL_HERMES=true ;;
    --help|-h)
      echo "Usage: $0 [--prefix=DIR] [--hermes]"
      echo "  --prefix=DIR   Install to DIR (default: ~/.claude)"
      echo "  --hermes       Also install Hermes Agent config"
      echo "  --help         Show this help"
      exit 0
      ;;
  esac
done

# ── Colors ─────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Backup Function ────────────────────────────────────────────────

backup_file() {
  local file="$1"
  if [ -f "$file" ]; then
    local backup="${file}.$(date +%Y%m%d-%H%M%S).bak"
    cp "$file" "$backup"
    warn "Backed up existing: $file → $backup"
  fi
}

# ── Install for Claude Code ────────────────────────────────────────

install_claude() {
  local src="$SCRIPT_DIR/claude"
  local dst="$TARGET_DIR"

  info "Installing absorb-osp for Claude Code..."
  info "  Source: $src"
  info "  Target: $dst"
  info ""

  # Create directories
  mkdir -p "$dst/skills/absorb-osp"
  mkdir -p "$dst/rules"
  mkdir -p "$dst/absorbed"

  # Copy with backup
  local files_copied=0
  local files_skipped=0

  # Skill definition
  if [ -f "$src/SKILL.md" ]; then
    backup_file "$dst/skills/absorb-osp/SKILL.md"
    cp "$src/SKILL.md" "$dst/skills/absorb-osp/SKILL.md"
    ok "Installed → $dst/skills/absorb-osp/SKILL.md"
    files_copied=$((files_copied + 1))
  fi

  # Workflow spec
  if [ -f "$src/WORKFLOW_SPEC.md" ]; then
    backup_file "$dst/skills/absorb-osp/WORKFLOW_SPEC.md"
    cp "$src/WORKFLOW_SPEC.md" "$dst/skills/absorb-osp/WORKFLOW_SPEC.md"
    ok "Installed → $dst/skills/absorb-osp/WORKFLOW_SPEC.md"
    files_copied=$((files_copied + 1))
  fi

  # Enforcement rules
  if [ -f "$src/rules/absorb-workflow.md" ]; then
    backup_file "$dst/rules/absorb-workflow.md"
    cp "$src/rules/absorb-workflow.md" "$dst/rules/absorb-workflow.md"
    ok "Installed → $dst/rules/absorb-workflow.md"
    files_copied=$((files_copied + 1))
  fi

  # Templates
  local template_src="$SCRIPT_DIR/templates"
  if [ -d "$template_src" ]; then
    for tmpl in "$template_src"/*.md; do
      local tmpl_name="TEMPLATE_$(basename "$tmpl")"
      local tmpl_dest="$dst/absorbed/$tmpl_name"
      if [ ! -f "$tmpl_dest" ]; then
        cp "$tmpl" "$tmpl_dest"
        ok "Installed template → $tmpl_dest"
        files_copied=$((files_copied + 1))
      else
        files_skipped=$((files_skipped + 1))
      fi
    done
  fi

  # Shared indexes (don't overwrite existing)
  local shared_src="$SCRIPT_DIR/shared"
  if [ -d "$shared_src" ]; then
    for f in "$shared_src"/*.md; do
      local dest="$dst/absorbed/$(basename "$f")"
      if [ ! -f "$dest" ]; then
        cp "$f" "$dest"
        ok "Created index → $dest"
        files_copied=$((files_copied + 1))
      else
        files_skipped=$((files_skipped + 1))
      fi
    done
  fi

  echo ""
  info "Claude Code install summary: $files_copied new/updated, $files_skipped skipped (already exist)"
}

# ── Install for Hermes Agent ───────────────────────────────────────

install_hermes() {
  local src="$SCRIPT_DIR/hermes"
  local hermes_config="${HERMES_CONFIG_DIR:-$HOME/.hermes/config}"

  if [ ! -d "$hermes_config" ]; then
    warn "Hermes config directory not found at $hermes_config"
    warn "Creating directory..."
    mkdir -p "$hermes_config"
  fi

  local files_copied=0

  if [ -f "$src/absorb-osp.yaml" ]; then
    backup_file "$hermes_config/absorb-osp.yaml"
    cp "$src/absorb-osp.yaml" "$hermes_config/absorb-osp.yaml"
    ok "Installed → $hermes_config/absorb-osp.yaml"
    files_copied=$((files_copied + 1))
  fi

  echo ""
  info "Hermes install summary: $files_copied file(s) installed"
}

# ── Main ───────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     absorb-osp  Installation             ║"
echo "║     v2.0.0                               ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Validate source
if [ ! -d "$SCRIPT_DIR/claude" ]; then
  error "Cannot find 'claude/' directory in $SCRIPT_DIR"
  error "Run this script from within the cloned repository."
  echo ""
  info "Correct usage:"
  info "  git clone $REPO_URL"
  info "  cd micos/absorb-osp && ./install.sh"
  exit 1
fi

install_claude

if [ "$INSTALL_HERMES" = true ]; then
  install_hermes
fi

# Install pre-push hook
if [ -d "$SCRIPT_DIR/.git/hooks" ] || [ -d "$(dirname "$SCRIPT_DIR")/.git/hooks" ]; then
  local_git_dir="$SCRIPT_DIR/.git"
  [ ! -d "$local_git_dir" ] && local_git_dir="$(dirname "$SCRIPT_DIR")/.git"
  if [ -d "$local_git_dir/hooks" ]; then
    cp "$SCRIPT_DIR/../scripts/pre-push.sh" "$local_git_dir/hooks/pre-push" 2>/dev/null && \
    chmod +x "$local_git_dir/hooks/pre-push" && \
    ok "Installed pre-push privacy hook" || true
  fi
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Installation Complete!                   ║"
echo "║                                           ║"
echo "║  Next steps:                              ║"
echo "║  1. Restart your agent session            ║"
echo "║  2. Send a GitHub URL to test:            ║"
echo '║     "Absorb https://github.com/..."       ║'
echo "║                                           ║"
echo "║  Docs: $REPO_URL           ║"
echo "╚══════════════════════════════════════════╝"
echo ""
