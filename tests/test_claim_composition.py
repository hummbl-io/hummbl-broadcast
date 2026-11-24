"""Integration test for the status, proof-type, and clock-gate composition."""

import unittest

from hummbl_broadcast.claim import (
    CLAIM_VERSION,
    ClockGate,
    PlaybackWithoutClock,
    ProofKind,
    admit_proof,
    status_sentence,
)


class TestClaimComposition(unittest.TestCase):
    def test_version_is_the_design_note_cycle(self):
        self.assertEqual(CLAIM_VERSION, 1)

    def test_design_note_refuses_playback_and_the_old_claim(self):
        sentence = status_sentence(ClockGate.DESIGN_NOTE)
        self.assertNotIn("24/7", sentence)
        self.assertIn("NOT BROADCASTING", sentence)
        self.assertEqual(
            admit_proof(ProofKind.SOURCE, ClockGate.DESIGN_NOTE),
            "source_receipt",
        )
        with self.assertRaises(PlaybackWithoutClock):
            admit_proof(ProofKind.PLAYBACK, ClockGate.DESIGN_NOTE)

    def test_clock_gate_admits_playback_without_saying_live(self):
        sentence = status_sentence(ClockGate.CLOCK)
        self.assertNotIn("24/7", sentence)
        self.assertNotIn("ON AIR", sentence)
        self.assertEqual(
            admit_proof(ProofKind.SOURCE, ClockGate.CLOCK),
            "source_receipt",
        )
        self.assertEqual(
            admit_proof(ProofKind.PLAYBACK, ClockGate.CLOCK),
            "playback_receipt",
        )

    def test_parts_move_independently(self):
        """Source admission does not depend on opening the clock gate."""
        self.assertEqual(
            admit_proof(ProofKind.SOURCE, ClockGate.DESIGN_NOTE),
            admit_proof(ProofKind.SOURCE, ClockGate.CLOCK),
        )
        self.assertNotEqual(
            status_sentence(ClockGate.DESIGN_NOTE),
            status_sentence(ClockGate.CLOCK),
        )


if __name__ == "__main__":
    unittest.main()
