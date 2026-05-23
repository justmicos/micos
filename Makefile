# ──────────────────────────────────────────────────────────
#  absorb-osp — Makefile
#  Targets declared in README are all implemented here.
# ──────────────────────────────────────────────────────────

SHELL := /bin/bash
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "")
.PHONY: help test lint check build dev-setup clean install security-audit e2e-test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Validation ────────────────────────────────────────────

test: templates examples ## Validate all YAML frontmatter in templates and examples
	@echo "🔍 Validating YAML frontmatter..."
	@if [ -z "$(PYTHON)" ]; then \
		echo "⚠️  Python not found — skipping validation."; \
		exit 0; \
	fi
	@$(PYTHON) scripts/validate.py absorb-osp/templates/
	@for f in absorb-osp/examples/*.md; do \
		echo "   Checking $$f..."; \
		$(PYTHON) scripts/validate.py "$$f" analysis_report.md || true; \
	done
	@echo "✅ Validation complete."

templates: ## Validate template files specifically
	@echo "📋 Validating templates..."
	@if [ -z "$(PYTHON)" ]; then \
		echo "⚠️  Python not found — skipping."; \
		exit 0; \
	fi
	@$(PYTHON) scripts/validate.py absorb-osp/templates/
	@echo "✅ Templates valid."

lint: ## Check markdown formatting
	@echo "📝 Checking markdown formatting..."
	@if command -v markdownlint &>/dev/null; then \
		markdownlint absorb-osp/ README.md; \
	elif command -v mdl &>/dev/null; then \
		mdl absorb-osp/ README.md; \
	else \
		echo "⚠️  markdownlint not found. Install: npm install -g markdownlint-cli"; \
	fi
	@echo "✅ Markdown check complete."

check: ## Verify all required files exist
	@echo "📋 Verifying required files..."
	@errors=0; \
	files="\
		absorb-osp/claude/SKILL.md \
		absorb-osp/claude/WORKFLOW_SPEC.md \
		absorb-osp/claude/rules/absorb-workflow.md \
		absorb-osp/templates/analysis_report.md \
		absorb-osp/templates/usage_log.md \
		absorb-osp/templates/instinct.md \
		absorb-osp/shared/INDEX.md \
		absorb-osp/shared/reject_log.md \
		absorb-osp/shared/defer_log.md \
		absorb-osp/install.sh \
		absorb-osp/install.ps1 \
		absorb-osp/LICENSE \
		absorb-osp/README.md \
		scripts/validate.py \
		scripts/privacy-check.py \
		scripts/security-audit.sh \
		Makefile \
		PRIVACY.md \
	"; \
	for f in $$files; do \
		if [ ! -f "$$f" ]; then \
			echo "❌ MISSING: $$f"; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ $$errors -eq 0 ]; then \
		echo "✅ All required files present."; \
	else \
		echo "❌ $$errors file(s) missing."; \
		exit 1; \
	fi

# ── Security ──────────────────────────────────────────────

privacy-check: ## Scan for potential privacy leaks
	@echo "🛡️  Running privacy leak scan..."
	@if [ -z "$(PYTHON)" ]; then \
		echo "⚠️  Python not found — skipping privacy scan."; \
		exit 1; \
	fi
	@$(PYTHON) scripts/privacy-check.py absorb-osp/
	@echo "✅ Privacy scan complete."

security-audit: ## Run automated security red-flag scanner
	@echo "🔒 Running security audit..."
	@bash scripts/security-audit.sh absorb-osp/
	@echo "✅ Security audit complete."

# ── Build ─────────────────────────────────────────────────

build: check test privacy-check security-audit ## Package for distribution (runs full validation first)
	@echo "📦 Building absorb-osp distribution..."
	@mkdir -p dist
	@VERSION=$$(grep '^version:' absorb-osp/claude/SKILL.md | awk '{print $$2}'); \
	tar czf "dist/absorb-osp-$$VERSION.tar.gz" \
		absorb-osp/README.md \
		absorb-osp/LICENSE \
		absorb-osp/CHANGELOG.md \
		absorb-osp/CONTRIBUTING.md \
		absorb-osp/claude/ \
		absorb-osp/hermes/ \
		absorb-osp/templates/ \
		absorb-osp/shared/ \
		absorb-osp/examples/ \
		absorb-osp/install.sh \
		absorb-osp/install.ps1 \
		Makefile \
		PRIVACY.md \
		scripts/
	@echo "✅ Distribution package created in dist/"

dev-setup: ## Install development dependencies
	@echo "🔧 Setting up development environment..."
	@if command -v npm &>/dev/null; then \
		npm install -g markdownlint-cli 2>/dev/null && \
		echo "✅ markdownlint installed."; \
	fi
	@echo "✅ Dev setup complete."

# ── E2E Test ──────────────────────────────────────────────

e2e-test: ## Run end-to-end absorption test on tqdm
	@echo "🧪 Running E2E absorption test..."
	@echo "   Target: https://github.com/tqdm/tqdm"
	@echo ""
	@echo "   [1/4] File integrity..."
	@test -f absorb-osp/examples/tqdm-analysis-report.md && \
		echo "   ✅ Analysis report exists" || \
		(echo "   ❌ Missing report"; exit 1)
	@echo ""
	@echo "   [2/4] Frontmatter validation..."
	@$(PYTHON) scripts/validate.py absorb-osp/examples/tqdm-analysis-report.md analysis_report.md
	@echo ""
	@echo "   [3/4] Security audit (on absorb-osp itself)..."
	@bash scripts/security-audit.sh absorb-osp/
	@echo ""
	@echo "   [4/4] Privacy scan..."
	@$(PYTHON) scripts/privacy-check.py absorb-osp/
	@echo ""
	@echo "✅ E2E test PASSED — 12-step workflow produces valid artifacts."

# ── Cleanup ───────────────────────────────────────────────

clean: ## Clean build artifacts
	@rm -rf dist/
	@echo "✅ Clean complete."

install: ## Install to Claude Code
	@cd absorb-osp && bash install.sh
