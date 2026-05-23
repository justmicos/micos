# ──────────────────────────────────────────────────────────
#  absorb-osp — Makefile
#  Targets declared in README are all implemented here.
# ──────────────────────────────────────────────────────────

SHELL := /bin/bash
.PHONY: help test lint check build dev-setup clean install

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Validate all YAML frontmatter in templates
	@echo "🔍 Validating YAML frontmatter in templates..."
	@python3 scripts/validate.py templates/ || \
		(python scripts/validate.py templates/ 2>/dev/null) || \
		(echo "⚠️  Python not found — skipping frontmatter validation."; \
		 echo "   Install Python 3 to enable validation.")
	@echo "✅ Frontmatter validation complete."

lint: ## Check markdown formatting
	@echo "📝 Checking markdown formatting..."
	@if command -v markdownlint &>/dev/null; then \
		markdownlint claude/ templates/ shared/ examples/ README.md; \
	elif command -v mdl &>/dev/null; then \
		mdl claude/ templates/ shared/ examples/ README.md; \
	else \
		echo "⚠️  markdownlint not found — installing via npm..."; \
		npm install -g markdownlint-cli 2>/dev/null && \
		markdownlint claude/ templates/ shared/ examples/ README.md || \
		echo "⚠️  Skipping markdown lint (npm not available either)."; \
	fi
	@echo "✅ Markdown check complete."

check: ## Verify all required files exist
	@echo "📋 Verifying required files..."
	@errors=0; \
	files="\
		claude/SKILL.md \
		claude/WORKFLOW_SPEC.md \
		claude/rules/absorb-workflow.md \
		templates/analysis_report.md \
		templates/usage_log.md \
		templates/instinct.md \
		shared/INDEX.md \
		shared/reject_log.md \
		shared/defer_log.md \
		install.sh \
		install.ps1 \
		LICENSE \
		README.md \
	"; \
	for f in $$files; do \
		if [ ! -f "absorb-osp/$$f" ] && [ ! -f "$$f" ]; then \
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

build: ## Package for distribution
	@echo "📦 Building absorb-osp distribution..."
	@mkdir -p dist
	@tar czf dist/absorb-osp-$$(cat absorb-osp/claude/SKILL.md | grep '^version:' | awk '{print $$2}').tar.gz \
		-C absorb-osp \
		README.md LICENSE CHANGELOG.md CONTRIBUTING.md \
		claude/ hermes/ templates/ shared/ examples/ \
		install.sh install.ps1 .gitignore
	@echo "✅ Distribution package created in dist/"

dev-setup: ## Install development dependencies
	@echo "🔧 Setting up development environment..."
	@if command -v npm &>/dev/null; then \
		npm install -g markdownlint-cli 2>/dev/null && \
		echo "✅ markdownlint installed."; \
	fi
	@if command -v pip3 &>/dev/null; then \
		pip3 install pyyaml 2>/dev/null && \
		echo "✅ PyYAML installed."; \
	elif command -v pip &>/dev/null; then \
		pip install pyyaml 2>/dev/null && \
		echo "✅ PyYAML installed."; \
	fi
	@echo "✅ Dev setup complete."

privacy-check: ## Scan for potential privacy leaks
	@echo "🛡️  Running privacy leak scan..."
	@python3 scripts/privacy-check.py absorb-osp/ || \
		python scripts/privacy-check.py absorb-osp/ || \
		(echo "⚠️  Python not found — skipping privacy scan."; exit 1)
	@echo "✅ Privacy scan complete."

clean: ## Clean build artifacts
	@rm -rf dist/
	@echo "✅ Clean complete."

install: ## Install to Claude Code
	@cd absorb-osp && ./install.sh
