---
name: absorb-osp
preamble-tier: 1
version: 2.0.0
description: |
  Systematic open-source project absorption closed-loop flywheel — security triage →
  deep evaluation → quantified judging → dedup classification → multi-depth
  internalization → load → integrate → verify → sync → iterate → evolve (12 steps).
  Triggers automatically on GitHub URLs.
triggers:
  - absorb open source
  - analyze open source project
  - open source project
  - evaluate this project
  - integrate
  - absorb
  - open source
  - github.com
  - load project
  - internalize
  - absorb-osp
  - assess project
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
  - AskUserQuestion
  - Agent
  - Glob
  - Grep
  - Skill
---

# absorb-osp v2.0.0 — Open Source Project Absorption Workflow

## 📖 Workflow Specification

**The complete 12-step specification is in `WORKFLOW_SPEC.md` (same directory).**
**You MUST read it before executing.** This file is a quick reference only.

---

## ⚡ Pre-Execution Checklist

Before starting, confirm:

1. **Read WORKFLOW_SPEC.md?** — If not, READ IT FIRST. The 12-step process is mandatory.
2. **Is a GitHub URL provided?** — If not, ask the user.
3. **Checked existing absorbed projects?** — See `shared/INDEX.md` to avoid duplicates.
4. **Templates available?** — Located in `templates/` directory.

---

## 🔍 Quick Reference

### Steps (in brief — see WORKFLOW_SPEC.md for full detail)

```
Trigger → Triage → Verify → Evaluate → Judge → Classify
→ Internalize → Load → Integrate → Verify → Sync → Iterate → Evolve
```

### Rejection Criteria (any one = stop)

| # | Criterion |
|---|-----------|
| 1 | Malicious code (cryptominer, backdoor, data exfiltration) |
| 2 | Critical unpatched vulnerabilities (RCE, SQLi, auth bypass) |
| 3 | Incompatible license (GPL/AGPL where unavoidable) |
| 4 | Hidden installer behavior (undeclared network calls, file ops) |
| 5 | Supply chain risk (known malicious dependencies) |
| 6 | Excessive permissions (beyond functional requirements) |

### Absorption Depths

| Level | Type | Artifacts |
|-------|------|-----------|
| L1 | Knowledge | Analysis report + instinct |
| L2 | Tool | L1 + invocable skill |
| L3 | Service | L2 + startup scripts + proxy route |
| L4 | Plugin | L1 + MCP server config |
| L5 | Deep | L3+L4 + code-level integration + orchestration |

---

## 📎 References

| Document | Path | Purpose |
|----------|------|---------|
| Workflow spec | `./WORKFLOW_SPEC.md` | **Read this first** |
| Enforcement rules | `./rules/absorb-workflow.md` | Mandatory rules |
| Project index | `../shared/INDEX.md` | Absorbed projects |
| Analysis template | `../templates/analysis_report.md` | Report format |
