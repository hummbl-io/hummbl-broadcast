# CLAUDE.md

## Project

**hummbl-broadcast** — 24/7 AI-generated video broadcast pipeline for HUMMBL.

Tech: Python 3.11+, pyproject.toml, ruff, pytest, RTMP, MiniMax-H3 API adapter

## Commands

```bash
# Setup (Python repos)
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
python -m pytest tests/ -v

# Setup (Node/TypeScript repos)
npm install
npm test
```

## Primitives

| # | Module |
|---|--------|
| 1 | Prompt queue management |
| 2 | Video adapter (MiniMax-H3/H3 Max) |
| 3 | Task poller |
| 4 | Clip store |
| 5 | Composer (brand overlay) |
| 6 | RTMP publisher |
| 7 | Cost governor |
| 8 | Kill switch |
| 9 | Receipt system (prompt hash, model, latency, cost, content URL) |

## Key Conventions

- Python 3.11+ required (where applicable)
- Apache 2.0 license
- Conventional Commits
- Branch naming: `type/agent/short-desc`
- No AI attribution in commit messages (no Co-authored-by, Generated-by, etc.)
- Never commit credentials, secrets, or runtime tokens
- Provider-neutral governance
