# Contributing to absorb-osp

Thank you for considering contributing to this project!

## How to Contribute

### Report Issues

- Use GitHub Issues to report bugs or suggest features
- Include your agent framework (Claude Code, Hermes Agent, etc.)
- Describe the step in the workflow where the issue occurred

### Submit Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run validation: `make test`
5. Commit with conventional commit messages
6. Push and open a Pull Request

### Development Setup

```bash
git clone https://github.com/justmicos/micos.git
cd absorb-osp
make dev-setup
```

### Code Style

- Markdown: Follow `.markdownlint.json` rules
- YAML frontmatter: Validate with `make lint`
- Shell scripts: Ensure POSIX-compatible (bash) and PowerShell variants

### Pull Request Guidelines

- Keep PRs focused on a single concern
- Update CHANGELOG.md for user-facing changes
- Update README.md if adding new features
- Add or update templates if changing output formats
- Test with both Claude Code and Hermes Agent if possible

## Workflow Evolution

This project is itself meant to evolve. If you identify a step in the workflow that could be improved, or a new step that should be added, please open an issue or PR.

The workflow specification (`claude/WORKFLOW_SPEC.md`) and the skill definition (`claude/SKILL.md`) should always be kept in sync.
