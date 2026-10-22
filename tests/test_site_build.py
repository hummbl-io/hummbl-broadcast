"""Test site build and static output for hummbl-broadcast.

These tests are claim-honesty gates, not copy checks. The published site is a
static artifact on a public CDN describing a pipeline that has never completed a
verified real generation run. So the invariants here assert what the build must
*not* say as firmly as what it must say:

  - no fabricated runtime state ("ON AIR", "24/7 ACTIVE", health "healthy")
  - no mock data presented as real audit receipts
  - no claim of cryptographic verification while receipts.py is a plain appender
  - no published price that disagrees with models.PRICE_PER_SECOND

An earlier revision of this file asserted `assertIn("ON AIR", html)` and
`health["status"] == "healthy"`, which made the false claims load-bearing: being
honest broke the suite. Those assertions are inverted deliberately -- if a
future change reintroduces the strings, these tests must fail.

The build is also redirected into a temp directory. The previous version called
build() against the real repo `public/` in setUp, so running the suite mutated
tracked files (and in a clean checkout rewrote receipts.json to empty).
"""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import tools.build_site as bs  # noqa: E402
from hummbl_broadcast.models import PRICE_PER_SECOND, ModelTier  # noqa: E402

# Strings that assert operational state a static artifact cannot observe.
FORBIDDEN_STATE_STRINGS = [
    "ON AIR",
    "24/7 ACTIVE",
    "Edge Node anvil",
    "APPROVED (Within $10 Cap)",
    # The claim, not the word: "not cryptographically verifiable" must stay legal.
    "verifiable cryptographic audit receipts",
    "cryptographic audit receipts",
]

# JS fallbacks that substituted invented values for absent receipt fields.
FORBIDDEN_FALLBACKS = [
    "r.cost_usd || 0.20",
    "r.model || 'MiniMax-H3'",
    "r.duration_seconds || 4",
    "rec_default",
    "2026-08-31T20:00:00Z",
    ">COMPLETED<",
]


class SiteBuildTestCase(unittest.TestCase):
    """Builds into a temp dir so the suite never mutates tracked public/."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        tmp_public = Path(self._tmp.name) / "public"
        self._orig = (bs.PUBLIC_DIR, bs.API_DIR)
        bs.PUBLIC_DIR = tmp_public
        bs.API_DIR = tmp_public / "api"
        bs.build()
        self.public = tmp_public
        self.api = tmp_public / "api"

    def tearDown(self):
        bs.PUBLIC_DIR, bs.API_DIR = self._orig
        self._tmp.cleanup()

    def _html(self):
        return (self.public / "index.html").read_text(encoding="utf-8")

    def _json(self, name):
        return json.loads((self.api / name).read_text(encoding="utf-8"))


class TestArtifacts(SiteBuildTestCase):
    def test_public_artifacts_exist(self):
        self.assertTrue((self.public / "index.html").exists())
        for name in ("schedule.json", "receipts.json", "summary.json", "health.json"):
            self.assertTrue((self.api / name).exists(), name)

    def test_no_external_scripts(self):
        html = self._html()
        self.assertNotIn("https://cdn.", html)
        self.assertNotIn('<script src="http', html)

    def test_identifying_copy_present(self):
        html = self._html()
        self.assertIn("HUMMBL Broadcast", html)
        self.assertIn("Morning Fleet SITREP", html)


class TestNoFabricatedRuntimeState(SiteBuildTestCase):
    def test_html_does_not_claim_to_be_live(self):
        html = self._html()
        for bad in FORBIDDEN_STATE_STRINGS:
            self.assertNotIn(bad, html, f"page asserts unobservable state: {bad!r}")

    def test_html_declares_not_broadcasting(self):
        html = self._html()
        self.assertIn("NOT BROADCASTING", html)
        self.assertIn("PRE-ALPHA", html)

    def test_html_disclaims_receipt_verifiability(self):
        """Positive counterpart: the page must say what the receipts are not."""
        html = self._html()
        self.assertIn("not cryptographically verifiable", html)
        self.assertIn("specified but not implemented", html)

    def test_endpoint_descriptions_do_not_contradict_artifacts(self):
        html = self._html()
        self.assertNotIn("Completed broadcast clip generation audit receipts", html)
        self.assertNotIn("Edge service health check and runtime state", html)

    def test_health_endpoint_does_not_claim_healthy(self):
        health = self._json("health.json")
        self.assertNotEqual(health.get("status"), "healthy")
        self.assertEqual(health.get("status"), "not_measured")
        self.assertIs(health.get("is_liveness_probe"), False)
        self.assertIn("disclosure", health)

    def test_summary_reports_real_state(self):
        summary = self._json("summary.json")
        self.assertEqual(summary.get("repo"), "hummbl-broadcast")
        self.assertEqual(summary.get("domain"), "broadcast.hummbl.dev")
        self.assertNotEqual(summary.get("status"), "24/7 ACTIVE")
        self.assertIs(summary.get("is_live"), False)
        self.assertEqual(summary.get("broadcast_state"), "not-broadcasting")
        self.assertEqual(summary.get("verified_real_generation_runs"), 0)
        self.assertEqual(summary.get("benchmarks_status"), "not-run")
        self.assertEqual(summary.get("schedule_blocks_planned"), 4)

    def test_schedule_blocks_are_marked_planned(self):
        schedule = self._json("schedule.json")
        self.assertEqual(len(schedule), 4)
        for block in schedule:
            self.assertEqual(block.get("state"), "planned", block.get("id"))


class TestReceiptHonesty(SiteBuildTestCase):
    def test_receipts_carry_mock_disclosure(self):
        doc = self._json("receipts.json")
        self.assertIsInstance(doc, dict, "bare array lets a consumer read mock as real")
        self.assertEqual(doc.get("data_source"), "mock-adapter")
        self.assertIs(doc.get("is_real_generation"), False)
        self.assertIn("disclosure", doc)
        self.assertIsInstance(doc.get("receipts"), list)

    def test_renderer_does_not_fabricate_absent_fields(self):
        html = self._html()
        for bad in FORBIDDEN_FALLBACKS:
            self.assertNotIn(bad, html, f"renderer fabricates receipt data: {bad!r}")

    def test_receipt_hashing_not_claimed(self):
        """receipts.py is a plain JSONL appender: no hash, no signature."""
        summary = self._json("summary.json")
        self.assertIs(summary.get("receipt_hashing_implemented"), False)
        src = (REPO_ROOT / "src" / "hummbl_broadcast" / "receipts.py").read_text(
            encoding="utf-8"
        )
        for primitive in ("hashlib", "sha256", "hmac"):
            self.assertNotIn(
                primitive,
                src,
                "receipts.py now implements hashing -- update the published "
                "claims and this gate together",
            )


class TestPublishedPricingMatchesCode(SiteBuildTestCase):
    def test_no_price_disagrees_with_models_table(self):
        """The page once advertised H3 at $0.03/sec against a verified $0.08."""
        html = self._html()
        self.assertNotIn("$0.03/sec", html)
        for tier in (ModelTier.H3, ModelTier.H3_MAX_480P, ModelTier.H3_MAX_768P):
            rendered = f"${PRICE_PER_SECOND[tier]:.2f}/sec"
            self.assertIn(rendered, html, f"{tier} rate missing or stale")

    def test_latency_is_not_asserted(self):
        html = self._html()
        self.assertNotIn("12-18 seconds", html)
        self.assertIn("not measured", html)


if __name__ == "__main__":
    unittest.main()
