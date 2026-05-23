# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
