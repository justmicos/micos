# absorb-osp — Open Source Project Absorption Workflow

> A systematic 12-step closed-loop flywheel for evaluating, absorbing, internalizing, and evolving open-source projects into your local AI agent ecosystem.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-brightgreen)](https://claude.ai/code)
[![Hermes Agent](https://img.shields.io/badge/Hermes%20Agent-Compatible-brightgreen)](https://github.com/HermesAgent)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Part of micos](https://img.shields.io/badge/Part%20of-micos-blue)](https://github.com/SATPROTOCOL/micos)

---

## Overview

**absorb-osp** transforms how AI agents interact with open-source projects. Instead of passively cloning repositories, it provides a disciplined 12-step process for:

- **Security-first triage** — Reject malicious or vulnerable projects before they touch your system
- **Deep architecture evaluation** — Understand every project's tech stack, API surface, and integration points
- **Quantified value scoring** — 5-dimension scoring matrix (capability fit, feasibility, compatibility, maintenance cost, security risk)
- **Deduplication & consolidation** — Automatically detect and merge/replace/enhance existing absorbed projects
- **Multi-level absorption** — From knowledge-level (L1) to deep integration (L5)
- **Full ecosystem sync** — Update all indexes, memories, and configurations automatically

### The 12-Step Flywheel

```
Trigger(0) → Triage(1) → Verify(2) → Evaluate(3) → Judge(4) → Classify(5)
→ Internalize(6) → Load(7) → Integrate(8) → Verify(9) → Sync(10) → Iterate(11) → Evolve(12)
```

| Step | Name | Description |
|------|------|-------------|
| 0 | **Trigger** | GitHub URL, user request, or auto-discovery |
| 1 | **Triage** | <30s quick scan: security red flags, basic eligibility |
| 2 | **Verify** | GitHub metadata, license, activity, malware detection |
| 3 | **Evaluate** | Full architecture analysis, API audit, security deep scan |
| 4 | **Judge** | 5-dimension scoring matrix, L1-L5 depth decision |
| 5 | **Classify** | Compare with existing projects: MERGE/SUPERSEDE/ENHANCE/STANDALONE |
| 6 | **Internalize** | Create skill/MCP/config/scripts based on depth level |
| 7 | **Load** | Install dependencies, build, verify startup |
| 8 | **Integrate** | Connect to proxy, trading system, workflow engine, MCP |
| 9 | **Verify** | End-to-end tests: build, API, integration, resource, security |
| 10 | **Sync** | Update all indexes and memory systems |
| 11 | **Iterate** | Usage logs, upstream tracking, issue recording |
| 12 | **Evolve** | Merge similar projects, upgrade capabilities, self-improve |

---

## Features

### Security by Design
- Red-flag checklist at triage step (eval/exec injection, hardcoded C2 endpoints, obfuscated scripts, unsigned binaries)
- Supply chain vulnerability scanning for every dependency
- Rejection with clear reasoning for dangerous projects

### Three Core Principles

1. **Scrutinize, Don't Idolize** — Every project is security-audited. Reject malicious code with clear reasoning.
2. **Absorb, Don't Copy** — Every project must produce tangible artifacts (skills, MCP configs, knowledge files).
3. **Evolve, Don't Accumulate** — Similar projects are merged or consolidated. No redundant capabilities.

### Five Absorption Depths

| Level | Type | Outputs |
|-------|------|---------|
| L1 | Knowledge | Analysis report + instinct file |
| L2 | Tool | L1 + invocable skill |
| L3 | Service | L2 + startup scripts + proxy route |
| L4 | Plugin | L1 + MCP server config |
| L5 | Deep | L3 + L4 + code-level integration + workflow orchestration |

### Agent Framework Support

- **Claude Code** — Native skill + enforcement rules via `.claude/` directory
- **Hermes Agent** — MCP tool config + proxy routing
- **Any LLM Agent** — Portable markdown specs, install scripts, and templates

---

## Quick Start

### Prerequisites

- Git
- An AI agent environment (Claude Code, Hermes Agent, or any LLM-powered coding agent)
- Node.js / Python / Go (depending on projects you absorb)

### Installation

> **Note**: absorb-osp is part of the [micos](https://github.com/SATPROTOCOL/micos) monorepo.

```bash
git clone https://github.com/SATPROTOCOL/micos.git
cd micos/absorb-osp

# For Claude Code
cp -r claude/* ~/.claude/

# For Hermes Agent
cp -r hermes/* ~/.hermes/config/
```

#### Per-project install (git submodule)

```bash
git submodule add https://github.com/SATPROTOCOL/micos.git .claude/micos
ln -s .claude/micos/absorb-osp/claude/* ~/.claude/
```

### Verify Installation

```bash
ls ~/.claude/skills/absorb-osp/
# Should show: SKILL.md WORKFLOW_SPEC.md
```

```bash
ls ~/.claude/rules/absorb-workflow.md
# Should show the enforcement rules
```

### First Use

Simply send a GitHub URL to your AI agent:

> "Let's absorb https://github.com/example/awesome-project"

The agent will automatically follow the 12-step workflow.

---

## Directory Structure

```
absorb-osp/
├── README.md                       # This file
├── LICENSE                         # MIT license
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── .gitignore                      # Ignored files
├── install.sh                      # Unix/macOS installer
├── install.ps1                     # Windows installer
│
├── claude/                         # Claude Code integration
│   ├── SKILL.md                    # Executable skill definition
│   ├── WORKFLOW_SPEC.md            # Complete workflow specification
│   └── rules/
│       └── absorb-workflow.md      # Enforcement rules (auto-loaded)
│
├── hermes/                         # Hermes Agent integration
│   ├── absorb-osp.yaml             # MCP tool + proxy configuration
│   └── README.md                   # Hermes-specific setup guide
│
├── templates/                      # Output templates
│   ├── analysis_report.md          # Project analysis report
│   ├── usage_log.md                # Ongoing usage tracker
│   └── instinct.md                 # Lightweight knowledge file
│
├── shared/                         # Shared indexes
│   ├── INDEX.md                    # All absorbed projects index
│   ├── reject_log.md               # Rejected projects log
│   └── defer_log.md                # Deferred projects log
│
└── examples/                       # Sample outputs
    └── sample-project-analysis.md  # Example analysis report
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ABSORB_OSP_DIR` | `$HOME/.claude` | Agent config directory |
| `ABSORB_OSP_SKILLS_DIR` | `$ABSORB_OSP_DIR/skills` | Skills storage directory |
| `ABSORB_OSP_ABSORBED_DIR` | `$ABSORB_OSP_DIR/absorbed` | Absorbed projects database |
| `ABSORB_OSP_LOG_DIR` | `$ABSORB_OSP_DIR/logs` | Usage logs directory |
| `ABSORB_PROJECTS_DIR` | `$HOME/projects` | Local project clone directory |
| `ABSORB_PORT_MIN` | `8000` | Min port for local services |
| `ABSORB_PORT_MAX` | `8999` | Max port for local services |

### Integration Targets

The workflow supports connecting absorbed services to:

| Target | Protocol | Priority |
|--------|----------|----------|
| AI Agent Skills | Config-based triggers | P0 |
| MCP Server Registry | JSON config | P1 |
| HTTP Proxy | Reverse proxy routes | P1 |
| Workflow Engine | YAML workflow nodes | P2 |
| Monitoring Dashboard | Health check endpoints | P2 |

---

## Usage Examples

### Absorb a project

Ask your AI agent:

> "Can you absorb https://github.com/user/amazing-toolkit?"

The agent will:
1. Run the 30-second security triage
2. Deep-verify GitHub metadata and license
3. Analyze architecture and API surface
4. Score against the 5-dimension matrix
5. Check for duplicates in your existing absorbed projects
6. Create all required artifacts (skill, config, report)
7. Install and verify the project works
8. Sync all indexes and memories

### Check absorbed projects

> "What projects have we absorbed so far?"

### Reject a dangerous project

> "Check out https://github.com/suspicious/sketchy-tool"

The agent's triage step will detect red flags and refuse with a clear explanation.

### Run quarterly consolidation

> "Run quarterly absorb-osp consolidation"

This triggers step 12 (Evolve) to merge similar projects and upgrade capabilities.

---

## Integration Guides

### Claude Code

Copy the `claude/` directory contents to `~/.claude/`:

```bash
cp -r claude/* ~/.claude/
```

The `.claude/rules/absorb-workflow.md` is auto-loaded every session. The skill at `.claude/skills/absorb-osp/SKILL.md` triggers automatically on GitHub URLs.

### Hermes Agent

Copy the `hermes/` directory to your Hermes config:

```bash
cp -r hermes/* ~/.hermes/config/
```

The MCP tool configuration registers `absorb-osp` as a callable tool. The proxy routes allow absorbed services to be accessed through Hermes Gateway.

### Custom Agent

The `WORKFLOW_SPEC.md` is a plain-text specification that any AI agent can follow as instructions. Copy it into your agent's system prompt or knowledge base.

---

## Development

### Running Tests

```bash
make test        # Validate all YAML frontmatter in templates
make lint        # Check markdown formatting
make check       # Verify all required files exist
```

### Building

```bash
make build       # Package for distribution
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/). See [CHANGELOG.md](CHANGELOG.md) for release history.

---

## License

[MIT](LICENSE) — Free for personal and commercial use.

---

## Why This Exists

AI agents today can clone and run almost any open-source project, but they lack a disciplined process for:

- **Security auditing** before running unknown code
- **Deduplication** — absorbing the same type of project multiple times
- **Knowledge retention** — remembering what was absorbed and how to use it
- **System evolution** — merging, upgrading, and retiring absorbed capabilities over time

**absorb-osp** fills this gap with a spec-first, security-aware, evolution-oriented workflow that any AI agent can follow.

---

## 👨‍💻 Developer

**absorb-osp** is part of the **micos** ecosystem, crafted by **[SATPROTOCOL](https://github.com/SATPROTOCOL)**.

<p align="center">
  <a href="https://github.com/SATPROTOCOL">
    <img src="https://img.shields.io/badge/GitHub-SATPROTOCOL-181717?style=for-the-badge&logo=github" alt="SATPROTOCOL">
  </a>
  <a href="https://github.com/SATPROTOCOL/micos">
    <img src="https://img.shields.io/badge/monos-SATPROTOCOL%2Fmicos-blue?style=for-the-badge&logo=github" alt="micos">
  </a>
</p>
