# CONSTITUTION.md — hummbl-broadcast

**Status:** v0.1
**Steward:** HUMMBL Research Institute
**Approving human:** Reuben Bowlby
**Standard:** HUMMBL Repo Standard v0.1
**Source of record:** git

## 1. Identity

`hummbl-io/hummbl-broadcast` — 24/7 AI-generated video broadcast pipeline for HUMMBL. Continuously-running video pipeline that generates short clips from prompts via a pluggable adapter (MiniMax-H3), composites them with HUMMBL brand overlays, and pushes to an RTMP endpoint (YouTube Live, Twitch, custom).

- **Class:** library/service
- **Visibility:** public
- **License:** Apache-2.0

## 2. Scope

This constitution operates under the HUMMBL Repo Standard (`hummbl-io/hummbl-governance/docs/standards/HUMMBL_REPO_STANDARD.md`) and the operating-environment constitution on the host machine. This constitution may be stricter than both, never weaker.

## 3. Protected invariants

These invariants are constitutionally protected. They cannot be changed, weakened, or conditionally suspended without a constitutional amendment (§7), a KRINEIA receipt, and human approval.

1. **Apache-2.0 license.** The license is Apache-2.0, unchanged. No proprietary license may be introduced.
2. **Git as source of record.** Git is the canonical source of record. No durable state claim may bypass Git provenance.
3. **Receipt integrity.** The Krineia chain (`_receipts/krineia/primary.jsonl`) is append-only and SHA-256-chained. No operator may rewrite history except via the documented `cut` operator.
4. **No AI attribution in commits.** AI agents may assist but must not be credited in Git commit authorship metadata or commit-message trailers. No `Co-authored-by`, `Generated-by`, or equivalent AI/vendor attribution.
5. **Conventional Commits.** Commit format is Conventional Commits. Breaking changes require a major version bump.
6. **No secrets in Git.** Credentials, API keys, tokens, and private keys must never be committed to the repository.
7. **Provider neutrality.** Root governance is model-, provider-, and vendor-neutral.

## 4. Normative files

The following files are normative. Edits require steward review:

- `CONSTITUTION.md`
- `KRINEIA.md`
- `AGENTS.md`
- `hummbl.repo.yaml` (if present)

## 5. Authority

- **Steward:** HUMMBL Research Institute
- **Approving human:** Reuben Bowlby
- **Agent operating contract:** `AGENTS.md`
- **Receipt manifest:** `KRINEIA.md`

## 6. Receipt-triggering changes

The following changes require a KRINEIA receipt before admission:

- Any edit to `CONSTITUTION.md`, `KRINEIA.md`, or `hummbl.repo.yaml`
- Any change to a protected invariant (Section 3)
- Any release or version bump
- Any change that alters the dependency contract

## 7. Amendment

Changes to this constitution require: a PR, a KRINEIA receipt, and human approval (Reuben Bowlby). Breaking changes bump this constitution's version (SemVer) and trigger a fleet re-audit of all repos consuming this repo's outputs.
