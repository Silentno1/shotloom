#!/usr/bin/env python3
import copy
import unittest
from pathlib import Path

import continuity_state as cs


ROOT = Path(__file__).resolve().parents[1]

class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.state = cs.initial("test")

    def apply(self, **values):
        base = {"shot_id": "S1", "sequence_index": 1, "take_id": "T1", "status": "accepted", "canon_effect": "update"}
        base.update(values)
        self.state = cs.apply_update(self.state, base)

    def test_candidate_cannot_mutate_canon_or_registry(self):
        with self.assertRaises(ValueError):
            self.apply(status="candidate", canon_effect="no-change", canon_patch={"x": 1})

    def test_rejected_record_leaves_canon_unchanged(self):
        self.apply(status="rejected", canon_effect="no-change")
        self.assertEqual(self.state["current_state"], {})
        self.assertEqual(self.state["registry"], {})

    def test_earlier_replacement_invalidates_dependent_later_take(self):
        self.apply(canon_patch={"prop": {"owner": "A"}})
        self.apply(shot_id="S2", sequence_index=2, take_id="T2", canon_patch={"prop": {"condition": "broken"}})
        self.apply(shot_id="S1", sequence_index=1, take_id="T3", canon_patch={"prop": {"owner": "B"}})
        self.assertEqual(self.state["current_state"]["prop"], {"owner": "B"})
        self.assertIn("S2", self.state["stale_takes"])
        self.assertEqual(self.state["last_accepted_shot"], "S1")

    def test_replacement_does_not_mutate_previous_take_record(self):
        self.apply()
        self.apply(take_id="T2")
        versions = self.state["shots"]["S1"]["versions"]
        self.assertEqual(versions[0]["status"], "accepted")
        self.assertEqual(self.state["shots"]["S1"]["active_take"], "T2")

    def test_explicit_dependency_path_avoids_unrelated_invalidation(self):
        self.apply(canon_patch={"prop": {"owner": "A"}, "light": "warm"})
        self.apply(
            shot_id="S2",
            sequence_index=2,
            take_id="T2",
            canon_effect="no-change",
            depends_on=["state.prop.owner"],
        )
        self.apply(take_id="T3", canon_patch={"prop": {"owner": "A"}, "light": "cool"})
        self.assertNotIn("S2", self.state["stale_takes"])
        self.assertEqual(self.state["last_accepted_shot"], "S2")

    def test_registry_patch_only_from_active_accepted_take(self):
        self.apply(registry_patch={"character": {"A": {"face": "v1"}}})
        self.apply(shot_id="S1", sequence_index=1, take_id="T2", registry_patch={"character": {"A": {"face": "v2"}}})
        self.assertEqual(self.state["registry"]["character"]["A"]["face"], "v2")

    def test_sequence_index_is_immutable(self):
        self.apply()
        with self.assertRaises(ValueError):
            self.apply(take_id="T2", sequence_index=3)

    def test_retry_packet_does_not_write_unaccepted_success_to_canon(self):
        text = (ROOT / "references/failure-attribution.md").read_text(encoding="utf-8")
        self.assertIn("choose between local repair and upstream rebuild", text)
        self.assertIn("Canon changes only after the take is explicitly accepted", text)

    def test_three_render_two_review_is_conditional(self):
        text = (ROOT / "references/take-review.md").read_text(encoding="utf-8")
        self.assertIn("only when the approved appearance family says so", text)
        self.assertIn("do not apply its checklist to another family", text)

    def test_standard_3d_does_not_require_cel_shading(self):
        text = (ROOT / "references/take-review.md").read_text(encoding="utf-8")
        self.assertIn("Standard 3D", text)
        self.assertIn("do not require cel shading or 2D effects", text)


if __name__ == "__main__":
    unittest.main()
