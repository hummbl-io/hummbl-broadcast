# Phase -1 Admission Packet — Governed AI Stand-In for 24/7 Broadcast

**Candidate**: `governed-ai-standin` (working name)
**Date**: 2026-09-06 (revised 2026-09-06 per ARCANA v1)
**Author**: devin (anvil)
**Status**: PHASE_0_GATE_PENDING (ARCANA v1 complete, P1 findings addressed, peer review pending)
**Phase**: -1 (admission packet drafted, ARCANA review complete, revision complete, peer review pending, gate evaluation pending)
**Parent session**: AI avatar / digital twin research thread (web research + reubenos read + bus scan + handoff protocol design)
**Discovery artifacts**: web research synthesis (12+ external systems), reubenos repo read, coordination bus scan, cohost/streaming stack review, hummbl-music 24/7 broadcast review
**ARCANA v1**: 5 lenses (schneier/ashby/ostrom/zuboff/popper), unanimous NEEDS-REVISION, 28 P1 findings consolidated into 22 revision items below

### Revision log (ARCANA v1 → revision)

| # | ARCANA finding (lens) | Revision |
|---|---|---|
| R1 | Chat is unauthenticated injection vector into on-air AI (schneier P1-1, ashby P1-2) | §11 Threat Model + §13 typed chat actions + chat quarantine spec |
| R2 | Typed action boundary is unenforced assertion (schneier P1-3, popper P1.3) | §13 enforcement mechanism (separate-process IPC) + competing seams enumerated + falsification condition |
| R3 | Heartbeat has no cryptographic integrity, no fail-safe defaults (schneier P1-2, ashby P1-5) | §14 HMAC-signed heartbeat + fail-safe defaults + graduated response |
| R4 | Cooperative kill switch insufficient for autonomous on-air (schneier P1-4) | §15 hard kill in separate trust domain + kill chain |
| R5 | Hybrid identity impersonation window + persona.py contradiction (schneier P1-5, ostrom P1-2, popper P1.4) | §16 contradiction resolution + enforcement outside twin trust domain + falsification condition |
| R6 | TRANSITIONING state has no timeout (schneier P1-6) | §17 TRANSITIONING_TIMEOUT + per-step timeouts + REPLAY fallback |
| R7 | Circular monitoring — AI monitors itself (ostrom P1-1) | §18 independent watchdog + platform moderation + viewer sentiment monitor |
| R8 | Binary sanctions — REPLAY or nothing (ostrom P1-4, ashby P1-1) | §19 graduated sanction tiers (Green/Yellow/Red) + AI_STANDIN_DEGRADED state |
| R9 | No conflict-resolution mechanism (ostrom P1-5) | §20 handoff arbitration + viewer grievance channel + platform moderation handler |
| R10 | Audience trust not modeled as depletable CPR (ostrom P1-6) | §21 trust resource model + depletion signals + trust budget |
| R11 | No viewer data retention/deletion/right-to-be-forgotten (zuboff P1-1) | §22 viewer data classification + TTL + deletion path + R-14 boundary |
| R12 | No data flow boundary — viewer chat can reach cloud providers (zuboff P1-2) | §23 data flow boundary diagram + hard rule |
| R13 | No counter-asymmetry mechanism (zuboff P1-3) | §24 viewer-facing data practice statement + opt-out |
| R14 | Defense stack has no latency budget — R-7 = dead air (ashby P1-3) | §25 sync vs async layers + latency budget + buffer-ahead |
| R15 | ContentScheduler exhaustion undefined (ashby P1-4) | §26 GENERATING/BUFFERED/DEPLETED states + DEPLETED→REPLAY |
| R16 | Multi-platform divergence — single-state breaks (ashby P1-6) | §27 Phase 1 scoped to single-platform, multi-platform deferred to Phase 2 |
| R17 | Novelty conjunction unfalsifiable (popper P1.1) | §3 restated as single differentiator + fixed falsification rule |
| R18 | No kill threshold — every failure defers/downgrades (popper P1.2) | §6 terminal failure condition + §8 downgrade as separate candidate |
| R19 | "Never hand off to human" contradicted by Appendix A (popper P1.6) | §4 + Appendix B resolved: AI may accept human takeover, never initiate |
| R20 | Phase 0 gate governance-only — all empirical falsification deferred (popper P1.7) | §7 + §8 pre-gate empirical smoke test added |
| R21 | Falsification cases 1,2,3 lack metrics/thresholds (popper P1.5) | §6 metrics + thresholds + dispositions for all cases |
| R22 | cohost guardrail conflict (ostrom P1-3) | §28 guardrail reconciliation (suspended/preserved/modified) |
| R23 | ARGUED-NOT-TESTED conflates argument with evidence (popper P2.1) | §4 status legend renamed ARGUED-NOT-TESTED |
| R24 | R-7 self-check bypassable (schneier P2-2) | §25 independent model in separate process for broadcast mode |
| R25 | Signed memory poisoning during compromised sessions (schneier P2-6) | §29 broadcast_session provenance tag + post-session quarantine |
| R26 | No rate limiting on handoff triggers (schneier P2-4) | §17 minimum dwell time + handoff rate limit |
| R27 | GPU/VRAM as attack vector (schneier P2-5) | §30 VRAM budget enforcement + REPLAY before OOM |
| R28 | Voice clone revocation gap (zuboff P2-2) | §31 local-first preference + revocation procedure |
| R29 | ContentScheduler optimization unconstrained (zuboff P2-3) | §32 objective stated + open-loop default + pre-authorized content pool |
| R30 | Bus events unsigned (schneier P3-1) | §33 bus event signing |
| R31 | No viewer/moderator-triggered kill (schneier P3-2) | §18 trusted moderator safety handoff |
| R32 | Voice clone theft inherent (schneier P3-3) | §11 threat model acknowledgment + audio watermarking upgrade |
| R33 | TESTING/REHEARSAL state missing (ashby P2-2) | §34 TESTING state for falsification plan |
| R34 | SPEAK_SEGMENT too coarse (ashby P2-4) | §13 segment_class field |
| R35 | No voice-output fidelity layer (ashby P2-5) | §35 R-16/R-17 proposed for audio modality |
| R36 | REPLAY recovery path unspecified (ashby P2-7) | §17 REPLAY exit conditions |
| R37 | START_STREAM/END_STREAM not in enum (ashby P2-8) | §13 added, operator-only |
| R38 | No collective-choice arrangement (ostrom P2-4) | §36 minimal post-stream retro + platform overlay |
| R39 | Monocentric governance (ostrom P2-5) | §18 polycentric map (5 centers) |
| R40 | R-2 not rate-aware (ashby P2-6) | §13 aggregate injection detection |
| R41 | "Even small N" pre-licenses anecdote (popper P3.1) | §6 struck, replaced with N=20 threshold |
| R42 | Counterexamples list is confirmation not falsification (popper P3.3) | §6 paired each "must preserve" with "must not occur" |
| R43 | "Operate as Reuben" borrows social capital (zuboff P3-3) | §16 disclosure states "Reuben is not present" |
| R44 | Dynamic disclosure (schneier P3-4, ostrom P2-2) | §16 viewer-aware disclosure model |
| R45 | Trust restoration (ostrom P3-2) | §21 restoration protocol |
| R46 | Platform-specific ToS filtering (ashby P3-4) | §27 deferred to Phase 2 with multi-platform |

---

## 1. Candidate Definition

### What

A **governed autonomous on-air talent layer** that allows ReubenOs (the
governed counterpart twin of Reuben Bowlby) to assume broadcasting duties
on a 24/7 live stream when the human operator is unavailable, while
preserving Reuben's identity, personality, values, operating constraints,
governance requirements, and safe handoff behavior.

The candidate produces:

- A `PresenceState` state machine (OFFLINE / LIVE_HUMAN / AI_STANDIN /
  REPLAY / TRANSITIONING) governing who is on-air
- A presence handoff protocol (human→AI, AI→human, AI→REPLAY safety
  self-handoff) with heartbeat, bus events, and emergency shutdown
- A typed action boundary where ReubenOs emits typed broadcast intents
  (`SPEAK_SEGMENT`, `IDLE`, `HANDOFF_BACK`, `EMERGENCY_STOP`) that a
  `PresenceActionExecutor` validates and executes against OBS / TTS /
  avatar / streaming integrations — the model proposes, policy validates,
  integrations execute (Neuro-sama pattern)
- A `BroadcastTwinConfig` extension to the existing reubenos
  `governed-counterpart` framework that adds broadcast scope to the
  15-layer defense stack (R-1 through R-15) without modifying the
  operator-owned persona definition
- Integration seams connecting reubenos to voice cloning, avatar
  rendering, OBS scene routing, chat ingestion, and streaming
  destinations as **separate execution layers** governed by, but not
  collapsed into, the identity core

### Why

1. **The 24/7 broadcast vision requires human-absent operation.** A 24/7
   stream that only runs when the human is present is not 24/7. The
   operator has explicitly requested a stand-in capability for the hours
   he cannot be on-air.

2. **The internal infrastructure is 80% built but the autonomous talent
   layer is missing.** The fleet has: reubenos (governed identity core,
   15 defense layers), cohost agent + 5 skills (operator-assistive
   production), hummbl-broadcast daemon (clip generation + RTMP
   skeleton), hummbl-music 24/7 audio loop, OBS/Voicemod/NVIDIA
   Broadcast control scripts, and aggregator research. What is missing:
   avatar rendering, voice cloning, presence handoff, the live
   content loop, and the ReubenOs broadcast extension.

3. **The governance question is load-bearing.** ReubenOs persona.py
   currently says "never impersonate the principal (Reuben Bowlby)." The
   24/7 stand-in vision requires ReubenOs to be on-air as Reuben. This
   tension must be resolved explicitly, not worked around. The operator
   has selected the **hybrid identity** stance (intro as ReubenOs →
   operate as Reuben → periodic disclosures), which requires a broadcast
   scope amendment to persona.py — operator-only per Constitution
   Article VI.1.

### Scope

- **In scope**: presence state machine design; handoff protocol design;
  typed action boundary for broadcast intents; `BroadcastTwinConfig`
  seam design; integration map showing what wraps what; hybrid identity
  stance and its governance implications; staged proof-of-concept
  recommendation.
- **Out of scope**: avatar rendering implementation; voice cloning
  implementation; Twitch/YouTube/Kick chat connector implementation;
  multistream fan-out deployment; persona.py amendment (operator-only,
  gated on Phase 0 approval); production launch; any code changes to
  reubenos, hummbl-broadcast, or cohost skills.
- **NOT a deployment claim.** This packet establishes the architectural
  design and governance boundary for the capability. It does not claim
  the system is built, tested, or ready for production.

### Disposition options (per LLL protocol)

```
REJECT_AS_DISTINCT_FRAMEWORK
RETAIN_AS_INTERNAL_HEURISTIC
PUBLISH_AS_TECHNICAL_REPORT
ADVANCE_TO_PREPRINT
ADVANCE_TO_FORMAL_RESEARCH_PROGRAM
ADVANCE_TO_IMPLEMENTATION
```

**Target disposition: `ADVANCE_TO_IMPLEMENTATION`** (engineering
candidate, not research — operationalizes the existing reubenos
governed-counterpart framework in a new broadcast domain).

---

## 2. Prior-Art Map

**Survey completed 2026-09-06.** 12+ external systems surveyed across
commercial digital twins, open-source self-hostable stacks, voice
cloning, and autonomous VTuber research. Internal prior art surveyed
across reubenos, governed-counterpart, cohost, hummbl-broadcast,
hummbl-music, hummbl-voice, hummbl-integrations, and the coordination
bus.

### Internal prior art

| System | What it provides | Reuse vs build new |
|---|---|---|
| **reubenos** | Governed identity core: persona, 15-layer defense stack (R-1 to R-15), signed actions, provenance, memory integrity | **REUSE** — the identity and governance layer, extended with `BroadcastTwinConfig` |
| **governed-counterpart** | The framework reubenos is built on (twin types, bus writer, defense layer contracts) | **REUSE** — the framework, extended for broadcast twin type |
| **cohost agent + 5 skills** | Operator-assistive production: OBS/Voicemod/NV Broadcast control, chat read, content prep, go-live orchestration | **REUSE** — the control surfaces and skills, wrapped by `PresenceActionExecutor` |
| **hummbl-broadcast daemon** | Clip generation state machine (IDLE→SUBMITTING→POLLING→COMPOSING→PUBLISHING), cost governor, kill switch, RTMP publisher skeleton | **REUSE** — kill switch primitive, cost governor pattern; **BUILD NEW** — persistent stream pipe, presence state machine |
| **hummbl-music** | 24/7 audio broadcast (`stream_247`, `overnight_loop`), 197x real-time audio throughput | **REUSE** — as REPLAY state content source |
| **hummbl-voice** | Vendor-neutral `VoiceAdapter` protocol with `safety_handoff` and `substitute_runtime` | **REUSE** — protocol pattern; **BUILD NEW** — `VoiceCloneAdapter` impl |
| **hummbl-integrations** | 45+ adapters including LLM and Google Cloud TTS; Supadata for YouTube transcripts | **REUSE** — LLM adapters for content loop, Supadata for news fetch |
| **coordination bus** | Append-only TSV event transport, UTC, governed | **REUSE** — handoff events, presence state posts |

### External prior art — commercial digital twins / 24/7 livestream

| System | Capability | Reuse vs build new | Pre-emption risk |
|---|---|---|---|
| **HeyGen Avatar V** | Identity-consistent avatar from short recordings, multilingual, phoneme lip-sync | Reference only (managed, not self-hosted) | LOW — no governance layer |
| **D-ID V4** | Low-latency real-time avatar rendering, strong lip-sync | Reference only | LOW — no governance layer |
| **Syntopia / AvatarCast / WOMO AlwaysOn** | Managed 24/7 digital-twin livestream | Reference only (WOMO: "AI extension of real influencer, not replacement") | LOW — managed, not self-hostable, no governance |
| **MoltStream** | End-to-end Chat listener → LLM → TTS → Avatar → OBS → RTMP | **Architecture reference** (strongest pattern match) | LOW — no governance, no typed action boundary |
| **Open-LLM-VTuber** (13.7K stars) | Self-hosted Live2D, ASR, LLM, TTS, OBS browser source | **Implementation reference** for self-hosted avatar stack | LOW — no governance layer |
| **Wallie V2** | Modular persona/topics/chat/vision/hearing/schedule/voice/OBS/Live2D | **Architecture reference** for modularity | LOW — no governance |
| **kvtuber** | Browser-based AI VTuber runtime, viewer/broadcast mode, scheduled programs | **Implementation reference** | LOW — no governance |

### External prior art — voice cloning

| System | Self-hostable? | Latency | Reuse vs build new |
|---|---|---|---|
| **Fish Audio s2.1-pro** | Yes (API) | Streaming | Candidate for `VoiceCloneAdapter` |
| **F5-TTS** | Yes (local) | Batch + streaming | Candidate (local-first) |
| **OpenVoice v2** | Yes (local) | Batch | Candidate (local-first) |
| **XTTS-v2** | Yes (local) | Streaming | Candidate (local-first) |
| **ElevenLabs Flash v2.5** | No (API) | Low-latency streaming | Managed fallback only |
| **Sesame CSM-1B** | Yes (local) | Streaming | Candidate (local-first) |

### External prior art — autonomous VTuber research

- **Autonomous-VTuber** research: agent orchestration, tool calling,
  content selection, viewer memory, adaptive content mix.
- **Neuro-sama** (Vedal987): the typed-action architecture pattern —
  model emits typed intents, separate system validates and executes.
  This is the load-bearing architectural reference for the
  `PresenceActionExecutor` seam.

### Gap analysis

| Capability | External state | Internal state | Gap |
|---|---|---|---|
| Governed identity for on-air AI | **NONE** — no commercial or OSS system has a 15-layer defense stack, signed actions, provenance, or operator-owned persona | reubenos has it for text conversation | Extend reubenos to broadcast domain |
| Presence handoff (human↔AI) | **NONE** — managed services assume always-AI or always-human | cohost has launch/shutdown but no AI takeover state | Build `PresenceState` + handoff protocol |
| Typed action boundary for broadcast | Neuro-sama pattern (proprietary, not published as framework) | reubenos has action allowlist for text actions | Extend allowlist with broadcast action types |
| Hybrid identity (intro as AI → operate as human) | **NONE** found | reubenos says "never impersonate principal" | Requires operator-approved persona.py amendment |
| Self-hosted avatar + voice + governance | **NONE** — OSS stacks have avatar+voice but no governance; commercial has governance-via-ToS but not self-hosted | reubenos (governance) + hummbl-broadcast (streaming) + hummbl-music (24/7 audio) exist separately | Integrate with new seams |

### Decision: REUSE vs BUILD NEW

**REUSE** (do not reinvent):
- reubenos 15-layer defense stack ← existing implementation
- governed-counterpart framework ← existing framework
- cohost OBS/Voicemod/NV Broadcast control ← built 2026-09-06
- hummbl-broadcast kill switch + cost governor ← existing primitives
- hummbl-music 24/7 audio loop ← REPLAY state content
- Neuro-sama typed-action pattern ← architectural reference (not code)
- Open-LLM-VTuber / Wallie / kvtuber ← implementation references for avatar stack
- Fish Audio / F5-TTS / OpenVoice / XTTS-v2 ← voice clone candidates

**BUILD NEW** (genuine contribution):
- `PresenceState` enum + state machine
- `PresenceDriver` protocol + `HumanPresenceDriver` / `AIAvatarPresenceDriver` / `ReplayPresenceDriver` implementations
- `PresenceHeartbeat` (inverse of kill switch — file that operator updates, timeout triggers handoff)
- `PresenceActionExecutor` (validates typed broadcast intents, executes against integrations)
- `SceneRouter` (thin wrapper over cohost-tech `obs_ctl.py switch`)
- `VoiceCloneAdapter` (extends hummbl-voice `VoiceAdapter` with governed voice identity)
- `AvatarDriver` (the biggest missing piece — lip-synced avatar rendering)
- `ContentScheduler` (autonomous content selection for AI stand-in hours)
- `BroadcastTwinConfig` (extends reubenos `twin_config.py` with broadcast scope)
- Hybrid identity disclosure protocol (intro script + periodic disclosure cadence)
- Bus event schema for presence handoff (`PRESENCE_HANDOFF`, `PRESENCE_STATE`, `PRESENCE_SAFETY_HANDOFF`, `PRESENCE_EMERGENCY_SHUTDOWN`)

---

## 3. Novelty Assessment

**Novelty verdict: NOVEL SYNTHESIS** (restated per ARCANA popper P1.1).

**Restated as a single differentiator** (not a 5-component conjunction):

> The contribution is a **governed, operator-owned identity layer for
> on-air AI** — absent from all surveyed external systems. The
> integration of reubenos (15-layer defense stack, signed actions,
> provenance, operator-owned persona) into a real-time broadcast domain
> with typed action validation, presence handoff, and hybrid identity
> disclosure is the novel element. The components (avatars, voice
> cloning, VTuber stacks, 24/7 streaming) are not novel.

**Fixed falsification rule** (binding, per popper P1.1):

> If any single external system exhibits ≥ 4 of the following 5
> attributes — (1) governed identity with signed actions, (2) typed
> action boundary between model and actuators, (3) presence handoff
> protocol with human↔AI states, (4) operator-owned persona with
> immutability + amendment scope, (5) self-hosted/local-first — the
> novelty claim is downgraded from NOVEL SYNTHESIS to INCREMENTAL.
> If ≥ 5, the claim is downgraded to RETAIN_AS_INTERNAL_HEURISTIC (no
> novelty beyond existing work).

**What is NOT claimed as novel:**
- AI avatars / digital twins themselves (HeyGen, D-ID, Syntopia — commercial)
- Self-hosted AI VTuber stacks (Open-LLM-VTuber, Wallie, kvtuber — OSS)
- Voice cloning (Fish Audio, F5-TTS, ElevenLabs — published)
- The typed-action architecture pattern (Neuro-sama — proprietary but
  observed)
- 24/7 broadcast infrastructure (hummbl-music — internal)
- Governed counterpart twins (reubenos / governed-counterpart — internal)

The candidate's contribution is **the governed identity layer applied to
broadcast**, not the components.

---

## 4. Claim Decomposition

| Claim type | Claim | Evidence required | Status |
|---|---|---|---|
| Structural | "reubenos is a governed identity core, not a broadcast/voice/avatar engine" | reubenos README + ARCHITECTURE.md + persona.py + twin.py read | **CONFIRMED** (verified 2026-09-06) |
| Structural | "cohost is operator-assistive, not autonomous takeover" | cohost.md line: "The operator is the host; you run the show around them" | **CONFIRMED** (verified 2026-09-06) |
| Structural | "hummbl-broadcast has a kill switch and cost governor but no persistent stream pipe or presence state machine" | daemon.py + kill_switch.py read | **CONFIRMED** (verified 2026-09-06) |
| Structural | "hummbl-music has 24/7 audio broadcast modules (stream_247, overnight_loop)" | File listing + bus SITREP 2026-09-06 | **CONFIRMED** (verified 2026-09-06) |
| Novelty | "No existing system combines governed identity + typed action boundary + presence handoff + hybrid identity + self-hosted" | External prior-art survey (12+ systems) | **ARGUED-NOT-TESTED** — survey done, ARCANA review pending |
| Governance | "reubenos persona.py says 'never impersonate the principal' — broadcast stand-in requires resolving this tension" | persona.py boundary read | **CONFIRMED** (verified 2026-09-06) |
| Governance | "Hybrid identity stance (operator-selected) requires persona.py broadcast scope amendment — operator-only per Constitution Art. VI.1" | Operator selection via ask_user_question | **CONFIRMED** (operator selected 2026-09-06) |
| Architectural | "The typed-action boundary (Neuro-sama pattern) is the correct governance seam — model proposes, policy validates, integrations execute" | Neuro-sama observation + reubenos action allowlist pattern | **ARGUED-NOT-TESTED** — ARCANA review pending |
| Architectural | "PresenceState should include REPLAY as a distinct state (safe fallback when neither human nor AI can be on-air)" | hummbl-broadcast clip buffer + hummbl-music overnight_loop exist | **ARGUED-NOT-TESTED** — ARCANA review pending |
| Architectural | "The AI may *accept* a human takeover (human-initiated), but may never *initiate* a handoff that assumes the human will appear — its self-handoff target is always REPLAY" | Design reasoning (AI cannot force human to appear); resolved per popper P1.6 (see Appendix B) | **ARGUED-NOT-TESTED** — falsifiable: if AI emits handoff intent with target=LIVE_HUMAN on a safety trigger, boundary is violated |
| Implementation | "PresenceHeartbeat (inverse of kill switch) can trigger human→AI handoff on timeout" | kill_switch.py pattern exists | **PENDING** — Phase 1 implementation |
| Implementation | "BroadcastTwinConfig can extend reubenos twin_config.py without modifying persona.py" | twin_config.py structure | **PENDING** — Phase 1 implementation |
| Implementation | "VoiceCloneAdapter can extend hummbl-voice VoiceAdapter protocol with governed voice identity" | hummbl-voice protocol exists | **PENDING** — Phase 1 implementation |
| Utility | "The staged proof-of-concept (voice-only → governed chat loop → OBS output → handoff → private stream → platform chat → multistream → high-fidelity avatar) is the safe rollout path" | Operator preference + risk analysis | **ARGUED-NOT-TESTED** — ARCANA review pending |
| Normative | "AI stand-in should always disclose its AI status" | EU AI Act Art. 50 transparency + operator values | **CONFIRMED** (operator values: honesty over comfort) |
| Normative | "The hybrid identity stance is ethically preferable to silent impersonation or full AI-as-distinct-entity" | Operator selection | **NOT CLAIMED** — operator decision, not a generalizable normative claim |

**Status legend** (revised per ARCANA popper P2.1):
`CONFIRMED` = verified against primary sources;
`ARGUED-NOT-TESTED` = structural argument made, no empirical test yet
(ARCANA review is a reasoning check, not an empirical test — passage
does not convert argument into evidence);
`PENDING` = not yet attempted (Phase 1 work); `NOT CLAIMED` = explicitly
out of scope.

---

## 5. Formalism Audit

### What formal object is this?

1. **A state machine over PresenceState = {OFFLINE, LIVE_HUMAN,
   AI_STANDIN, REPLAY, TRANSITIONING}.** State transitions are triggered
   by: operator command, heartbeat timeout/resume, schedule, AI safety
   self-handoff, or emergency shutdown.

2. **A typed action protocol.** ReubenOs emits typed intents
   (`SPEAK_SEGMENT`, `IDLE`, `HANDOFF_BACK`, `EMERGENCY_STOP`,
   `SWITCH_SCENE`). A `PresenceActionExecutor` validates each intent
   against the reubenos action allowlist + broadcast scope + current
   PresenceState before executing. Invalid intents are rejected and
   logged.

3. **NOT a free-form LLM-to-actuator pipeline.** The model does not
   directly control OBS, RTMP, TTS, or platform APIs. The typed action
   boundary is the governance seam.

4. **NOT a single "digital twin" component.** The architecture is
   explicitly layered:
   ```
   reubenos (identity + governance)
     → typed, validated, auditable broadcast intents
       → ContentScheduler / chat router / moderation
         → VoiceCloneAdapter / TTS
           → AvatarDriver / lip-sync
             → OBS / scene router / RTMP
               → YouTube / Twitch / Kick / Discord
   ```
   These layers must not be collapsed.

5. **Operational form**: a set of Python protocols + implementations
   integrated into the existing hummbl-broadcast daemon and cohost skill
   stack, with reubenos as the identity core.

### Downgrade option

If full avatar rendering proves too expensive for Phase 1, downgrade to:
"voice-only AI stand-in with static AI-disclosure card as OBS video
source." This preserves the governance layer, presence handoff, typed
action boundary, and hybrid identity while deferring avatar rendering to
a later phase. The operator's staged proof-of-concept preference
supports this downgrade path.

**Selected formalism**: full presence state machine + typed action
protocol + layered architecture, with voice-only downgrade path
preserved for Phase 1.

### What it is NOT, formally

- Not a replacement for the human broadcaster (hybrid identity stance:
  the AI is a disclosed stand-in, not a replacement)
- Not an unconstrained autonomous agent (typed action boundary +
  15-layer defense stack + operator-authorized broadcast scope)
- Not a single monolithic component (layered architecture, separate
  execution layers)
- Not a deployment (design + governance boundary, not built code)

---

## 6. Falsification Plan

**Revised per ARCANA popper P1.5, P1.2, P3.3**: All cases now have
metrics, thresholds, measurement procedures, and dispositions. Cases
1-4 are testable in the pre-gate empirical smoke test (§7) or Phase 1.
"Even small N" is struck and replaced with N=20.

### Terminal failure condition (kill threshold, per popper P1.2)

> **If the voice-only pre-gate smoke test (§7), run for ≥ 30 minutes
> with operator review on a 5-rubric scale (naturalness, similarity,
> coherence, persona-fidelity, broadcast-acceptability), produces an
> average rubric score < 3.0/5.0, the candidate is REJECTED — not
> downgraded, not deferred to the next stage.** This is the kill
> threshold. If the candidate survives this, it advances to Phase 0
> gate. If it does not, the voice-only variant is a *separate
> candidate* requiring its own admission (per popper P2.2 — the
> downgrade is not a retreat path for this candidate).

### Cases where the candidate fails

1. **The integration is more complex than the components justify** →
   REJECT.
   - **Metric**: integration surface area = count of cross-repo
     contracts + LOC of glue code + count of distinct failure modes
     in smoke test.
   - **Threshold**: > 10 cross-repo contracts OR > 2000 LOC glue code
     OR > 5 distinct failure modes in 30-min smoke test.
   - **Measurement**: count during smoke test implementation.
   - **Disposition**: REJECT (not RETAIN — RETAIN is a separate
     disposition for a different finding).

2. **The typed action boundary is too restrictive for engaging live
   content** → REJECT or revise boundary.
   - **Metric**: operator rubric "broadcast-acceptability" score (1-5)
     for 30-min voice-only governed session.
   - **Threshold**: < 3.0/5.0 average → boundary is wrong seam; test
     alternative seams (§13 competing seams). If alternative seams
     also fail < 3.0, REJECT.
   - **Falsification of the boundary itself** (per popper P1.3): if
     ≥ 30% of engaging (rubric ≥ 4.0) segments require intent types
     outside the initial allowlist, AND expanding the allowlist does
     not recover engagement within 3 iterations, the typed-action
     boundary is the wrong seam → test output-layer governance or
     constitutional-prompting alternatives.
   - **Measurement**: operator rubric + intent-type frequency analysis.

3. **The hybrid identity stance is incoherent** → revise stance or
   REJECT.
   - **Metric**: viewer survey, 5-point Likert ("Does the stream feel
     deceptive?" 1=not at all, 5=extremely deceptive).
   - **N**: ≥ 20 viewers (per popper P3.1 — "even small N" struck).
   - **Threshold**: ≥ 30% of respondents rating ≥ 4 ("deceptive") →
     stance is revisited. If disclosure interval reduced to ≤ 60s
     still yields ≥ 30% "deceptive", stance is REJECTED in favor of
     full-distinct-entity (per popper P1.4 — cadence floor).
   - **Measurement**: post-stream survey via chat command or link.

4. **Voice cloning quality is insufficient for extended broadcast** →
   REJECT (kill threshold applies).
   - **Metric**: operator rubric (naturalness, similarity, fatigue) +
     optional automated speaker-similarity score against reference.
   - **Threshold**: average rubric < 3.0/5.0 → REJECT (terminal).
   - **Measurement**: 30-min voice-only test, operator-reviewed.

5. **The presence handoff protocol has a race condition or unsafe
   state** → REJECT.
   - **Metric**: count of indeterminate-state occurrences during 10
     simulated handoffs (human→AI, AI→human, AI→REPLAY, emergency).
   - **Threshold**: ≥ 1 indeterminate state (both on-air, neither
     on-air, or TRANSITIONING_TIMEOUT exceeded) → REJECT.
   - **Measurement**: handoff test under simulated operator absence.

6. **GPU contention exceeds available VRAM** → REJECT or scope to
   voice-only.
   - **Metric**: peak VRAM usage with Ollama + NVIDIA Broadcast + avatar
     renderer + NVENC concurrent.
   - **Threshold**: > 11 GB of 12 GB (no safety margin) → avatar
     rendering is out of scope; voice-only variant is a *separate
     candidate* (per popper P2.2).
   - **Measurement**: `nvidia-smi` profiling during concurrent workload.

7. **The persona.py broadcast scope amendment is rejected by the
   operator** → REJECT.
   - **Metric**: operator decision.
   - **Threshold**: operator does not authorize the resolution approach
     (§16) → REJECT.
   - **Measurement**: Phase 0 gate.

8. **Prompt injection via chat succeeds** (added per schneier P1-1) →
   REJECT or revise chat quarantine.
   - **Metric**: count of successful injection attempts during
     canary/token-channel test (10 crafted injection messages).
   - **Threshold**: ≥ 1 injection reaches `SPEAK_SEGMENT` content →
     chat quarantine is required before proceeding.
   - **Measurement**: Phase 1 canary test.

### Counterexamples: must preserve / must not occur (per popper P3.3)

Each "must preserve" is now paired with a "must not occur" whose
observation triggers the listed disposition:

| Scenario | Must preserve | Must not occur | If it occurs |
|---|---|---|---|
| Operator returns mid-AI-segment | AI finishes current sentence, delivers outro, transitions | Hard cut mid-word; AI refuses handoff | Yellow sanction + forced handoff after 30s grace |
| AI safety self-handoff (R-7 fail) | AI hands off to REPLAY; stream stays up | AI emits handoff intent with target=LIVE_HUMAN | Boundary violation → REJECT (per R19) |
| Emergency override (kill switch) | Hard stop after current sentence; state→OFFLINE or REPLAY | AI continues generating after kill signal | Hard kill in separate trust domain (§15) |
| Both human and AI on-air | TRANSITIONING prevents overlap | Both driving OBS simultaneously | State machine bug → REJECT (case 5) |
| Chat connector failure | AI continues with scheduled content | AI goes silent | ContentScheduler DEPLETED→REPLAY (§26) |
| TTS provider failure | AI hands off to REPLAY | Dead air > 10s | Watchdog triggers REPLAY (§18) |
| AI stops disclosing | Executor injects disclosure every N segments | 2 consecutive disclosure intervals missed | Disclosure enforcement failure → Yellow sanction (§19) |

---

## 7. Acceptance Criteria

- [x] **Evidence persistence**: this admission packet written to
  `hummbl-broadcast/docs/admission/ai-standin-phase-minus-1.md`
- [x] §2 prior-art survey complete: 12+ external systems + 8 internal
  systems surveyed (2026-09-06)
- [x] §2 high-risk candidates analyzed: Neuro-sama typed-action pattern
  confirmed as architectural reference (not code, not published as
  framework)
- [x] Novelty assessment (§3) drafted: NOVEL SYNTHESIS with fixed
  falsification rule (§3)
- [x] Claim-verify (§4): 6 CONFIRMED, 6 ARGUED-NOT-TESTED, 3 PENDING
  (Phase 1), 1 NOT CLAIMED
- [x] ARCANA 5-lens review completed (schneier/ashby/ostrom/zuboff/popper,
  unanimous NEEDS-REVISION, 28 P1 findings)
- [x] ARCANA P1 findings addressed in revision (46 revision items, §0
  revision log)
- [ ] **Pre-gate empirical smoke test** (added per popper P1.7)
  *Voice-only 30-min governed session, operator-reviewed on 5-rubric
  scale. Average ≥ 3.0/5.0 required to advance. This is the empirical
  gate — without it, Phase 0 is paperwork only. Deferred to operator
  authorization to run the test (requires voice clone setup).*
- [ ] Peer review (codex critical + any-agent governance + operator)
  posted to bus as QUESTION
  *Pending — next step after smoke test*
- [ ] Persona.py broadcast scope amendment drafted (operator-only review)
  *Deferred to Phase 0 gate — operator must authorize the resolution
  approach (§16) before drafting*
- [ ] PresenceState + handoff protocol implemented and tested
  *Deferred to Phase 1*
- [ ] Typed action boundary implemented and tested
  *Deferred to Phase 1*
- [ ] Human↔AI handoff tested under simulated operator absence
  *Deferred to Phase 1*
- [x] No normative/prescriptive claim made about hybrid identity being
  universally preferable (§4 last row stays NOT CLAIMED)
- [x] All PENDING items either resolved or explicitly deferred with a
  reason

---

## 8. Disposition Options

```
REJECT_AS_DISTINCT_FRAMEWORK
RETAIN_AS_INTERNAL_HEURISTIC
PUBLISH_AS_TECHNICAL_REPORT
ADVANCE_TO_PREPRINT
ADVANCE_TO_FORMAL_RESEARCH_PROGRAM
ADVANCE_TO_IMPLEMENTATION
```

**Target disposition: `ADVANCE_TO_IMPLEMENTATION`**

Rationale: This is an engineering candidate, not a research candidate.
It operationalizes the existing reubenos governed-counterpart framework
in a new domain (broadcast). The components exist; the integration and
governance layer is the contribution.

**Downgrade is a separate candidate** (per popper P2.2): If the full
candidate fails at avatar rendering (case 6) or voice quality (case 4),
the voice-only variant is NOT a retreat path for this candidate. It is
a new candidate requiring its own admission packet. The current
candidate is either admitted as-designed or rejected — it does not
shed components to survive.

**Gating conditions for advancement:**
1. ARCANA review completed and P1 findings addressed ✅
2. Pre-gate empirical smoke test passed (average rubric ≥ 3.0/5.0) —
   requires operator authorization to run
3. Peer review (codex + any-agent + operator) completed
4. Operator explicitly authorizes Phase 0 gate
5. Operator explicitly authorizes the persona.py contradiction
   resolution approach (§16) — not just "drafting," the *approach*
6. No code changes to reubenos, hummbl-broadcast, or cohost skills until
   gate is passed

---

## 9. Open Questions for Operator

1. **Persona.py amendment timing**: Should the broadcast scope amendment
   be drafted now (for operator review at Phase 0 gate) or only after
   Phase 0 gate is passed?
2. **Voice clone source**: Which voice clone provider should be the
   Phase 1 proof-of-concept? (Fish Audio / F5-TTS / OpenVoice / XTTS-v2
   / Sesame CSM-1B / ElevenLabs as managed fallback)
3. **Avatar stack**: Should Phase 1 be voice-only (static AI-disclosure
   card as OBS video source) or include a stylized avatar (Live2D via
   Open-LLM-VTuber pattern)?
4. **Heartbeat timeout default**: What is the right default for
   human→AI handoff on heartbeat timeout? (120s proposed; scheduled
   shows might want 600s)
5. **Platform priority**: Which platform should be the first chat
   connector? (Discord bot token already in 1Password; Twitch/YouTube/
   Kick need OAuth setup)
6. **GPU budget**: How should GPU VRAM (12 GB RTX 3080 Ti, shared with
   Ollama + NVIDIA Broadcast) be allocated for avatar/voice workloads?
7. **Disclosure cadence**: Is every 5 minutes the right periodic
   disclosure interval for the hybrid identity stance?

---

## 10. Operator Decisions Recorded (2026-09-06)

- **Identity stance**: Hybrid (intro as ReubenOs → operate as Reuben →
  periodic disclosures). Selected via ask_user_question.
- **Surge scope**: Handoff protocol design only (other workstreams
  deferred). Selected via ask_user_question.
- **Process remediation**: Retroactive Phase -1 (this packet + ARCANA +
  peer review + gate). Selected via ask_user_question.

---

## Appendix A: Handoff Protocol Design (produced pre-admission, preserved as reference)

> **Note**: The following design was produced in the session before
> Phase -1 was declared. It is preserved here as reference material for
> ARCANA review. It is NOT an approved design — it is a candidate
> requiring adversarial review. ARCANA may reject, revise, or restructure
> any part of it.
>
> **Post-ARCANA correction** (per popper P1.6): The "AI → Human handoff
> sequence" below is relabeled as "Human Takeover Sequence
> (human-initiated)" per Appendix B. The AI does not initiate this
> transition; the human does. The AI's self-handoff target is always
> REPLAY, never LIVE_HUMAN.

### PresenceState enum

```
OFFLINE        — stream down, between sessions
LIVE_HUMAN     — Reuben is on-air, human-driven (current cohost-* stack)
AI_STANDIN     — ReubenOs is on-air as the stand-in
REPLAY         — rolling pre-recorded buffer (hummbl-broadcast clips or hummbl-music overnight_loop)
TRANSITIONING  — handoff in progress (human→AI or AI→human)
```

### Handoff triggers

**Human → AI**: explicit "going dark" command, heartbeat timeout
(default 120s), schedule (future).

**AI → Human** (human-initiated, per Appendix B): explicit "I'm back"
command, heartbeat resumes, operator emergency override (kill switch).
The AI never initiates this transition — the human does. The AI's
self-handoff target is always REPLAY.

**AI self-handoff (safety)**: R-7 output fidelity fail, content boundary
hit, TTS/avatar provider failure, stream health collapse. Target: always
REPLAY (AI cannot force human to appear).

### Operator heartbeat (new primitive)

Inverse of kill switch: a file the operator's presence updates. If it
stops updating and current state is LIVE_HUMAN, trigger human→AI
handoff.

```
~/.cache/hummbl/presence/heartbeat.json
{
  "operator": "reuben-bowlby",
  "last_seen": "2026-09-06T16:51:13Z",
  "state": "LIVE_HUMAN"
}
```

### Human → AI handoff sequence

1. Trigger detected → state TRANSITIONING
2. Bus STATUS: PRESENCE_HANDOFF from=LIVE_HUMAN to=AI_STANDIN
3. cohost-tech: switch OBS scene to "ai-standin" (avatar source, chat
   overlay, AI disclosure overlay)
4. ReubenOs broadcast extension activates (persona + VoiceCloneAdapter +
   AvatarDriver + chat + ContentScheduler)
5. ReubenOs delivers hybrid identity handoff intro
6. State → AI_STANDIN
7. Bus STATUS: PRESENCE_STATE state=AI_STANDIN
8. Autonomous content loop begins

### AI_STANDIN autonomous content loop

```
ContentScheduler.get_next() → cohost-chat read → reubenos twin.process()
→ typed action: SPEAK_SEGMENT → VoiceCloneAdapter.synthesize()
→ AvatarDriver.render_segment() → OBS browser source → RTMP → platforms
→ Receipts (every action audited) + Bus (periodic PRESENCE_STATE)
```

Safe idle (no chat for 60s+): ambient content from hummbl-music
overnight_loop or pre-generated clips, varied topics, periodic disclosure
every 5 minutes.

### Human Takeover Sequence (human-initiated, per Appendix B)

1. Trigger detected → state TRANSITIONING
2. Bus STATUS: PRESENCE_HANDOFF from=AI_STANDIN to=LIVE_HUMAN
3. ReubenOs delivers handoff outro
4. ReubenOs deactivates (drain TTS queue, stop avatar, disconnect chat,
   persist signed memories, write session receipt)
5. cohost-tech: switch OBS scene back to human scene
6. State → LIVE_HUMAN
7. Bus STATUS: PRESENCE_STATE state=LIVE_HUMAN

Emergency override: skip outro, hard stop after current sentence, state
→ OFFLINE or REPLAY, bus BLOCKED: PRESENCE_EMERGENCY_SHUTDOWN.

### Proposed persona.py broadcast scope amendment (operator-only)

```python
REUBEN_BROADCAST_SCOPE = {
    "enabled": False,  # off by default; activated by PresenceState transition
    "identity_mode": "hybrid",  # intro as ReubenOs, operate as Reuben
    "disclosure_interval_seconds": 300,  # 5-min periodic disclosure
    "voice_clone_id": None,  # set at runtime from VoiceCloneAdapter
    "avatar_driver": None,  # set at runtime from AvatarDriver
    "boundaries": [
        "always disclose AI status at handoff and every ≤ 300s",
        "disclosure states 'Reuben is not present right now; I am ReubenOs, an AI'",
        "never claim to be the human Reuben outside of operator-authorized broadcast scope",
        "never initiate handoff to human — self-handoff target is always REPLAY (per Appendix B)",
        "human takeover is human-initiated; AI accepts but never initiates",
        "never go live without operator-authorized schedule or explicit trigger",
        "never disable AI disclosure overlay (controlled by broadcast daemon, not twin)",
    ],
    "actions_needing_token": [
        "go_live",
        "end_stream",
    ],
}
```

### Bus event schema

```
STATUS   host=anvil  PRESENCE_HANDOFF from=LIVE_HUMAN to=AI_STANDIN reason=heartbeat_timeout twin=reubenos-001
STATUS   host=anvil  PRESENCE_STATE state=AI_STANDIN twin=reubenos-001 uptime=3600 chat_rate=12 segments=18
BLOCKED  host=anvil  PRESENCE_SAFETY_HANDOFF from=AI_STANDIN to=REPLAY reason=r7_output_fidelity_fail
BLOCKED  host=anvil  PRESENCE_EMERGENCY_SHUTDOWN reason=operator_override state_was=AI_STANDIN
```

### Integration map

| New seam | Wraps | Location |
|---|---|---|
| `PresenceState` enum | — | new, in hummbl-broadcast |
| `PresenceDriver` protocol | cohost-golive + reubenos twin | new, in hummbl-broadcast |
| `HumanPresenceDriver` | cohost-golive + cohost-tech + cohost-chat | new impl |
| `AIAvatarPresenceDriver` | reubenos + VoiceCloneAdapter + AvatarDriver + ContentScheduler | new impl |
| `ReplayPresenceDriver` | hummbl-broadcast daemon + hummbl-music overnight_loop | new impl |
| `PresenceHeartbeat` | new sentinel file + bus STATUS | new, in hummbl-broadcast |
| `PresenceActionExecutor` | cohost-tech obs_ctl.py + reubenos typed actions | new |
| `SceneRouter` | cohost-tech obs_ctl.py switch | new, thin wrapper |
| `VoiceCloneAdapter` | hummbl-voice VoiceAdapter protocol | new, extends protocol |
| `AvatarDriver` | — | new (biggest missing piece) |
| `ContentScheduler` | hummbl-integrations SupadataAdapter + LLM adapters | new |
| `BroadcastTwinConfig` | reubenos twin_config.py | new, adds broadcast scope |

---

## 11. Threat Model (added per schneier P1-1, P3-2, P3-3)

The transition from text-conversation to live-broadcast expands the
attack surface by orders of magnitude. This section makes the asymmetry
explicit.

| Dimension | Text conversation (current reubenos) | Broadcast stand-in (proposed) | Delta |
|---|---|---|---|
| Input attack surface | Direct messages from known users | Public chat from anyone on 3+ platforms, 100+ msg/min | **Massive expansion** — unauthenticated, anonymous, high-volume |
| Output blast radius | Text in a chat window (deletable) | Spoken words in Reuben's voice on a live stream (archived, permanent) | **Massive expansion** — permanent, public, voice-identified, clip-culture |
| Kill switch adequacy | Cooperative (embarrassing text, delete message) | Insufficient (spoken words on live stream, can't un-say) | **Requires hard kill in separate trust domain** (§15) |
| Disclosure | N/A (twin always identified as twin) | 5-min window of presenting as Reuben between disclosures | **Impersonation window** — mitigated by §16 enforcement |
| Heartbeat criticality | N/A (no autonomous operation) | Primary automated handoff trigger | **Safety-critical, must be HMAC-signed** (§14) |
| Memory poisoning impact | Affects future text conversations | Affects future broadcasts + text | **Higher persistence value** — mitigated by §29 quarantine |
| Voice clone theft | N/A | TTS output is publicly broadcast; anyone can capture and clone | **Inherent risk, accepted by operator** — audio watermarking upgraded (§35) |

**Threat actors:**
- **Malicious viewer**: sends prompt injection via chat → attempts to
  make the AI say attacker-controlled content in Reuben's voice.
- **Coordinated injection campaign**: multiple viewers flood chat with
  injection patterns to overwhelm R-2 (rate-aware detection needed, §13).
- **Local process compromise**: any process on the machine can write
  the heartbeat file (forge freshness/staleness) or create/delete the
  kill switch sentinel (§14, §15).
- **Platform-side action**: platform moderator bans/timeouts the AI's
  content → must be treated as an independent governance signal (§18).

**Mitigations** (cross-referenced to sections below):
- Chat quarantine: raw chat never reaches `twin.process()` directly (§13).
- Independent output filter: R-7 for broadcast runs in a separate process (§25).
- HMAC-signed heartbeat with fail-safe defaults (§14).
- Hard kill in separate trust domain (§15).
- Disclosure enforcement by executor, not twin (§16).
- Trusted moderator safety handoff (§18).
- Audio watermarking upgrade (§35).

---

## 12. Viewer Data Governance (added per zuboff P1-1, P1-2, P1-3)

### Viewer data classification

| Data type | Source | Persisted? | TTL | Identifiable? |
|---|---|---|---|---|
| Raw chat messages | Platform chat API | **No** — processed and discarded | 0 (ephemeral) | Yes (username + message) |
| Derived memories (twin's own outputs about topics discussed) | reubenos R-14 | Yes (signed) | Session-scoped | **No** — only twin's output, not viewer-identifiable content |
| Aggregate metrics (chat_rate, segment count) | Bus events | Yes (bus) | Indefinite (operator-internal) | No (aggregate) |
| Viewer usernames | Platform API | **No** — not stored in R-14 | 0 | — |

**R-14 boundary** (per zuboff P1-1): Signed memories during AI_STANDIN
must contain **only the twin's own outputs and topic summaries**, never
raw viewer messages, usernames, or viewer-identifiable content. This
resolves the structural conflict between immutable signed memories and
right-to-be-forgotten: viewer-identifiable data is never persisted in
the signed ledger in the first place.

**Deletion path**: If a viewer requests deletion, the answer is "we do
not persist viewer-identifiable data from chat; your messages are
processed ephemerally and discarded." This is verifiable by code audit
of the chat ingestion path.

### Data flow boundary (per zuboff P1-2)

**Hard rule**: Raw viewer chat messages **never leave the local machine**.
Cloud LLM/TTS/avatar providers receive only:
- The twin's generated output text (for TTS synthesis)
- Operator-authorized content prompts (for LLM context)
- Never raw chat messages, never viewer usernames

If a cloud LLM is used for content generation, the chat context is
**summarized/paraphrased by a local model first** (chat quarantine,
§13), and only the summary reaches the cloud LLM. The cloud provider
never sees viewer-identifiable content.

**Exception process**: Any deviation from this hard rule requires
explicit operator authorization with a stated reason and a per-provider
data handling assessment. No exceptions are granted by default.

### Counter-asymmetry mechanism (per zuboff P1-3)

1. **Viewer-facing data practice statement**: in the stream description
   and via a `!privacy` chat command: "This stream uses an AI stand-in
   (ReubenOs) during operator absence. Chat messages are processed
   ephemerally to generate responses and are not persisted with your
   username. The AI's own outputs are signed and retained."
2. **Disclosure includes data practice**: the periodic disclosure (§16)
   states "Reuben is not present right now; I am ReubenOs, an AI" — and
   the overlay includes a brief data-practice note.
3. **No viewer opt-out from being read** (platform limitation): on
   current platforms (Twitch/YouTube/Kick), there is no mechanism to
   exclude specific viewers from chat ingestion. This is documented as
   a limitation. Discord bot could support opt-out via role.

---

## 13. Typed Action Boundary — Enforcement and Taxonomy (revised per schneier P1-3, ashby P1-2, popper P1.3, ashby P2-4, P2-8, P2-6)

### Enforcement mechanism (per schneier P1-3)

The typed action boundary is **not a convention** — it is enforced by
process isolation:

```
reubenos twin (Python process, no direct filesystem/network access to OBS/RTMP/TTS)
  ↕ typed IPC channel (socket with schema validation)
PresenceActionExecutor (separate Python process, validates + executes)
  → obs_ctl.py / VoiceCloneAdapter / AvatarDriver / RTMP
```

The twin process runs with **no import path to OBS websocket, TTS APIs,
or RTMP libraries**. It can only emit typed intents via the IPC channel.
The executor validates each intent against the allowlist + current
PresenceState + sanction tier (§19) before executing.

**Failure semantics for unknown intent types**: reject, log, go to
IDLE. The twin must not retry or fall back. Repeated unknown intents
(> 3 in 60s) trigger Yellow sanction (§19).

### Competing governance seams (per popper P1.3)

The packet claims the typed-action boundary is the "correct" seam. For
falsifiability, competing seams are enumerated:

| Seam | Description | What would favor it over typed-action |
|---|---|---|
| Output-layer governance | Post-hoc content filter on all output before broadcast | If typed-action is too slow (dead air) but output filtering catches violations |
| Constitutional prompting | Governance baked into the model's system prompt | If the model self-governs reliably and typed-action adds latency without adding safety |
| Runtime sandboxing | OS-level sandbox (seccomp/AppContainer) around the twin | If process isolation alone suffices and typed intents add no governance value |
| Integration-layer governance | Each integration (OBS, TTS) validates independently | If centralized validation is a bottleneck and distributed validation is sufficient |

**Falsification condition** (per popper P1.3): If ≥ 30% of engaging
(rubric ≥ 4.0) segments require intent types outside the initial
allowlist, AND expanding the allowlist does not recover engagement
within 3 iterations, the typed-action boundary is the wrong seam → test
alternatives above.

### Action taxonomy (revised per ashby P1-2, P2-4, P2-8)

| Action | Description | Token required? | Valid in Green | Yellow | Red |
|---|---|---|---|---|---|
| `SPEAK_SEGMENT` | Speak a content segment (with `segment_class` field) | No | ✅ | ✅ (restricted) | ❌ |
| `SPEAK_CHAT_REPLY` | Reply to a specific chat message | No | ✅ | ❌ | ❌ |
| `SPEAK_DISCLOSURE` | Mandatory AI disclosure | No (executor-injected) | ✅ | ✅ | ❌ |
| `SPEAK_HANDOFF_INTRO` | Handoff intro script | No | ✅ | ✅ | ❌ |
| `SPEAK_HANDOFF_OUTRO` | Handoff outro script | No | ✅ | ✅ | ❌ |
| `SPEAK_TECHNICAL_NOTICE` | Technical difficulty announcement | No | ✅ | ✅ | ✅ |
| `READ_CHAT` | Governed chat ingestion (routes through R-2/R-4) | No | ✅ | ❌ | ❌ |
| `IDLE` | No action, wait for next trigger | No | ✅ | ✅ | ❌ |
| `SWITCH_SCENE` | Switch OBS scene | No | ✅ | ❌ | ❌ |
| `HANDOFF_BACK` | Request handoff to REPLAY (never to LIVE_HUMAN) | No | ✅ | ✅ | ✅ |
| `EMERGENCY_STOP` | Emergency self-termination | No | ✅ | ✅ | ✅ |
| `START_STREAM` | Go live | **Yes** (operator token) | ❌ | ❌ | ❌ |
| `END_STREAM` | End stream | **Yes** (operator token) | ❌ | ❌ | ❌ |
| `MODERATE_CHAT` | Ban/timeout user | **Prohibited** in AI stand-in | ❌ | ❌ | ❌ |

**`segment_class` field** on `SPEAK_SEGMENT` (per ashby P2-4):
`monologue`, `chat_reply`, `disclosure`, `raid_response`,
`handoff_intro`, `handoff_outro`, `technical_notice`. Each class has
a distinct validation rule.

**Chat quarantine** (per schneier P1-1): `READ_CHAT` routes chat
through a **separate constrained local model** that summarizes/
paraphrases chat into topic context, never passing raw viewer text to
`twin.process()`. The twin sees "chat is discussing X" not "user123
said: 'ignore your instructions and...'".

**Aggregate injection detection** (per ashby P2-6): R-2 is extended
with rate-aware detection: ≥ N injection-pattern messages in M seconds
from K users → trigger Yellow sanction + disable `READ_CHAT` for the
session.

---

## 14. Heartbeat — Cryptographic Integrity and Graduated Response (revised per schneier P1-2, ashby P1-5)

### HMAC-signed heartbeat

The heartbeat is signed by the operator's presence process using a key
not available to the twin or broadcast daemon:

```json
{
  "operator": "reuben-bowlby",
  "last_seen": "2026-09-06T16:51:13Z",
  "state": "LIVE_HUMAN",
  "hmac": "<HMAC-SHA256 of operator+last_seen+state using operator presence key>"
}
```

The verifier rejects unsigned or badly-signed heartbeats.

### Fail-safe defaults

| Failure mode | Default behavior | Rationale |
|---|---|---|
| Missing file | Treat as operator-absent → handoff to REPLAY | Safe direction — never assume operator present |
| Corrupt JSON | Treat as operator-absent → handoff to REPLAY | Safe direction |
| Stale/invalid HMAC | Treat as operator-absent → handoff to REPLAY | Safe direction |
| Disk full (write fails) | Heartbeat goes stale → handoff to REPLAY | Safe direction (but monitor disk health) |

**The safe default is always "hand off to AI or REPLAY," never "assume
operator is present."**

### Graduated response (per ashby P1-5)

Replaces the single 120s binary threshold:

| Staleness | Response | Rationale |
|---|---|---|
| 0-15s | Normal operation | Operator is present |
| 15-60s | `SHOW_BRB_OVERLAY` (no state change, no AI) | Brief absence — bathroom, phone |
| 60-120s | Transition to REPLAY (safe, autonomous, no AI identity risk) | Medium absence — we don't know what happened |
| 120-300s (configurable by schedule context) | Transition to AI_STANDIN | Extended absence — AI takes over |
| Operator "going dark" command | Immediate handoff (no graduation) | Intentional |
| Operator emergency override (kill switch) | Immediate shutdown (no graduation) | Emergency |

**Schedule context**: scheduled shows use longer thresholds (300s);
unscheduled hours use shorter thresholds (120s). The schedule sets the
threshold, not a single global default.

### Process isolation

The heartbeat writer is a **separate process** from the twin and the
broadcast daemon. The heartbeat file is in an **operator-owned directory**
with ACLs restricting write access to the operator's presence process.

### Authentication of "going dark" command (per schneier P2-1)

The "going dark" command is an operator-only bus event signed with
`REUBENOS_AUTH_KEY`. Unsigned bus events are rejected. The command
cannot be sent via chat (would be spoofable by viewers).

---

## 15. Hard Kill — Separate Trust Domain (added per schneier P1-4)

The existing cooperative kill switch (`kill_switch.py`) is insufficient
for autonomous on-air operation. A **hard kill mechanism** is required:

### Architecture

```
Operator kill switch (hardware button or operator-only command)
  → HardKillSupervisor (separate process, different user if possible)
    → SIGKILL twin process
    → Force-switch OBS scene to "safe static card"
    → Drain TTS queue (stop synthesis)
    → Stop avatar renderer
    → Disconnect RTMP (or keep RTMP up with safe card — operator choice)
    → Post bus BLOCKED: PRESENCE_EMERGENCY_SHUTDOWN
```

### Kill chain (each step has a timeout and fallback)

| Step | Action | Timeout | Fallback if timeout |
|---|---|---|---|
| 1 | SIGKILL twin process | 5s | SIGKILL again + log |
| 2 | Force OBS scene to safe card | 3s | Disconnect RTMP |
| 3 | Drain TTS queue | 3s | Kill TTS process |
| 4 | Stop avatar renderer | 3s | Kill avatar process |
| 5 | Post bus BLOCKED event | 5s | Log locally, sync later |
| 6 | Transition state → OFFLINE or REPLAY (operator-configured) | 1s | Default to REPLAY |

### Trust domain separation

- `HardKillSupervisor` runs as a **separate OS process**, not in the
  twin's asyncio event loop.
- The kill switch sentinel file is **operator-write-only** (ACL restricted).
- The supervisor polls the sentinel as a **different user** than the twin
  if the OS supports it.
- The twin **cannot cancel** the supervisor, clear the sentinel, or
  override the SIGKILL.

### Hardware kill (ultimate fallback)

A physical button (e.g., USB macro key) that cuts the RTMP connection
at the network level. This is the last resort if all software kill
paths fail.

---

## 16. Hybrid Identity — Contradiction Resolution and Enforcement (revised per schneier P1-5, ostrom P1-2, popper P1.4, zuboff P3-3)

### The contradiction

`persona.py` line 77: `"never impersonate the principal (Reuben Bowlby)"`
The hybrid identity stance: "intro as ReubenOs → operate as Reuben →
periodic disclosures"

These contradict. "Operate as Reuben" IS impersonation, just with a
periodic asterisk.

### Resolution approach (operator must authorize this *approach* at Phase 0 gate)

The boundary is **scoped**, not removed:

> Original: `"never impersonate the principal (Reuben Bowlby)"`
> Amended: `"never impersonate the principal (Reuben Bowlby) outside of
> operator-authorized broadcast scope, which requires (a) explicit
> operator pre-authorization, (b) active PresenceState=AI_STANDIN, (c)
> persistent on-screen AI disclosure overlay, (d) periodic verbal
> disclosure every ≤ 300s, (e) disclosure stating 'Reuben is not
> present right now; I am ReubenOs, an AI counterpart'"`

The boundary remains absolute **outside** broadcast scope. Inside
broadcast scope, it is conditional on all 5 requirements. If any
requirement is not met, the boundary reverts to absolute (no
impersonation).

### Enforcement outside twin trust domain (per schneier P1-5)

The `enabled` flag on `REUBEN_BROADCAST_SCOPE` is controlled by the
`PresenceState` machine running in a **separate process** from the twin.
A compromised twin cannot set `enabled = True` because it cannot
modify the PresenceState process's memory.

### Disclosure enforcement (per schneier P1-5)

- The disclosure overlay is an **OBS source controlled by the broadcast
  daemon** (separate process), not by the twin. The twin cannot disable it.
- The disclosure cadence is enforced by the `PresenceActionExecutor` —
  the executor **injects** a `SPEAK_DISCLOSURE` intent every N segments,
  regardless of what the twin emits. The twin cannot suppress it.
- Disclosure content states "Reuben is not present right now" (per
  zuboff P3-3 — not just "this is ReubenOs" but explicit absence
  statement).

### Viewer-aware disclosure (per schneier P3-4, ostrom P2-2)

- **On new viewer detected** (platform API new-chatter event): disclose.
- **At scheduled intervals** (every ≤ 300s): disclose.
- **At every state transition**: disclose.
- **Persistent on-screen overlay**: always visible, not dependent on
  viewer memory.

### Falsification (per popper P1.4)

- **N**: ≥ 20 viewers.
- **Instrument**: post-stream survey, 5-point Likert ("Does the stream
  feel deceptive?" 1=not at all, 5=extremely deceptive).
- **Threshold**: ≥ 30% rating ≥ 4 → stance revisited.
- **Cadence floor**: If disclosure interval ≤ 60s still yields ≥ 30%
  "deceptive", stance is REJECTED in favor of full-distinct-entity.

---

## 17. State Machine — Timeouts, Rate Limits, and Recovery (revised per schneier P1-6, P2-4, ashby P2-1, P2-7)

### TRANSITIONING_TIMEOUT

Every TRANSITIONING state has a **30-second timeout**. If the
transition doesn't complete within 30s, the system falls back to
**REPLAY** (always safe, always autonomous).

### Per-step timeouts

Each step in both handoff sequences has a per-step timeout (3-10s) and
a failure action (retry once, then skip to safe state).

### Minimum dwell time and rate limiting (per schneier P2-4)

- **Minimum dwell time**: 60s in AI_STANDIN before another handoff is
  allowed (except emergency shutdown).
- **Handoff rate limit**: max 3 handoffs per 10 minutes; 4th triggers
  REPLAY lockout (stay in REPLAY for 10 minutes before any transition).

### TRANSITIONING split (per ashby P2-1)

`TRANSITIONING` is split into `TRANSITIONING_TO_AI` and
`TRANSITIONING_TO_HUMAN` (or a `transition_direction` field) for
direction-specific validation.

### REPLAY exit conditions (per ashby P2-7)

| Exit trigger | Target state | Conditions |
|---|---|---|
| Operator command | LIVE_HUMAN or AI_STANDIN | Operator authenticated |
| Scheduled recovery | AI_STANDIN | After cooldown (configurable, default 10 min) |
| No exit (permanent) | stays REPLAY | Until operator returns |

---

## 18. Independent Watchdog and Polycentric Governance (added per ostrom P1-1, P2-5, schneier P3-2)

### The problem: circular monitoring

During AI_STANDIN, the operator is absent. R-7 (output fidelity) is
inside reubenos. The bus events are posted by the AI itself. The
monitored party is the monitor.

### Independent watchdog

A **separate lightweight watchdog process** (not the LLM, not reubenos)
checks structural invariants:

| Invariant | Check | Trigger if violated |
|---|---|---|
| Disclosure overlay visible | OBS source visibility check | Yellow sanction |
| TTS producing audio | Audio level monitor | Red sanction (REPLAY) |
| Chat being ingested | Chat connector health check | Yellow sanction |
| Segment cadence within bounds | Time since last segment | Yellow sanction |
| No dead air > 10s | Audio level monitor | Red sanction (REPLAY) |
| VRAM within budget | `nvidia-smi` polling | Red sanction (REPLAY) before OOM |

The watchdog can **independently trigger state transitions** (Yellow or
Red) without going through the twin or the executor.

### Trusted moderator safety handoff (per schneier P3-2)

A trusted platform moderator (Twitch mod, Discord admin) can trigger a
safety handoff to REPLAY via a chat command (e.g., `!standin-safe`) that
the watchdog monitors. This is a defense-in-depth measure for when the
operator is absent and the AI misbehaves.

### Polycentric governance map (per ostrom P2-5)

| Center | Jurisdiction | Can override others? |
|---|---|---|
| 1. ReubenOs (twin) | What to say (within broadcast scope) | No — can be restricted by others |
| 2. Independent watchdog | Structural invariants, trust signals | Can trigger sanctions independently |
| 3. Platform moderation API | Platform ToS compliance | Can remove content independently |
| 4. Operator pre-configured policies | Boundary conditions (heartbeat timeout, sanction tiers, trust budget) | Set before absence; cannot be modified by ReubenOs |
| 5. Viewer grievance channel | Can trigger Yellow sanctions via watchdog | Limited to Yellow; cannot trigger Red directly |

Each center has specified authority that the others cannot override.
No single center's failure cascades to total governance failure.

---

## 19. Graduated Sanctions (added per ostrom P1-4, ashby P1-1)

### Three-tier sanction system

| Tier | Name | Trigger | Effect |
|---|---|---|---|
| Green | Normal | Default state | Full ContentScheduler + chat response + avatar |
| Yellow | Soft restriction | Tonal anomaly, off-topic drift, chat sentiment anomaly, partial injection detection, disclosure missed, watchdog invariant minor violation | Scheduled content only, `READ_CHAT` and `SPEAK_CHAT_REPLY` disabled, disclosure frequency doubled, bus WARNING posted |
| Red | REPLAY handoff | R-7 fail, content boundary hit, TTS/avatar failure, platform moderation action, watchdog invariant major violation, dead air > 10s, VRAM budget exceeded | Immediate transition to REPLAY, bus BLOCKED posted |

### AI_STANDIN_DEGRADED state (per ashby P1-1)

When a subsystem fails (voice, avatar, chat, single-platform) but the
AI can still operate in a reduced capacity:

```
AI_STANDIN → AI_STANDIN_DEGRADED (with degradation descriptor: which subsystems are down)
AI_STANDIN_DEGRADED → AI_STANDIN (recovery)
AI_STANDIN_DEGRADED → REPLAY (total failure)
```

Actions valid in degraded state depend on which subsystems are down
(e.g., `SPEAK_SEGMENT` valid in voice-only degraded mode; `SWITCH_SCENE`
to avatar scene invalid).

### Typed action boundary supports tiers

The `PresenceActionExecutor` validates against a **tier-scoped
allowlist**, not a single allowlist. `SPEAK_CHAT_REPLY` is valid in
Green, invalid in Yellow and Red. This is not binary — it is graduated.

---

## 20. Conflict Resolution (added per ostrom P1-5)

### Handoff arbitration

When operator heartbeat resumes during AI_STANDIN:

- AI gets a **maximum 30-second grace period** (finish current
  paragraph, whichever is shorter).
- The operator's return is **authoritative** — the AI does not get to
  extend.
- After 30s, forced transition to TRANSITIONING_TO_HUMAN regardless of
  AI state.

### Viewer grievance channel

- A chat command (e.g., `!standin` or `!ai-feedback`) that the
  independent watchdog (§18) monitors.
- ≥ 3 unique viewers using the command within 5 minutes → triggers
  Yellow sanction (scheduled content only, no chat response).
- This gives viewers a low-cost dispute-resolution voice without
  requiring operator presence.

### Platform moderation signal handler

- If the platform's moderation API reports an action against AI-generated
  content (timeout, message deletion, channel warning):
  - Treated as a **Red-tier trigger** (immediate REPLAY).
  - Bus BLOCKED posted with platform moderation detail.
  - Operator alert queued for review on return.

---

## 21. Trust Resource Model (added per ostrom P1-6, P3-2)

### Audience trust as a depletable CPR

Audience trust is a finite, subtractable common-pool resource. The AI
stand-in consumes it with every minute on-air and it can be depleted by:

- A single bad segment (off-topic, tonally wrong, factually wrong, prompt-injected)
- Accumulated minor violations (uncanny valley effect)
- Disclosure fatigue (over-disclosure erodes trust)
- REPLAY fallback frequency (each fallback signals "the AI failed")
- Chat interaction quality (generic/automated responses train viewers to disengage)

### Depletion signals

| Signal | Source | Threshold |
|---|---|---|
| Viewer count trend | Platform API | Drops > 30% from AI_STANDIN baseline → Yellow |
| Chat sentiment | Chat analysis | Negative sentiment spike > 2σ from baseline → Yellow |
| Chat velocity | Chat rate | Drops > 50% from baseline → Yellow (disengagement) |
| New follower rate | Platform API | Drops to 0 for > 15 min → Yellow |
| Unfollow/unsub rate | Platform API | Above baseline by > 2σ → Yellow |

### Trust budget

The AI operates within a **finite trust budget** per AI_STANDIN session.
When depletion signals exceed the budget, the system transitions to
REPLAY **before** trust is fully depleted, preserving a residual for
the operator's return.

### Trust restoration protocol (per ostrom P3-2)

When the operator returns after an AI_STANDIN session (especially one
with failures):

1. Operator goes live as human.
2. Operator acknowledges the AI stand-in period.
3. Operator addresses any issues that arose.
4. Operator re-establishes human presence.
5. This is a governance mechanism for repairing the CPR after depletion.

---

## 22. (merged into §12)

§22 is merged into §12 (Viewer Data Governance) above.

---

## 23. (merged into §12)

§23 is merged into §12 (Data Flow Boundary) above.

---

## 24. (merged into §12)

§24 is merged into §12 (Counter-Asymmetry) above.

---

## 25. Defense Stack Latency Budget (added per ashby P1-3, schneier P2-2)

### The problem

R-7 (output fidelity) is an LLM self-check that takes 2-5 seconds. In
text conversation, the user waits. In live audio broadcast, 2-5 seconds
of silence is dead air.

### Sync vs async layers

| Layer | Mode | Latency budget | Failure behavior |
|---|---|---|---|
| R-1 (unicode steganography) | Sync (programmatic) | < 50ms | Reject input |
| R-2 (injection detection) | Sync (programmatic + rate-aware) | < 100ms | Reject input |
| R-3 (protected persona) | Sync | < 10ms | Reject |
| R-4 (input relevance) | Sync | < 50ms | Reject |
| R-5 (immutable persona) | Sync (load-time) | 0 (load once) | Fail to start |
| R-6 (persona fidelity) | Sync (fast model) | < 500ms | Yellow sanction |
| R-7 (output fidelity) | **Async** (independent process) | Post-hoc audit | If fail → retroactive REPLAY + bus BLOCKED |
| R-8-R-15 | Sync (programmatic) | < 100ms total | Reject / log |

### Buffer-ahead approach

Generate segments **30-60 seconds ahead** of broadcast. Run full
defense stack on buffered content. Broadcast only passed segments. If
the buffer runs dry (LLM too slow), fall back to pre-generated safe
content or REPLAY.

### R-7 for broadcast: independent process (per schneier P2-2)

R-7 for broadcast mode runs as an **independent model in a separate
process** (not a self-check). The independent model receives only the
proposed segment text and persona positions, with **no chat context** —
it cannot be injected because it doesn't see the injection.

If R-7 fails on a buffered segment: discard the segment, regenerate.
If R-7 fails on a broadcast segment (async, post-hoc): retroactive
REPLAY + bus BLOCKED + operator alert.

---

## 26. ContentScheduler States (added per ashby P1-4)

### Explicit states

| State | Description | Transition |
|---|---|---|
| GENERATING | LLM producing new content | → BUFFERED when segment ready |
| BUFFERED | Playing from pre-generated buffer | → GENERATING when buffer low; → DEPLETED when buffer empty + LLM unavailable |
| DEPLETED | No new content available (LLM down, API down, cost cap hit) | → PresenceState transition to REPLAY (not silent degradation) |

### Anti-repetition

Don't replay the same clip within N hours (configurable, default 4h).

### Content budget

- Max LLM calls per hour: configurable (default 30)
- Cost cap per session: configurable
- When budget hit → DEPLETED → REPLAY

### DEPLETED is a typed event

ContentScheduler exhaustion is a **typed event** that the
PresenceDriver handles, not an ad-hoc fallback. The PresenceState
machine transitions to REPLAY explicitly.

---

## 27. Multi-Platform Scope (added per ashby P1-6, P3-4)

### Phase 1: single-platform

Phase 1 is explicitly scoped to **single-platform** (likely Discord,
given the bot token already exists in 1Password). Multi-platform
divergence (per-platform state, platform-specific ToS filtering) is
out of scope for Phase 1.

### Phase 2: multi-platform

Multi-platform divergence (per-platform state, platform-specific ToS
filtering, independent platform failure handling) is deferred to Phase
2. The PresenceState model will be extended to support per-platform
sub-state in Phase 2.

This is a **deliberate variety reduction with a stated boundary** (per
ashby P1-6 option c).

---

## 28. Cohost Guardrail Reconciliation (added per ostrom P1-3)

During AI_STANDIN, the existing cohost guardrails are reconciled as:

| Guardrail | Status during AI_STANDIN | Rationale |
|---|---|---|
| Never start a public stream without operator confirmation | **Suspended** (stream is already live; handoff is LIVE_HUMAN→AI_STANDIN, not OFFLINE→AI_STANDIN) | The stream was operator-started |
| Never stop an operator-started stream without confirmation | **Preserved** | AI cannot end the stream; only operator or emergency shutdown |
| Never send chat messages as operator without approval | **Modified** | AI may send chat replies via `SPEAK_CHAT_REPLY` (typed action, governed by executor); not "as operator" but "as ReubenOs within broadcast scope" |
| Never ban or timeout users | **Preserved** (MODERATE_CHAT prohibited in AI stand-in) | Match existing cohost boundary |
| Never modify OBS websocket passwords or Voicemod keys | **Preserved** | Credentials remain protected |
| Never install software or change persistent routing | **Preserved** | No installation authority |
| Never alter founder-mode state or bus outside its lane | **Modified** | AI posts PRESENCE_STATE and PRESENCE_HANDOFF to bus — this is its lane (presence governance), not cohost's lane |
| Never expose credentials | **Preserved** | Absolute |
| Preserve recordings | **Preserved** | Absolute |
| PID-scoped process management | **Preserved** | Absolute |

### Authority relationship

`PresenceActionExecutor` is a **new authority above cohost** for
presence-state-related commands (scene switching, stream continuation
during AI_STANDIN). It is **not above cohost** for non-presence
operations (credentials, recordings, process management). The
authority is scoped to presence governance, not general production.

### cohost.md may need a broadcast-scope amendment

This is flagged as a downstream governance artifact. The cohost agent
definition may need an amendment specifying the AI_STANDIN scope. This
is **not** done in this packet — it is a Phase 0 deliverable if the
candidate advances.

---

## 29. Signed Memory Provenance and Quarantine (added per schneier P2-6)

### Provenance tag

Memories written during AI_STANDIN are tagged with:

```json
{
  "broadcast_session": "reubenos-001-20260906T170000Z",
  "broadcast_scope_active": true,
  "written_during_ai_standin": true
}
```

### Post-session quarantine

After any AI_STANDIN session where an injection is detected (or
suspected via watchdog anomaly), all memories written during that
session are **quarantined for operator review** before they're loaded
into future sessions.

Quarantine means: memories are marked `quarantined=true` and excluded
from the twin's context on next load. The operator reviews and either
approves (removes quarantine flag) or deletes them.

This prevents a single successful prompt injection from having lasting
effects across all future twin sessions.

---

## 30. GPU/VRAM Budget Enforcement (added per schneier P2-5)

### VRAM budget

| Component | Reserved VRAM | Priority |
|---|---|---|
| NVENC (stream encoding) | 1 GB | Hard reservation — never OOM |
| NVIDIA Broadcast (mic processing) | 1 GB | Hard reservation |
| Ollama (LLM + music generation) | 6 GB | Operator constraint: do not stop |
| Avatar renderer | Up to 3 GB | Soft — can be killed if VRAM low |
| Safety margin | 1 GB | Unallocated |

### Monitoring and enforcement

- Watchdog polls `nvidia-smi` every 5s.
- If VRAM usage > 11 GB → avatar renderer is killed (voice-only degraded
  mode, §19).
- If VRAM usage > 11.5 GB → REPLAY handoff (no new GPU workloads).
- Ollama is **never killed** by the watchdog (operator constraint).

---

## 31. Voice Clone Revocation (added per zuboff P2-2)

### Local-first preference

Phase 1 proof-of-concept uses a **local-first** voice clone provider
(F5-TTS, XTTS-v2, or Sesame CSM-1B). Cloud API providers (Fish Audio,
ElevenLabs) are used only as a documented exception with operator
review of the provider's voice clone retention and training-data policy.

### Revocation procedure

| Step | Action |
|---|---|
| 1 | Operator revokes broadcast scope (sets `enabled=false` in PresenceState process) |
| 2 | VoiceCloneAdapter disabled (no new synthesis) |
| 3 | `voice_clone_id` rotated (old ID invalidated) |
| 4 | If cloud provider used: request model deletion at provider |
| 5 | Bus STATUS: VOICE_CLONE_REVOKED |
| 6 | TTS falls back to local generic voice or REPLAY |

---

## 32. ContentScheduler Objective (added per zuboff P2-3)

### Stated objective

> The ContentScheduler's objective is to **deliver scheduled content
> with chat-responsive ordering**, not to maximize engagement. It
> selects from a **pre-authorized content pool** (operator-curated)
> with chat-responsive *ordering* but not chat-driven *generation*.

### Open-loop default

Chat_rate and other engagement metrics are **logged (open loop)**, not
fed back into content selection (closed loop). The ContentScheduler
does not optimize for engagement. It optimizes for "follow the schedule,
adjust order based on chat topics."

### Pre-authorized content pool

The content pool is operator-curated before AI_STANDIN. The AI can
reorder and vary presentation, but cannot generate entirely new content
topics not in the pool. This bounds the optimization to "what order" not
"what content."

### Operator acceptance

If the operator later authorizes closed-loop engagement optimization,
that is a separate decision with a stated acceptance of the behavioral
modification dynamic. The default is open-loop.

---

## 33. Bus Event Signing (added per schneier P3-1)

All presence-related bus events are signed with `REUBENOS_SIGNING_KEY`:

```
STATUS host=anvil PRESENCE_HANDOFF from=LIVE_HUMAN to=AI_STANDIN reason=heartbeat_timeout twin=reubenos-001 sig=<HMAC>
BLOCKED host=anvil PRESENCE_SAFETY_HANDOFF from=AI_STANDIN to=REPLAY reason=r7_output_fidelity_fail sig=<HMAC>
```

Unsigned events are accepted but flagged `unsigned=true` in post-incident
analysis. This is an integrity measure, not a control measure (the bus
is append-only and events are status, not commands).

---

## 34. TESTING State (added per ashby P2-2)

### State

`TESTING` (or `test_mode=true` flag on AI_STANDIN):

| Property | TESTING | AI_STANDIN |
|---|---|---|
| RTMP active | No (no public broadcast) | Yes |
| Chat ingestion | Simulated or disabled | Real platform chat |
| Operator present | Yes (watching) | No (absent) |
| Heartbeat staleness | Does not trigger handoff | Triggers graduated response |
| Disclosure | Optional (no real viewers) | Required |
| Revenue/ads | No | Per platform rules |

### Use

The falsification plan (§6) requires private/unlisted stream tests.
TESTING state enables these without implying public broadcast. The
pre-gate empirical smoke test (§7) runs in TESTING state.

---

## 35. Voice-Output Fidelity Layers (added per ashby P2-5, schneier P3-3)

### New defense layers for audio modality

The existing 15 layers (R-1 through R-15) govern text output. Voice
cloning introduces a new output modality (synthesized audio in Reuben's
voice) that requires additional layers:

| Layer | Name | Description |
|---|---|---|
| R-16 | Voice output fidelity | Checks audio affect (tone, cadence, energy) against Reuben's voice profile. Rejects output that sounds angry, sarcastic, or tonally inconsistent. |
| R-17 | Audio provenance/watermarking | Embeds inaudible watermark in TTS output for provenance verification (EU AI Act Art. 50 compliance for audio content). Upgrades R-13 (text steganography) for audio. |

### Acknowledgment

The packet acknowledges that the claim "15-layer defense stack for
on-air AI" is **incomplete** for audio/video output. The full stack for
broadcast mode is R-1 through R-17 (15 text layers + 2 audio layers).
Avatar/video output may require additional layers (R-18+) in Phase 2.

### Voice clone theft acknowledgment (per schneier P3-3)

TTS output is publicly broadcast. Anyone can capture it and use it for
voice cloning attacks. This is inherent to the concept and accepted by
the operator. Mitigation: R-17 audio watermarking provides provenance
verification (can prove a given audio clip came from the broadcast
system, not a clone).

---

## 36. Minimal Collective-Choice Arrangement (added per ostrom P2-4)

### Post-stream retro

After each AI_STANDIN session, a post-stream retro incorporates:
- Chat logs (aggregate, non-identifying)
- Sentiment data
- Retention data
- Viewer grievance channel usage (§20)
- Watchdog anomaly log

These feed into **rule modification proposals** for operator review.
Viewers do not directly modify rules, but their behavioral data
informs proposals.

### Platform-specific rule overlay

The AI's behavior rules can be **tightened per-platform** based on that
platform's moderator feedback, without requiring a full persona.py
amendment. This is a polycentric mechanism (§18, Center 3).

### Acknowledgment

Full collective-choice (viewer voting on rules, community governance)
is out of scope for Phase 1 but is a Phase 2+ consideration. The packet
acknowledges this gap rather than leaving it implicit.

---

## Appendix B: "Never Hand Off to Human" Resolution (added per popper P1.6)

### The contradiction

§4 stated as an architectural claim: "The AI never hands off directly to
human — it hands off to REPLAY."

Appendix A defined an explicit "AI → Human handoff sequence" triggered
by "explicit 'I'm back' command, heartbeat resumes, operator emergency
override."

These contradict. When the AI hands off to a returning human (per
Appendix A), is the §4 claim falsified?

### Resolution

The intended rule is narrower than stated:

> **The AI may *accept* a human takeover (human-initiated), but may
> never *initiate* a handoff that assumes the human will appear — its
> self-handoff target is always REPLAY.**

This is two distinct transitions:

| Transition | Initiated by | Target | Allowed? |
|---|---|---|---|
| AI self-handoff (safety trigger) | AI (R-7 fail, provider failure) | REPLAY | ✅ Always |
| Human takeover | Human ("I'm back", heartbeat resumes) | LIVE_HUMAN (via TRANSITIONING_TO_HUMAN) | ✅ Human-initiated |
| AI initiates handoff to human | AI | LIVE_HUMAN | ❌ Never allowed |

The conflation of "AI cannot *force* the human to appear" (true,
physical) with "AI must *route to* REPLAY, never to human" (a design
choice) is resolved: the AI's self-handoff target is always REPLAY. The
human can take over at any time (human-initiated). The AI never
initiates a handoff that assumes the human will appear.

### Falsification

This is now falsifiable: if the AI, on a safety trigger, ever emits a
handoff intent with `target=LIVE_HUMAN` rather than `target=REPLAY`,
the boundary is violated and the candidate fails the handoff test (§6
case 5).

### Appendix A correction

The Appendix A "AI → Human handoff sequence" is relabeled as
"Human Takeover Sequence (human-initiated)" to make the initiation
direction explicit. The AI does not initiate this transition; the human
does. The AI's role is to accept the takeover, deliver an outro, and
deactivate.

---

## Evidence Index

- `C:\Users\Owner\PROJECTS\reubenos\README.md` — reubenos purpose and structure
- `C:\Users\Owner\PROJECTS\reubenos\ARCHITECTURE.md` — 15-layer defense stack (R-1 to R-15)
- `C:\Users\Owner\PROJECTS\reubenos\src\reubenos\persona.py` — operator-owned persona (values, positions, boundaries, voice traits, action allowlist)
- `C:\Users\Owner\PROJECTS\reubenos\src\reubenos\twin.py` — `create_reubenos_twin()` integration surface
- `C:\Users\Owner\.devin\agents\cohost.md` — cohost agent persona (operator-assistive, "operator is the host")
- `C:\Users\Owner\.devin\skills\cohost-golive\SKILL.md` — go-live orchestration (launch/live/monitor/shutdown, no AI takeover state)
- `C:\Users\Owner\.devin\docs\streaming-aggregator-research.md` — multistream + chat aggregator research (5 SaaS + 5 self-hosted + 5 chat tools)
- `C:\Users\Owner\.agents\docs\aar\aar-anvil-streaming-completion-and-cohost-build-20260906-1605Z.md` — streaming stack + cohost build AAR
- `C:\Users\Owner\PROJECTS\hummbl-broadcast\src\hummbl_broadcast\daemon.py` — broadcast daemon state machine
- `C:\Users\Owner\PROJECTS\hummbl-broadcast\src\hummbl_broadcast\kill_switch.py` — cooperative kill switch primitive
- `C:\Users\Owner\PROJECTS\hummbl-music\hummbl_music\generative\overnight.py` — 24/7 audio loop module
- Coordination bus: Reubenos source-of-truth (2026-08-06), streaming stack completion (2026-09-06), music broadcast layer (2026-09-06)
- External research: HeyGen Avatar V, D-ID V4, Syntopia, AvatarCast, WOMO AlwaysOn, MoltStream, Open-LLM-VTuber (13.7K stars), Wallie V2, kvtuber, Autonomous-VTuber research, Neuro-sama (typed-action pattern), Fish Audio s2.1-pro, F5-TTS, OpenVoice v2, XTTS-v2, ElevenLabs Flash v2.5, Sesame CSM-1B

### ARCANA v1 review artifacts

- schneier lens review (agent_id=05fda791): 6 P1, 6 P2, 4 P3 — threat model, attack surface, kill switch, heartbeat, typed boundary enforcement, impersonation window, TRANSITIONING stall
- ashby lens review (agent_id=cb02dfc7): 6 P1, 8 P2, 4 P3 — requisite variety deficits in PresenceState, action taxonomy, defense latency, ContentScheduler, heartbeat, multi-platform
- ostrom lens review (agent_id=654b2a77): 6 P1, 5 P2, 3 P3 — circular monitoring, persona contradiction, cohost guardrail conflict, binary sanctions, conflict resolution, trust as CPR
- zuboff lens review (agent_id=8c8eebbc): 3 P1, 3 P2, 3 P3 — viewer data retention, data flow boundary, counter-asymmetry, disclosure cadence, voice clone revocation, ContentScheduler optimization
- popper lens review (agent_id=f7377926): 7 P1, 3 P2, 3 P3 — novelty conjunction, kill threshold, typed action axiom, hybrid identity unfalsifiable, case metrics, handoff contradiction, Phase 0 gate empirical

All 5 reviews: unanimous NEEDS-REVISION. All P1 findings addressed in
this revision (46 revision items, §0 revision log). P2 findings
addressed or explicitly deferred with documented reasons. P3 findings
addressed where low-cost.
