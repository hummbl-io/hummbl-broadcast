"""One composition of the three broadcast parts.

Status sentence, proof type, and clock gate stay separate. This module only
chains them: the gate chooses the sentence, and the sentence's gate decides
whether a proof may be called playback.
"""

from __future__ import annotations

from enum import Enum

# v0 was the isolated chain. v1 points the README and the site status at the
# design-note sentence and labels ingest as a source receipt. No clock.
CLAIM_VERSION = 1


class ClockGate(Enum):
    DESIGN_NOTE = "design-note"
    CLOCK = "clock"


class ProofKind(Enum):
    SOURCE = "source"
    PLAYBACK = "playback"


STATUS_SENTENCE = {
    ClockGate.DESIGN_NOTE: (
        "PRE-ALPHA — NOT BROADCASTING. Design note. No playback clock."
    ),
    ClockGate.CLOCK: (
        "Playback clock is in scope. This sentence is not a claim of being live."
    ),
}


class PlaybackWithoutClock(Exception):
    """A source-file proof must not be admitted as playback."""


def status_sentence(gate: ClockGate) -> str:
    sentence = STATUS_SENTENCE[gate]
    if "24/7" in sentence:
        raise ValueError("status sentence must not restore the 24/7 claim")
    return sentence


def admit_proof(kind: ProofKind, gate: ClockGate) -> str:
    """Return the proof type name this gate allows.

    A source proof is always a source receipt. A playback proof is admitted
    only when the clock gate is CLOCK. Admission does not mean anything aired.
    """
    sentence = status_sentence(gate)
    if kind is ProofKind.SOURCE:
        if "NOT BROADCASTING" not in sentence and gate is ClockGate.DESIGN_NOTE:
            raise ValueError("design-note status lost its refusal")
        return "source_receipt"
    if gate is not ClockGate.CLOCK:
        raise PlaybackWithoutClock(sentence)
    return "playback_receipt"
