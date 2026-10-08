#!/usr/bin/env python3
"""Contract routing tests, not measurements of any model's visual quality."""

from copy import deepcopy
import unittest

import visual_contract as validator


class OpenAppearanceTests(unittest.TestCase):
    def common(self, family, name):
        return {
            "production_method": "AI generation from approved first frame",
            "final_appearance": name,
            "appearance_family": family,
            "space_and_perspective": "flat overlap; no orbit or lens parallax",
            "motion_cadence": "approved held poses and discrete changes",
            "vfx_compositing": "no added effects",
            "forbidden_drift": ["envelope changes owner before the handoff"],
        }

    def custom(self):
        data = self.common("other", "墨片折影：剪纸形状与情绪墨色")
        data["family_specific_contract"] = {
            "edges": "no fixed outline; paper silhouette stays readable",
            "paint": "ink area changes with the approved emotional beat",
            "motion": "whole-shape replacement allowed on the turn",
            "anchors": "envelope identity and ownership persist through replacement",
        }
        return data

    def mixed(self):
        data = self.common("mixed_media", "permanent photo, drawn and cel-like composite")
        data.update({
            "space_and_perspective": "shared composition with contracted occlusion",
            "motion_cadence": "each layer keeps its approved cadence; contact synchronizes",
            "layer_ownership": {
                "character": {"appearance_family": "photographic", "rule": "photo materials"},
                "background": {"appearance_family": "hand_drawn_2d", "rule": "flat paint"},
                "device": {"appearance_family": "three_render_two", "rule": "bounded cel shading"},
            },
            "boundary_rules": "device remains in the character's hand; layers coexist throughout",
            "retained_anchors": ["identity", "device ownership", "shared event timing"],
        })
        return data

    def test_unlisted_custom_look_is_preserved_without_normalization(self):
        data = self.custom()
        original = deepcopy(data)
        self.assertEqual(validator.validate_contract(data), [])
        self.assertEqual(data, original)

    def test_custom_name_does_not_need_a_new_family_enum(self):
        data = self.custom()
        data["final_appearance"] = "unnamed experimental paper-and-ink look"
        self.assertEqual(validator.validate_contract(data), [])
        self.assertEqual(data["appearance_family"], "other")

    def test_custom_contract_cannot_be_replaced_by_only_a_style_name(self):
        data = self.custom()
        data.pop("family_specific_contract")
        self.assertTrue(any("family_specific_contract" in e for e in validator.validate_contract(data)))

    def test_unknown_schema_key_points_to_other_without_reclassifying_input(self):
        data = self.custom()
        data["appearance_family"] = "墨片折影"
        self.assertTrue(any("or other" in e for e in validator.validate_contract(data)))
        self.assertEqual(data["appearance_family"], "墨片折影")

    def test_outline_free_2d_is_valid_with_meaningful_edge_decision(self):
        data = self.common("hand_drawn_2d", "outline-free watercolor")
        data.update({
            "line_language": "no fixed contour; color edges may breathe",
            "shape_language": "flat readable shapes",
            "layer_and_paint": "watercolor layers; bounded paint variation",
            "deformation": "approved drawn replacements, not 3D rig deformation",
        })
        original = deepcopy(data)
        self.assertEqual(validator.validate_contract(data), [])
        self.assertEqual(data, original)
        self.assertNotIn("shadow_language", data)
        self.assertNotIn("volume_and_perspective", data)

    def test_same_2d_family_can_preserve_opposite_edge_and_cadence_choices(self):
        base = self.common("hand_drawn_2d", "project-specific drawn animation")
        base.update({"shape_language": "drawn silhouettes", "layer_and_paint": "painted layers", "deformation": "bounded deformation"})
        looks = [
            {"line_language": "fixed clean contours", "motion_cadence": "continuous drawn motion"},
            {"line_language": "no fixed outline", "motion_cadence": "held poses and stepped changes"},
        ]
        for decisions in looks:
            with self.subTest(decisions=decisions):
                data = {**base, **decisions}
                self.assertEqual(validator.validate_contract(data), [])
                for key, value in decisions.items():
                    self.assertEqual(data[key], value)

    def test_standard_3d_needs_no_outline_or_shadow_band_fields(self):
        data = self.common("standard_3d", "mature stylized volume without cartoon outlines")
        data.update({
            "space_and_perspective": "coherent 3D space",
            "volume_and_perspective": "stable character and prop volumes",
            "rig_and_deformation": "bounded rig deformation",
            "light_and_color": "volumetric light with continuity",
            "materials": "separated materials without cel bands",
        })
        self.assertEqual(validator.validate_contract(data), [])
        self.assertNotIn("line_language", data)
        self.assertNotIn("shadow_language", data)

    def test_stop_motion_keeps_stepping_and_material_marks(self):
        data = self.common("stop_motion", "clay stop-motion appearance")
        data.update({
            "material_persistence": "finger impressions allowed; object identity persists",
            "replacement_cadence": "12fps-like stepping; not an output-fps assertion",
            "contact_and_scale": "cup and hand contact positions persist",
        })
        original = deepcopy(data)
        self.assertEqual(validator.validate_contract(data), [])
        self.assertEqual(data, original)

    def test_permanent_mixed_composite_needs_no_invented_global_return(self):
        data = self.mixed()
        original = deepcopy(data)
        self.assertEqual(validator.validate_contract(data), [])
        self.assertEqual(data, original)
        self.assertNotIn("three_render_two_dimensions", data)
        # This checks root routing only; nested artistic rules still require review.

    def test_local_three_render_two_layer_does_not_allow_global_payload(self):
        for payload in ("three_render_two_dimensions", "three_render_two_contract"):
            for value in ({}, None, {"contours": "local device only"}):
                with self.subTest(payload=payload, value=value):
                    data = self.mixed()
                    data[payload] = value
                    self.assertTrue(any("allowed only" in e for e in validator.validate_contract(data)))


if __name__ == "__main__":
    unittest.main()
