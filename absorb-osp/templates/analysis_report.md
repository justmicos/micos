---
absorb_date: YYYY-MM-DD
github_url: https://github.com/owner/repo
license: MIT
stars: 1500
depth: L3
status: built
judge_score: 3.5
classify_decision: STANDALONE
integration_targets:
  - agent-skills
  - mcp
  - proxy
  - workflow-engine
---

# <project-name> — Deep Analysis Report

## 0. Triage Record

| Check | Result | Notes |
|-------|--------|-------|
| Security redline | ✅/❌ | |
| Basic eligibility | ✅/❌ | |
| Relevance | ✅/❌ | |
| Absorbability | ✅/❌ | |

## 1. Verification Summary

| Dimension | Assessment | Evidence |
|-----------|------------|----------|
| GitHub activity | | stars, last_commit, contributors |
| License | | type + compatibility |
| Security status | | dependabot, CVE, secret scan |
| Quality | | CI status, test coverage, docs |

## 2. Project Overview

<!-- 1-2 paragraphs describing core functionality and positioning -->

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Language | |
| Framework | |
| Runtime | |
| Database | |
| Dependencies | |

## 4. Architecture

<!-- Architecture description + data flow -->

```
<!-- ASCII architecture diagram -->
```

## 5. Core Capabilities

<!-- List of core functional modules and capabilities -->

## 6. API / Interface

| Method | Path | Purpose |
|--------|------|---------|
<!-- All callable interfaces -->

## 7. Security Audit

| Check | Result | Notes |
|-------|--------|-------|
| Malicious code | ✅/❌ | |
| Known vulnerabilities | ✅/❌ | |
| Hardcoded secrets | ✅/❌ | |
| Insecure defaults | ✅/❌ | |
| Permission overreach | ✅/❌ | |

## 8. Judge Scorecard

| Dimension | Weight | Score | Weighted | Note |
|-----------|--------|-------|----------|------|
| Capability fit | 30% | | | |
| Feasibility | 25% | | | |
| Interface compat | 20% | | | |
| Maintenance cost | 15% | | | |
| Security risk | 10% | | | |
| **Total** | **100%** | | | |

**Decision**: ✅ Absorb / ⚠️ Conditional / ❌ Reject
**Depth**: L1/L2/L3/L4/L5

## 9. Classification Analysis

| Existing Project | Overlap | Relationship | Merge Strategy |
|-----------------|---------|--------------|----------------|
<!-- Compare with existing absorbed projects -->

**Classification**: MERGE / SUPERSEDE / ENHANCE / STANDALONE

## 10. Artifact Checklist

- [ ] `analysis_report.md` — This file
- [ ] `skills/<name>/SKILL.md`
- [ ] `mcp-servers/<name>.json`
- [ ] `instincts/<name>.md`
- [ ] `start-<name>.sh` (Unix)
- [ ] `start-<name>.ps1` (Windows)
- [ ] Proxy route
- [ ] Workflow integration
- [ ] Memory system entry
- [ ] `INDEX.md` update

## 11. Usage Scenarios

<!-- 3-5 concrete usage scenarios for quick recall -->

## 12. Iteration Plan

- [ ] <!-- Outstanding tasks -->

## 13. Integration Details

### How to Start

```bash
# Command to start the service/tool
```

### How to Verify

```bash
# Command to verify it's working
```
