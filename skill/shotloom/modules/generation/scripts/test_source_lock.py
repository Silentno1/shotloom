#!/usr/bin/env python3
import unittest
from pathlib import Path

import source_lock_check as checker
from test_director_gate import production_fields


class SourceLockTests(unittest.TestCase):
    def test_diagnosis_and_prompting_do_not_authorize_generation(self):
        text = (Path(__file__).resolve().parents[1] / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("Do not require a full production packet", text)
        # Public boundary is stronger: remote generation is outside this module,
        # not merely an action awaiting a second permission.
        self.assertIn("This module never uploads, submits, spends credits or operates accounts", text)
        self.assertIn("a prompt-only answer does not trigger media review", text)
        self.assertIn("before production acceptance", text)

    def valid(self, level="concept"):
        return {
            **production_fields(),
            "production_level": level,
            "authority_sources_and_versions": ["screenplay-v1", "director-v2", "visual-v3"],
            "appearance_family": "photographic",
            "required_endpoint": "character exits frame",
            "review_criteria": ["identity", "endpoint"],
            "reference_manifest": [{
                "id": "face-1",
                "approval_state": "pending" if level == "concept" else "approved",
                "primary_role": "face identity",
                "allowed_transfer": "face only",
                "forbidden_transfer": "wardrobe and light",
                "priority": 1,
            }],
            "sound_ownership_plan": {
                "sound_events": [],
                "compiled_generation_audio_ids": [],
                "post_handoff_ids": [],
            },
        }

    def test_concept_allows_pending_reference(self):
        self.assertEqual(checker.validate_source_lock(self.valid()), [])

    def test_continuity_rejects_pending_reference(self):
        data = self.valid("continuity")
        data["reference_manifest"][0]["approval_state"] = "pending"
        self.assertTrue(any("requires approved" in item for item in checker.validate_source_lock(data)))

    def test_formal_requires_complete_sound_contract(self):
        data = self.valid("formal")
        data.pop("sound_ownership_plan")
        self.assertTrue(any("sound_ownership_plan" in item for item in checker.validate_source_lock(data)))


if __name__ == "__main__":
    unittest.main()
