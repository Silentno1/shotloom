#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReviewContractTests(unittest.TestCase):
    def test_targeted_review_cannot_silently_approve_or_write(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("does not request a full acceptance review or a ledger write", text)
        self.assertIn("Still-image review does not need video preflight", text)
        self.assertIn("Actual listening at normal playback is mandatory", text)
        self.assertIn("Only after explicit acceptance", text)

    def test_sound_review_respects_plan_and_actual_result(self):
        text = (ROOT / "references/take-review.md").read_text(encoding="utf-8")
        self.assertIn("Missing `post_only` sound is expected", text)
        self.assertIn("Natural native dialogue", text)
        self.assertIn("compare acoustic identity", text)

    def test_post_owned_absence_does_not_trigger_retry(self):
        text = (ROOT / "references/failure-attribution.md").read_text(encoding="utf-8")
        self.assertIn("do not retry picture generation", text)
        self.assertIn("preserve any native sound that already passes", text)


if __name__ == "__main__":
    unittest.main()
