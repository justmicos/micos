# 🔒 Privacy & Configuration Guide

> **Everything in this repository is PUBLIC.** Never commit personal information.

---

## What NOT to Commit

| Category | Examples | Why |
|----------|----------|-----|
| Local file paths | `C:\Users\yourname\`, `/home/yourname/` | Reveals your username and system layout |
| API keys | `sk-...`, `ghp_...`, `AKIA...` | Credential theft |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----` | System compromise |
| Emails | `yourname@gmail.com` | Spam, doxxing |
| IP addresses | `192.168.1.x`, `10.0.0.x` | Network topology leak |
| Personal names | Full real name if not public | Privacy |
| Local project paths | References to your specific directories | Reveals project structure |

## Automated Protection

This repository includes automated privacy protection at multiple levels:

### 1. Pre-Push Hook (local)

Blocks pushes containing privacy leaks before they reach GitHub.

```bash
# Install the hook (one-time)
ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push
chmod +x scripts/pre-push.sh
```

### 2. GitHub Actions CI (remote)

Every push and PR is automatically scanned. Privacy check runs FIRST and blocks the pipeline if leaks are found.

### 3. Pre-Release Check

Before any release tag (`v*`) is published, a full privacy scan runs. Releases with leaks are blocked.

---

## User Configuration

### Environment Variables

All user-specific paths and preferences are configurable via environment variables.
**Never hardcode local paths in repository files.**

| Variable | Default | Config File | Description |
|----------|---------|-------------|-------------|
| `CLAUDE_CONFIG_DIR` | `~/.claude` | `~/.claude/config.json` | Claude Code configuration directory |
| `ABSORB_PROJECTS_DIR` | `~/projects` | `~/.config/absorb-osp/config` | Local clone directory for absorbed projects |
| `ABSORB_PORT_MIN` | `8000` | `~/.config/absorb-osp/config` | Minimum port for local services |
| `ABSORB_PORT_MAX` | `8999` | `~/.config/absorb-osp/config` | Maximum port for local services |

### User Config File

Create `~/.config/absorb-osp/config` (not in the repository!):

```ini
# ~/.config/absorb-osp/config
# Local configuration — NEVER commit this file

CLAUDE_CONFIG_DIR=/home/user/.claude
ABSORB_PROJECTS_DIR=/home/user/projects
ABSORB_PORT_MIN=8000
ABSORB_PORT_MAX=8999
```

---

## Customizing for Your Fork

When forking this repository, you must update:

| What | Where | Replace With |
|------|-------|-------------|
| GitHub org/user | `README.md`, `CHANGELOG.md` | Your GitHub username |
| Repo URL | `install.sh`, `install.ps1` | Your fork URL |
| Contact info | `CONTRIBUTING.md` | Your contact |

**Always run the privacy scanner before pushing to your fork:**

```bash
python3 scripts/privacy-check.py .
```

---

## Pre-Release Checklist

Before tagging a release:

- [ ] `python3 scripts/privacy-check.py . --verbose` — Zero findings
- [ ] `python3 scripts/validate.py absorb-osp/templates/` — All pass
- [ ] `make check` — All files present
- [ ] Reviewed for accidental local references
- [ ] Updated CHANGELOG.md
- [ ] Bumped version in claude/SKILL.md

---

## Reporting a Privacy Leak

If you discover a privacy leak in a published commit:
1. **Immediately** revoke any exposed credentials
2. Open a GitHub Issue with `[PRIVACY]` prefix
3. Do not post details publicly — contact the maintainer directly

---

*Last updated: 2026-05-23*
