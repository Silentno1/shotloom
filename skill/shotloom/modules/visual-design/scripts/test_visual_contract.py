#!/usr/bin/env python3
import unittest
from pathlib import Path

import visual_contract as validator


ROOT = Path(__file__).resolve().parents[1]


class VisualContractTests(unittest.TestCase):
    def test_bounded_design_uses_conditional_reads_and_validation(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("without creating a full visual bible", text)
        self.assertIn("Do not run schema checks for a concept explanation", text)
        self.assertIn("Before handing a new or changed visual contract downstream", text)

    def common(self, family):
        return {
            "production_method": "method",
            "final_appearance": "appearance",
            "appearance_family": family,
            "space_and_perspective": "space",
            "motion_cadence": "cadence",
            "vfx_compositing": "vfx",
            "forbidden_drift": ["drift"],
        }

    def test_separates_method_appearance_category(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("Production method", text)
        self.assertIn("Final visual appearance", text)
        self.assertIn("Platform upload category", text)

    def test_three_render_two_contract_is_complete(self):
        text = (ROOT / "references/three-render-two.md").read_text(encoding="utf-8")
        for term in ("Contours", "Shadow bands", "Materials", "Texture adhesion", "Cadence", "Deformation"):
            self.assertIn(term, text)

    def test_reference_roles_have_priority_and_conflict_rules(self):
        text = (ROOT / "references/asset-and-spatial-systems.md").read_text(encoding="utf-8")
        for term in ("one primary responsibility", "priority", "allowed transfer", "forbidden transfer", "conflict rule"):
            self.assertIn(term, text)

    def test_valid_three_render_two_requires_all_eight_dimensions(self):
        data = self.common("three_render_two")
        data.update({
            "volume_and_perspective": "coherent volume",
            "line_language": "selective contours",
            "shadow_language": "two controlled bands",
            "materials": "separated cloth skin metal",
            "texture_adhesion": "attached through motion",
            "two_d_effects": "contact-aware drawn effects",
            "deformation": "bounded smears",
        })
        self.assertEqual(validator.validate_contract(data), [])
        data.pop("texture_adhesion")
        self.assertTrue(any("texture_adhesion" in item for item in validator.validate_contract(data)))

    def test_photographic_does_not_require_three_render_two_fields(self):
        data = self.common("photographic")
        data.update({
            "capture_behavior": "physical camera",
            "anatomy_and_performance": "natural",
            "light_and_color": "motivated sources",
            "materials": "physical response",
        })
        errors = validator.validate_contract(data)
        self.assertEqual(errors, [])
        self.assertNotIn("line_language", data)
        self.assertNotIn("shadow_language", data)
        self.assertNotIn("deformation", data)

    def test_anime_is_not_an_appearance_family(self):
        data = self.common("anime")
        self.assertTrue(any("unsupported appearance_family" in item for item in validator.validate_contract(data)))

    def test_three_render_two_payload_cannot_leak_into_other_family(self):
        data = self.common("hand_drawn_2d")
        data.update({
            "line_language": "drawn line",
            "shape_language": "flat graphic shape",
            "layer_and_paint": "painted layers",
            "deformation": "drawn smears",
            "three_render_two_dimensions": {},
        })
        self.assertTrue(any("allowed only" in item for item in validator.validate_contract(data)))

    def test_every_non_three_family_has_an_independent_valid_contract(self):
        family_fields = {
            "hand_drawn_2d": {
                "line_language": "drawn line",
                "shape_language": "flat shape",
                "layer_and_paint": "painted layers",
                "deformation": "drawn deformation",
            },
            "standard_3d": {
                "volume_and_perspective": "3D volume",
                "rig_and_deformation": "rig contract",
                "light_and_color": "3D lighting",
                "materials": "3D materials",
            },
            "stop_motion": {
                "material_persistence": "persistent material",
                "replacement_cadence": "replacement cadence",
                "contact_and_scale": "physical contact scale",
            },
            "motion_graphics": {
                "hierarchy_and_typography": "graphic hierarchy",
                "interpolation_and_timing": "motion timing",
                "information_legibility": "legible information",
            },
            "mixed_media": {
                "layer_ownership": "owned layers",
                "boundary_rules": "explicit boundaries",
                "retained_anchors": "retained anchors",
            },
            "other": {"family_specific_contract": "project-specific contract"},
        }
        for family, fields in family_fields.items():
            with self.subTest(family=family):
                data = self.common(family)
                data.update(fields)
                self.assertEqual(validator.validate_contract(data), [])
                self.assertNotIn("three_render_two_dimensions", data)


if __name__ == "__main__":
    unittest.main()
