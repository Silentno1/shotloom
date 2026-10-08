#!/usr/bin/env python3
import unittest

import sound_contract_check as checker


class SoundOwnershipContractTests(unittest.TestCase):
    def valid(self):
        return {
            "sound_events": [
                {
                    "id": "dialogue-1",
                    "category": "dialogue",
                    "continuity_scope": "shot",
                    "audible_ownership": "post_only",
                    "selected_for_generation": False,
                    "requires_picture_sync": True,
                    "picture_sync_strategy": "external_lipsync",
                    "picture_cue": "visible mouth performance follows the approved line",
                    "sync_anchor": {"start": "mouth opens", "stop": "lips close"},
                    "post_handoff": {"line": "批准对白", "perspective": "close"},
                    "audible_prompt_markers": ["批准对白"],
                },
                {
                    "id": "cup-contact",
                    "category": "prop_contact",
                    "continuity_scope": "shot",
                    "audible_ownership": "native_required",
                    "selected_for_generation": True,
                    "picture_sync_strategy": "native_audio_driver",
                    "audible_prompt_markers": ["cup click"],
                },
                {
                    "id": "room-tone",
                    "category": "ambience",
                    "continuity_scope": "scene",
                    "audible_ownership": "native_optional",
                    "selected_for_generation": False,
                    "post_handoff": {"identity": "quiet cafe bed"},
                    "audible_prompt_markers": ["quiet cafe bed"],
                },
            ],
            "compiled_generation_audio_ids": ["cup-contact"],
            "post_handoff_ids": ["dialogue-1", "room-tone"],
        }

    def test_valid_contract_separates_post_dialogue_picture_sync_from_audio(self):
        self.assertEqual(checker.validate_sound_contract(self.valid()), [])

    def test_post_only_cannot_leak_into_generation_partition(self):
        data = self.valid()
        data["compiled_generation_audio_ids"].append("dialogue-1")
        self.assertTrue(any("exactly equal" in item for item in checker.validate_sound_contract(data)))

    def test_synchronized_post_dialogue_needs_picture_strategy_and_anchors(self):
        data = self.valid()
        event = data["sound_events"][0]
        event["picture_sync_strategy"] = "none"
        event.pop("sync_anchor")
        errors = checker.validate_sound_contract(data)
        self.assertTrue(any("picture-sync strategy" in item for item in errors))
        self.assertTrue(any("sync_anchor" in item for item in errors))

    def test_duplicate_ids_are_rejected(self):
        data = self.valid()
        data["sound_events"].append(dict(data["sound_events"][0]))
        self.assertTrue(any("duplicate sound id" in item for item in checker.validate_sound_contract(data)))

    def test_post_only_marker_is_rejected_from_prompt_sound_fields_but_allowed_in_picture_description(self):
        prompt = """integrated_multimodal_description:\nMouths 批准对白 for later dubbing.\noverall_soundscape:\nCup click.\nnon_diegetic_music:\nNone.\n"""
        result = checker.check_sound_contract(self.valid(), prompt)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(result["unverified"])
        bad = prompt.replace("Cup click.", "Cup click plus 批准对白.")
        self.assertTrue(any("leaked" in item for item in checker.validate_sound_contract(self.valid(), bad)))


if __name__ == "__main__":
    unittest.main()
