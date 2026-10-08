#!/usr/bin/env python3
from copy import deepcopy
import unittest

import appearance_coverage_check as checker


class AppearanceCoverageTests(unittest.TestCase):
    def valid_three(self):
        return {
            "appearance_family": "three_render_two",
            "three_render_two_dimensions": {
                name: {"destination": "prompt", "note": "required in this operation"}
                for name in checker.THREE_RENDER_TWO_DIMENSIONS
            },
        }

    def test_all_eight_dimensions_are_accounted_for(self):
        self.assertEqual(checker.validate_packet(self.valid_three()), [])

    def test_missing_dimension_is_rejected(self):
        packet = self.valid_three()
        packet["three_render_two_dimensions"].pop("texture_adhesion")
        self.assertTrue(any("texture_adhesion" in item for item in checker.validate_packet(packet)))

    def test_non_prompt_destinations_are_explicit_and_valid(self):
        packet = self.valid_three()
        packet["three_render_two_dimensions"]["cadence"] = {
            "destination": "not_applicable",
            "note": "static image, not an animation keyframe",
        }
        self.assertEqual(checker.validate_packet(packet), [])

    def test_non_three_render_two_family_cannot_receive_payload(self):
        packet = {"appearance_family": "photographic", "three_render_two_dimensions": {}}
        self.assertTrue(any("must be absent" in item for item in checker.validate_packet(packet)))

    def test_other_family_without_payload_passes(self):
        self.assertEqual(checker.validate_packet({"appearance_family": "hand_drawn_2d"}), [])

    def test_all_non_three_routes_preserve_their_own_style_without_payload(self):
        for family in ("photographic", "hand_drawn_2d", "standard_3d", "stop_motion", "motion_graphics", "mixed_media", "other"):
            with self.subTest(family=family):
                packet = {"appearance_family": family, "final_appearance": "approved project-specific look"}
                original = deepcopy(packet)
                self.assertEqual(checker.validate_packet(packet), [])
                self.assertEqual(packet, original)

    def test_null_is_not_an_absent_specialized_payload(self):
        for family in ("photographic", "hand_drawn_2d", "standard_3d", "stop_motion", "motion_graphics", "mixed_media", "other"):
            with self.subTest(family=family):
                packet = {"appearance_family": family, "three_render_two_dimensions": None}
                self.assertTrue(any("must be absent" in e for e in checker.validate_packet(packet)))

    def test_mixed_root_and_local_three_map_are_checked_independently(self):
        # The coverage checker is not a recursive mixed-layer semantic validator.
        packet = {"appearance_family": "mixed_media", "layer_ownership": {"device": "three_render_two"}}
        original = deepcopy(packet)
        self.assertEqual(checker.validate_packet(packet), [])
        self.assertEqual(checker.validate_packet(self.valid_three()), [])
        self.assertEqual(packet, original)
        packet["three_render_two_dimensions"] = self.valid_three()["three_render_two_dimensions"]
        self.assertTrue(any("must be absent" in e for e in checker.validate_packet(packet)))

    def test_destination_needs_reason(self):
        packet = self.valid_three()
        packet["three_render_two_dimensions"]["contours"] = {"destination": "reference", "note": ""}
        self.assertTrue(any("non-empty note" in item for item in checker.validate_packet(packet)))


if __name__ == "__main__":
    unittest.main()
