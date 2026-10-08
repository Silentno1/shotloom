"""Behavior regressions for standalone audio and malformed contract values."""
import copy
import unittest

import appearance_coverage_check as appearance
import platform_evidence_check as evidence
import sound_contract_check as sound
import source_lock_check as source
from test_director_gate import production_fields


class InputSafetyTests(unittest.TestCase):
    def test_appearance_malformed_destinations_report_errors(self):
        for value in ([], {}, None, 1, True):
            packet = {"appearance_family": "three_render_two", "three_render_two_dimensions": {
                k: {"destination": value, "note": "test"} for k in appearance.THREE_RENDER_TWO_DIMENSIONS}}
            with self.subTest(value=value):
                self.assertTrue(appearance.validate_packet(packet))

    def test_required_evidence_unhashable_level_reports_errors(self):
        for value in ([], {}, None, 1, True):
            packet = {"platform": "test", "model": "test", "surface": "test", "required_claims": ["c"],
                      "claims": [{"id": "c", "value": 1, "evidence_level": value}]}
            with self.subTest(value=value):
                self.assertTrue(evidence.validate_evidence(packet))

    def test_top_level_nonobjects_report_errors(self):
        for value in ([], None, "text"):
            self.assertTrue(appearance.validate_packet(value))
            self.assertTrue(evidence.validate_evidence(value))

    def partition(self, requires_sync):
        return {"sound_events": [{"id": "voice", "category": "dialogue", "continuity_scope": "scene",
                "audible_ownership": "post_only", "post_handoff": "ADR", "requires_picture_sync": requires_sync}],
                "compiled_generation_audio_ids": [], "post_handoff_ids": ["voice"]}

    def test_sync_flag_is_strict_boolean(self):
        for value in ("true", "false", 1, 0, [], {}, None):
            with self.subTest(value=value):
                self.assertTrue(any("boolean" in e for e in sound.validate_sound_contract(self.partition(value))))

    def test_true_sync_still_requires_anchors(self):
        self.assertTrue(any("picture_cue" in e for e in sound.validate_sound_contract(self.partition(True))))

    def test_unsynchronized_post_audio_remains_valid(self):
        self.assertEqual(sound.validate_sound_contract(self.partition(False)), [])


class AudioLockTests(unittest.TestCase):
    def packet(self):
        return {**production_fields(), "media_type": "audio", "production_level": "formal", "authority_sources_and_versions": ["sound-v1"],
                "required_endpoint": "complete line", "review_criteria": ["actual listening", "words", "sync"],
                "reference_manifest": [], "audio_brief": {
                    "purpose": "ADR", "delivery_role": "master_candidate", "sound_ids": ["voice-1"],
                    "content": "exact approved words", "timing": "cut-v2 sync anchors", "voice_or_source_identity": "voice-v1",
                    "acoustic_perspective": "near dry voice", "usage_authority": "user-owned source"}}

    def test_audio_does_not_require_appearance_or_picture_partition(self):
        self.assertEqual(source.validate_source_lock(self.packet()), [])

    def test_audio_cannot_redefine_picture_ownership(self):
        packet = self.packet()
        packet["sound_ownership_plan"] = {}
        self.assertTrue(source.validate_source_lock(packet))

    def test_audio_missing_brief_fields_is_not_complete(self):
        for field in self.packet()["audio_brief"]:
            packet = self.packet()
            del packet["audio_brief"][field]
            with self.subTest(field=field):
                self.assertTrue(source.validate_source_lock(packet))

    def test_audio_formal_pending_voice_not_approved(self):
        packet = self.packet()
        packet["reference_manifest"] = [{"id": "voice", "approval_state": "pending", "primary_role": "voice",
                "allowed_transfer": "identity", "forbidden_transfer": "text", "priority": 1}]
        self.assertTrue(any("requires approved" in x for x in source.validate_source_lock(packet)))

    def test_image_and_video_requirements_not_weakened(self):
        for media in ("image", "video"):
            packet = self.packet()
            packet["media_type"] = media
            self.assertTrue(any("appearance_family" in x for x in source.validate_source_lock(packet)))


if __name__ == "__main__":
    unittest.main()
