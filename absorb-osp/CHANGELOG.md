# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.1] - 2026-05-23

### Fixed
- models.py: WorkflowStep `start()`/`complete()` methods; WorkflowResult `_add()` helper
- analyzer.py: curl cached, API retry, expanded tech detection (Ruby, Kotlin, Swift, Angular, Nuxt.js), encoding-safe
- workflow.py: word-boundary dedup, real security_scan call, proper step lifecycle, INDEX.md separator skip
- reporter.py: removed dead imports, classify_decision not hardcoded, uses `classification` param
- scanner.py: `verbose` param used, 4→7 security checks, 50+ scan types, expanded skip dirs
- cli.py: removed unused imports, status works with project name, validate shows field count, scan has --verbose
- mcp_server.py: utf-8 encoding on all reads, dynamic version from __init__, try/except wrapping
- daemon.py: CORS headers, input validation, sorted watcher, descriptive errors
- privacy-check.py: false-positive allowlist entries for scanner patterns

### Changed
- __init__.py: exports WorkflowEngine, scan_for_leaks, security_scan
- All modules: consistent encoding="utf-8" on all file I/O

## [2.0.0] - 2026-05-23

### Added
- 12-step closed-loop flywheel (up from 8 steps)
- Step 1: Triage — 30-second security red-flag scan
- Step 5: Classify — Deduplication and merge decision against existing projects
- Step 10: Sync — Automatic index and memory system updates
- Step 12: Evolve — Quarterly consolidation and workflow self-improvement
- 5-dimension quantified scoring matrix (Judge step)
- 5-level absorption depth system (L1-L5)
- Security audit gates贯穿 all steps
- Template system with 3 standardized templates
- REJECTED.md and DEFERRED.md project logs
- Hermes Agent integration support
- Cross-platform installer scripts (bash + PowerShell)

### Changed
- SKILL.md restructured for framework-agnostic readability
- WORKFLOW_SPEC.md expanded from operational checklist to comprehensive spec

### Security
- Red-flag detection checklist in Triage step
- Supply chain vulnerability scanning in Evaluate step
- Security re-check in final Verify step

## [1.0.0] - 2026-05-15

### Added
- Initial 8-step absorption workflow
- Basic SKILL.md with trigger words
- Analysis report template
- Basic verify/evaluate/judge/internalize/load/verify/iterate flow
- Claude Code integration via `.claude/skills/`

[2.0.0]: https://github.com/justmicos/micos/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/justmicos/micos/releases/tag/v1.0.0
