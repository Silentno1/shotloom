#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectorContractTests(unittest.TestCase):
    def test_local_scope_does_not_require_whole_work_package(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("For a local question or adjustment", text)
        self.assertIn("not a full director package", text)
        self.assertIn("before recommending a whole-work method", text)
        self.assertIn("File writes and handoffs follow the user's authorization", text)

    def test_action_has_no_fixed_hit_duration(self):
        text = (ROOT / "references/stylized-action.md").read_text(encoding="utf-8")
        self.assertIn("No fixed seconds", text)
        self.assertIn("primary spectacle owner", text)

    def test_arcane_is_not_two_person_permanent_lock(self):
        text = (ROOT / "references/authority-and-method-bible.md").read_text(encoding="utf-8")
        self.assertIn("not a unique permanent two-person unit", text)
        self.assertIn("Barthélémy Maunoury", text)

    def test_scope_excludes_generation_and_canon(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("generation", text)
        self.assertIn("review-continuity", text)

    def test_sound_ownership_is_case_specific(self):
        text = (ROOT / "references/transitions-sound.md").read_text(encoding="utf-8")
        for state in ("native_required", "native_optional", "post_only", "intentional_silence"):
            self.assertIn(state, text)
        self.assertIn("do not have universal defaults", text)
        self.assertIn("Do not require ambience in every scene", text)


if __name__ == "__main__":
    unittest.main()
