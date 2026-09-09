# Contributing to hummbl-broadcast

Thank you for considering contributing to hummbl-broadcast.

---

## Before You Start

1. **Read the AGENTS.md** for agent conventions and repository guidelines.
2. **Open an issue first** for new features, breaking changes, or architectural questions. Bug fixes and documentation improvements do not require an issue.
3. **Check existing issues** — someone may already be working on the same thing.

---

## Development Setup

```bash
# Clone
git clone https://github.com/hummbl-io/hummbl-broadcast.git
cd hummbl-broadcast

# Create virtual environment (Python repos)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install with test dependencies
pip install -e ".[test]"

# Run tests
python -m pytest tests/ -v
```

---

## Pull Request Process

1. **Branch naming:** `type/description` — e.g., `fix/router-bug`, `docs/readme-update`
2. **Commit format:** Conventional Commits — `fix:`, `feat:`, `docs:`, `test:`, `refactor:`
3. **PR description:** Include what changed and why, test plan, and any breaking changes
4. **CI must pass** where configured
5. **One concern per PR** — do not bundle unrelated changes
6. **No AI attribution** — do not add `Co-authored-by`, `Generated-by`, or equivalent AI/vendor attribution to commits

---

## Code Standards

- Python 3.11+ syntax only (where applicable)
- Type hints required for public functions
- No `print()` statements in production code — use logging or the governance bus
- Every new feature needs tests
- Every bug fix needs a regression test

---

## Questions?

- **Technical:** Open an issue with the `question` label
- **Security:** Email security@hummbl.io (do not open public issues for security concerns)
- **General:** Reach out on the HUMMBL governance bus or in GitHub discussions

---

**License:** Apache 2.0. By contributing, you agree that your contributions will be licensed under the same license.
