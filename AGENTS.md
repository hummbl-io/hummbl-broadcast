# AGENTS.md — hummbl-broadcast

## Mission & Governance
This repository is an active component of the HUMMBL fleet.
All agents operating within this repository are bound by the canonical governance rules and protocols defined at the fleet root:
- Canonical Rules & Guardrails: `~/.agents/rules/`
- Apex Connection Point: `apex-nexus` (`https://github.com/hummbl-io/apex-nexus.git`)
- Public Publishing Authority: `oss` (`https://github.com/hummbl-io/oss.git`)

## Operational Disciplines
1. **Verify Before Claiming**: Verify file states, tests, and metrics directly before claiming completion or resolution.
2. **Branching & Commits**: Never commit directly to `main`. Create feature branches (`feat/<agent>/<desc>` or `fix/<agent>/<desc>`). Sign commits where required.
3. **Topology Boundaries**: Archived frameworks (`founder-mode`, standalone `hummbl-governance` repo) are dead and scavenger-only.
4. **Coordination Bus**: Transmit milestones and significant updates via the canonical bus bridge (`bus-post.ps1`).
