"""Test site build and static output for hummbl-broadcast."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSiteBuild(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        import tools.build_site as bs
        self.bs = bs
        self.bs.build()

    def test_public_artifacts_exist(self):
        public = REPO_ROOT / "public"
        self.assertTrue((public / "index.html").exists())
        self.assertTrue((public / "api" / "schedule.json").exists())
        self.assertTrue((public / "api" / "receipts.json").exists())
        self.assertTrue((public / "api" / "summary.json").exists())
        self.assertTrue((public / "api" / "health.json").exists())

    def test_index_html_invariants(self):
        html = (REPO_ROOT / "public" / "index.html").read_text(encoding="utf-8")
        self.assertIn("HUMMBL Broadcast", html)
        self.assertIn("ON AIR", html)
        self.assertIn("Morning Fleet SITREP", html)
        self.assertIn("MiniMax-H3", html)
        # Verify no external unmetered scripts
        self.assertNotIn("https://cdn.", html)
        self.assertNotIn("<script src=\"http", html)

    def test_json_validity(self):
        summary = json.loads((REPO_ROOT / "public" / "api" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary.get("repo"), "hummbl-broadcast")
        self.assertEqual(summary.get("domain"), "broadcast.hummbl.dev")
        self.assertEqual(summary.get("schedule_blocks"), 4)

        health = json.loads((REPO_ROOT / "public" / "api" / "health.json").read_text(encoding="utf-8"))
        self.assertEqual(health.get("status"), "healthy")


if __name__ == "__main__":
    unittest.main()
