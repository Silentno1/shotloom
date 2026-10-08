#!/usr/bin/env python3
import unittest
from pathlib import Path

import prompt_structure_check as checker


ROOT = Path(__file__).resolve().parents[1]

BASE = """integrated_multimodal_description:\n[Shot 1] Setup.\n[Shot 2] At 00:02.500, consequence.\noverall_soundscape:\nRoom tone.\nnon_diegetic_music:\nN/A\n"""
REF = """subject_definitions:\n<Subject 1> from <Picture 1>.\n<Video 1> supplies camera movement.\n<Audio 1> supplies voice timbre for <Subject 1> (S1).\nsummary:\n[reference generation + audio reference] A brief exchange.\nretention_analysis:\n<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - identity.\n<Video 1>: weak_reference - camera movement.\n<Audio 1>: reference - voice timbre only.\ndetailed_description:\nLive-action.\n[Shot 1] Setup.\n[Shot 2] At 00:03.000, the camera follows <Video 1>'s movement. <Subject 1> (S1) uses <Audio 1>'s timbre and says <d>[Chinese] 等一下。</d>\noverall_soundscape:\nRoom tone.\nnon_diegetic_music:\nN/A\n"""


class H3StructureTests(unittest.TestCase):
    def empty(self):
        return {"first_frames": 0, "last_frames": 0, "reference_images": [], "reference_videos": [], "reference_audios": []}

    def test_valid_t2va(self):
        errors, _ = checker.check_h3(BASE, "T2VA", 7, self.empty())
        self.assertEqual(errors, [])

    def test_valid_ref2va(self):
        manifest = self.empty()
        manifest["reference_images"] = [{"id": 1, "role": "identity"}]
        manifest["reference_videos"] = [{"id": 1, "duration": 5, "role": "motion"}]
        manifest["reference_audios"] = [{"id": 1, "duration": 4, "role": "voice"}]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertEqual(errors, [])

    def test_audio_only_ref_is_rejected(self):
        manifest = self.empty()
        manifest["reference_audios"] = [{"id": 1, "duration": 4, "role": "voice"}]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertTrue(any("only Ref2VA" in item for item in errors))

    def test_total_file_count_and_media_durations(self):
        manifest = self.empty()
        manifest["reference_images"] = [{"id": i, "role": "image"} for i in range(1, 10)]
        manifest["reference_videos"] = [{"id": 1, "duration": 8, "role": "motion"}, {"id": 2, "duration": 8, "role": "motion"}, {"id": 3, "duration": 2, "role": "motion"}]
        manifest["reference_audios"] = [{"id": 1, "duration": 1, "role": "voice"}]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertTrue(any("12-file" in item for item in errors))
        self.assertTrue(any("video total" in item for item in errors))
        self.assertTrue(any("audio 1 duration" in item for item in errors))

    def test_wrong_schema_and_seedance_label(self):
        text = BASE.replace("integrated_multimodal_description:", "overall_soundscape:", 1) + "\n@图片1"
        errors, _ = checker.check_h3(text, "T2VA", 7, self.empty())
        self.assertTrue(any("field order" in item for item in errors))
        self.assertTrue(any("@ media labels" in item for item in errors))

    def test_cut_must_be_inside_duration(self):
        errors, _ = checker.check_h3(BASE.replace("00:02.500", "00:07.000"), "T2VA", 7, self.empty())
        self.assertTrue(any("inside" in item for item in errors))

    def test_empty_required_fields_are_rejected(self):
        empty = "integrated_multimodal_description:\noverall_soundscape:\nnon_diegetic_music:\n"
        errors, _ = checker.check_h3(empty, "T2VA", 7, self.empty())
        self.assertTrue(any("field is empty" in item for item in errors))

    def test_reference_ids_and_roles_are_validated(self):
        manifest = self.empty()
        manifest["reference_images"] = [{"id": 2, "role": ""}]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertTrue(any("consecutive" in item for item in errors))
        self.assertTrue(any("role" in item for item in errors))

    def test_shot_blocks_cannot_be_hidden_in_summary(self):
        bad = REF.replace("A brief exchange.", "[Shot 99] At 00:01.000, hidden cut.")
        manifest = self.empty()
        manifest["reference_images"] = [{"id": 1, "role": "identity"}]
        manifest["reference_videos"] = [{"id": 1, "duration": 5, "role": "motion"}]
        manifest["reference_audios"] = [{"id": 1, "duration": 4, "role": "voice"}]
        errors, _ = checker.check_h3(bad, "Ref2VA", 8, manifest)
        self.assertTrue(any("belong only" in item for item in errors))

    def ref_manifest(self):
        manifest = self.empty()
        manifest["reference_images"] = [{"id": 1, "role": "identity"}]
        manifest["reference_videos"] = [{"id": 1, "duration": 5, "role": "motion"}]
        manifest["reference_audios"] = [{"id": 1, "duration": 4, "role": "voice"}]
        return manifest

    def test_definition_and_retention_shot_references_are_legal(self):
        text = REF.replace("<Subject 1> from <Picture 1>.", "<Subject 1> from <Picture 1>.\n<Picture 1> is the first frame of [Shot 1].")
        errors, _ = checker.check_h3(text, "Ref2VA", 8, self.ref_manifest())
        self.assertEqual(errors, [])

    def test_missing_single_shot_marker_is_rejected(self):
        text = BASE.replace("[Shot 1] Setup.\n[Shot 2] At 00:02.500, consequence.", "An unmarked single shot.")
        errors, _ = checker.check_h3(text, "T2VA", 7, self.empty())
        self.assertTrue(any("requires [Shot 1]" in item for item in errors))

    def test_cut_timestamp_requires_three_decimals(self):
        errors, _ = checker.check_h3(BASE.replace("00:02.500", "00:02.5"), "T2VA", 7, self.empty())
        self.assertTrue(any("MM:SS.mmm" in item for item in errors))

    def test_keyframe_alignments_match_last_shot_and_duration(self):
        instructions = {
            "I2VA": (1, 0, "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."),
            "FL2VA": (1, 1, "How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 2) aligns with the 7.00-second mark of the target video."),
            "L2VA": (0, 1, "How the reference pictures align with the target video — <Picture 1> (from [Shot 2]) aligns with the 7.00-second mark of the target video."),
        }
        for mode, (first, last, instruction) in instructions.items():
            with self.subTest(mode=mode):
                manifest = self.empty()
                manifest.update(first_frames=first, last_frames=last)
                errors, _ = checker.check_h3(instruction + "\n\n" + BASE, mode, 7, manifest)
                self.assertEqual(errors, [])
                errors, _ = checker.check_h3(BASE, mode, 7, manifest)
                self.assertTrue(any("alignment" in item for item in errors))

    def test_wrong_final_frame_time_is_rejected(self):
        manifest = self.empty()
        manifest["last_frames"] = 1
        text = "How the reference pictures align with the target video — <Picture 1> (from [Shot 2]) aligns with the 8.00-second mark of the target video.\n\n" + BASE
        errors, _ = checker.check_h3(text, "L2VA", 7, manifest)
        self.assertTrue(any("alignment" in item for item in errors))

    def test_enabled_video_audio_is_not_an_extra_uploaded_file(self):
        manifest = self.ref_manifest()
        manifest["reference_images"] = [{"id": i, "role": "identity"} for i in range(1, 10)]
        manifest["reference_videos"] = [{"id": i, "duration": 5, "role": "motion"} for i in range(1, 4)]
        manifest["reference_audios"] = [{"id": 1, "source_video_id": 2, "duration": 5, "role": "voice"}]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertEqual(errors, [])

    def test_unbound_or_overlong_video_audio_is_rejected(self):
        for source_id, duration, expected in [(9, 4, "source_video_id"), (1, 6, "fit its source")]:
            with self.subTest(source_id=source_id, duration=duration):
                manifest = self.ref_manifest()
                manifest["reference_audios"][0].update(source_video_id=source_id, duration=duration)
                errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
                self.assertTrue(any(expected in item for item in errors))

    def test_bad_source_duration_reports_errors_without_crash(self):
        manifest = self.ref_manifest()
        manifest["reference_videos"][0]["duration"] = "unknown"
        manifest["reference_audios"][0]["source_video_id"] = 1
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertTrue(any("numeric duration" in item for item in errors))

    def test_duplicate_video_audio_track_is_rejected(self):
        manifest = self.ref_manifest()
        manifest["reference_audios"] = [{"id": i, "source_video_id": 1, "duration": 4, "role": "voice"} for i in (1, 2)]
        errors, _ = checker.check_h3(REF, "Ref2VA", 8, manifest)
        self.assertTrue(any("track once" in item for item in errors))

    def test_generic_validator_cannot_return_false_confidence(self):
        errors, _ = checker.check_generic()
        self.assertTrue(any("cannot validate" in item for item in errors))


class CompilationContractTests(unittest.TestCase):
    def test_transcode_starts_from_shared_source_lock(self):
        text = (ROOT / "references/source-lock-transcode-repair.md").read_text(encoding="utf-8")
        self.assertIn("Start from the same source lock", text)
        self.assertIn("not from another model's finished prompt", text)

    def test_prompt_check_does_not_auto_rewrite(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("When asked to check only, diagnose without rewriting", text)

    def test_repair_separates_local_change_from_upstream_rebuild(self):
        text = (ROOT / "references/source-lock-transcode-repair.md").read_text(encoding="utf-8")
        self.assertIn("change_scope", text)
        self.assertIn("return to the owning upstream contract", text)

    def test_three_render_two_compiler_has_an_explicit_activation_gate(self):
        text = (ROOT / "references/three-render-two-compilation.md").read_text(encoding="utf-8")
        self.assertIn("only when the approved source lock records", text)
        self.assertIn("Do not activate it from", text)

    def test_other_appearance_families_do_not_inherit_three_render_two(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("Appearance-family rules are conditional", text)
        self.assertIn("must not inherit three-render-two requirements", text)


if __name__ == "__main__":
    unittest.main()
