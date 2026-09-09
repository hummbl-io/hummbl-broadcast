# DOCTRINE.md — hummbl-broadcast

**Status:** v0.1
**Steward:** HUMMBL Research Institute

## 1. Thesis

hummbl-broadcast is 24/7 ai-generated video broadcast pipeline for hummbl. Continuously-running video pipeline that generates short clips from prompts via a pluggable adapter (MiniMax-H3), composites them with HUMMBL brand overlays, and pushes to an RTMP endpoint (YouTube Live, Twitch, custom). The core bet is that 24/7 ai-generated video broadcast pipeline for hummbl should be built with stdlib-only, dependency-free, and embeddable principles where applicable, aligned with the HUMMBL governance framework.

## 2. Conceptual vocabulary

- **Governance** — the framework of receipts, identity, roles, laws, and evidence that governs agent actions
- **Receipt** — a structured, signed record that an action affecting shared state occurred
- **Admission** — the gated process by which candidate state becomes durable state
- **Krineia** — the append-only, SHA-256-chained receipt system that proves governance happened

## 3. Design principles

1. **Stdlib-first.** Prefer Python stdlib over third-party dependencies where possible.
2. **Proven before shipped.** Primitives are extracted from production use, not theoretical.
3. **Receipts-first.** Agents post evidence before claiming completion.
4. **Fast-fail, never hang.** Systems should degrade gracefully rather than blocking indefinitely.
5. **Provider-neutral.** Root governance is model-, provider-, and vendor-neutral.
6. **No AI attribution.** AI agents may assist but must not be credited in Git commit metadata.

## 4. Boundaries

hummbl-broadcast provides its specific scope; it is not an orchestration platform (that is hummbl-agent's control plane), does not define mental models (that is Base120), and does not replace the governance runtime (that is hummbl-governance). It is focused on its defined scope and integrates with the broader HUMMBL ecosystem via the coordination bus and governance primitives.

## 5. Open questions

- How should this repo integrate with the KRINEIA governance network as it matures?
- What is the right boundary between this repo's scope and adjacent HUMMBL repos?
- How can compliance mapping stay current as regulatory frameworks evolve?
- Should this repo expose MCP server tools for its primitives?
