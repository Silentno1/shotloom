"""State revisions, edit-event accounting, and real native-frame evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import continuity_state as cs
import selection_manifest_check as selection
import take_preflight as take


class RevisionTests(unittest.TestCase):
    def state(self):
        state = cs.initial("fixture")
        for i in (1, 2):
            state = cs.apply_update(state, {"shot_id": f"S{i}", "take_id": f"T{i}", "status": "accepted",
                "sequence_index": i, "canon_patch": {"owner": "B"} if i == 1 else {"broken": True}})
        return state

    def revision(self, state, **kwargs):
        return {"expected_state_hash": cs.value_hash(state), "reason": "authorized edit", "approval_source": "test-only approval", **kwargs}

    def test_withdrawal_keeps_history_and_invalidates_dependencies(self):
        state = self.state()
        old = copy.deepcopy(state)
        result = cs.revise_state(state, self.revision(state, deactivate_shots=["S1"]))
        self.assertEqual(state, old)
        self.assertEqual(result["shots"]["S1"]["versions"], old["shots"]["S1"]["versions"])
        self.assertIsNone(result["shots"]["S1"]["active_take"])
        self.assertIn("S2", result["stale_takes"])
        self.assertEqual(result["current_state"], {})
        self.assertEqual(cs.validate_state(result), [])

    def test_reject_candidate_does_not_withdraw_accepted(self):
        result = cs.apply_update(self.state(), {"shot_id": "S1", "take_id": "rejected", "sequence_index": 1,
                                              "status": "rejected", "canon_effect": "no-change"})
        self.assertEqual(result["shots"]["S1"]["active_take"], "T1")

    def test_resequence_marks_moved_takes_stale_without_rewriting_versions(self):
        state = self.state()
        result = cs.revise_state(state, self.revision(state, sequence_indices={"S1": 2, "S2": 1}))
        self.assertEqual(set(result["stale_takes"]), {"S1", "S2"})
        self.assertEqual(result["shots"]["S1"]["versions"], state["shots"]["S1"]["versions"])
        result = cs.apply_update(result, {"shot_id": "S2", "take_id": "reviewed", "status": "accepted", "sequence_index": 1})
        self.assertNotIn("S2", result["stale_takes"])
        self.assertIn("S1", result["stale_takes"])

    def test_revision_rejects_missing_authority_stale_hash_and_collision(self):
        state = self.state()
        variants = [self.revision(state, sequence_indices={"S1": 2}),
                    self.revision(state, deactivate_shots=["unknown"]),
                    self.revision(state, deactivate_shots=["S1"], approval_source=""),
                    self.revision(state, deactivate_shots=["S1"], expected_state_hash="stale"),
                    self.revision(state, sequence_indices={"S1": True})]
        for revision in variants:
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                cs.revise_state(state, revision)

    def test_separate_contexts_do_not_merge_subjective_state(self):
        reality = self.state()
        dream = cs.apply_update(cs.initial("dream-context"), {"shot_id": "D1", "take_id": "DT1", "status": "accepted",
                  "sequence_index": 1, "canon_patch": {"owner": "C"}})
        self.assertEqual(reality["current_state"]["owner"], "B")
        self.assertEqual(dream["current_state"]["owner"], "C")

    def test_selection_provenance_is_bound_and_preserved(self):
        provenance = {"cut_sha256": "a" * 64, "selection_fingerprint": "b" * 64,
                      "event_ids": ["E1"], "acceptance_source": "explicit cut-v2 review"}
        update = {"shot_id": "S1", "take_id": "selected-v2", "sequence_index": 1, "status": "accepted",
                  "selection_provenance": provenance}
        result = cs.apply_update(self.state(), update)
        self.assertEqual(result["shots"]["S1"]["versions"][-1]["selection_provenance"], provenance)
        update["selection_provenance"] = {"cut_sha256": "missing"}
        with self.assertRaises(ValueError):
            cs.apply_update(self.state(), update)

    def test_cli_revision_writes_valid_history_and_rejects_stale_retry(self):
        with tempfile.TemporaryDirectory(prefix="ledger-revision-cli-") as folder:
            root = Path(folder)
            state, revision = root / "state.json", root / "revision.json"
            cs.atomic_write(state, self.state())
            # Use the on-disk snapshot, including its initialization timestamps.
            cs.atomic_write(revision, self.revision(cs.read_json(state), deactivate_shots=["S1"]))
            command = [sys.executable, "-B", str(Path(cs.__file__)), "revise", str(state), str(revision)]
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            snapshot = state.read_bytes()
            self.assertEqual(cs.validate_state(cs.read_json(state)), [])
            retry = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(retry.returncode, 2)
            self.assertEqual(state.read_bytes(), snapshot)


class SelectionTests(unittest.TestCase):
    def packet(self):
        return {"cut_version": "v1", "cut_file": "/fixture.mp4", "cut_sha256": "a" * 64,
                "time_origin": "first decoded video frame, seconds, out exclusive", "fragments": [{
                    "id": "F1", "take_id": "T1", "source_file": "/source.mp4", "source_sha256": "b" * 64,
                    "source_in": 1.0, "source_out": 2.0, "timeline_in": 0.0, "timeline_out": 1.0, "time_mapping": "normal"}],
                "events": [{"id": "E1", "context_id": "objective", "story_position": "before E2", "status": "shown",
                    "fragment_ids": ["F1"], "evidence": "observed handoff", "authority_source": "script-v1"}]}

    def test_valid_structure_never_claims_media_approval(self):
        result = selection.check(self.packet())
        self.assertEqual(result["status"], "passed_structure_only")
        self.assertIn("actual media and hashes", result["not_checked"])

    def test_ellipsis_can_retain_event_without_shown_fragment(self):
        packet = self.packet()
        packet["events"][0].update(status="omitted_but_retained", fragment_ids=[], evidence="approved before/after implication")
        self.assertTrue(selection.check(packet)["ok"])

    def test_unresolved_event_is_not_a_pass(self):
        packet = self.packet()
        packet["events"][0]["status"] = "unresolved"
        self.assertFalse(selection.check(packet)["ok"])
        self.assertEqual(selection.check(packet)["status"], "unverified")

    def test_story_removal_requires_authority(self):
        packet = self.packet()
        packet["events"][0]["status"] = "removed_by_approved_story_change"
        self.assertFalse(selection.check(packet)["ok"])
        packet["events"][0]["approval_source"] = "explicit story-change approval"
        self.assertTrue(selection.check(packet)["ok"])

    def test_changed_fragment_marks_same_event_for_recheck(self):
        before = self.packet()
        after = copy.deepcopy(before)
        after["fragments"][0]["source_in"] = 1.5
        after["fragments"][0]["timeline_out"] = 0.5
        result = selection.check(after, before)
        self.assertEqual(result["changed_event_ids"], ["E1"])
        self.assertNotEqual(result["selection_fingerprint"], selection.check(before)["selection_fingerprint"])

    def test_one_event_can_have_multiple_fragments_without_duplicate_event(self):
        packet = self.packet()
        fragment = copy.deepcopy(packet["fragments"][0])
        fragment.update(id="F2", timeline_in=1, timeline_out=2)
        packet["fragments"].append(fragment)
        packet["events"][0]["fragment_ids"].append("F2")
        self.assertTrue(selection.check(packet)["ok"])

    def test_deleted_event_is_reported_as_changed(self):
        before = self.packet()
        after = copy.deepcopy(before)
        after["events"] = []
        result = selection.check(after, before)
        self.assertEqual(result["changed_event_ids"], ["E1"])
        self.assertFalse(result["ok"])

    def test_invalid_previous_does_not_get_a_comparison_pass(self):
        self.assertFalse(selection.check(self.packet(), {"events": []})["ok"])

    def test_bad_values_fail_cleanly(self):
        for field, value in (("source_in", True), ("source_out", float("nan")), ("timeline_out", 0)):
            packet = self.packet()
            packet["fragments"][0][field] = value
            self.assertFalse(selection.check(packet)["ok"])
        packet = self.packet()
        packet["events"][0]["status"] = []
        self.assertFalse(selection.check(packet)["ok"])


class NativeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ffmpeg, cls.ffprobe = take.find_binary("ffmpeg"), take.find_binary("ffprobe")
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def fixture(self, root, timing="setpts=PTS", audio=False):
        source = root / "vertical.mkv"
        pixels = b"".join(bytes((i * 3, 10, 20)) * (36 * 64) for i in range(60))
        command = [self.ffmpeg, "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "36x64",
                   "-framerate", "60", "-i", "pipe:0"]
        if audio:
            command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=2", "-c:a", "pcm_s16le"]
        command += ["-vf", timing, "-fps_mode", "vfr", "-c:v", "ffv1", "-pix_fmt", "bgr0", str(source)]
        subprocess.run(command, input=pixels, capture_output=True, check=True)
        return source

    def red(self, path):
        return subprocess.check_output([self.ffmpeg, "-v", "error", "-i", str(path), "-vf", "crop=1:1:0:0",
                                        "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"])[0]

    def test_native_dense_keeps_portrait_dimensions_and_pixels(self):
        with tempfile.TemporaryDirectory(prefix="native-review-test-") as folder:
            root = Path(folder)
            source = self.fixture(root)
            result = take.dense_frame_burst(self.ffmpeg, source, root, 0, .2, 60, 120, "native")
            info = take.metadata(take.probe(self.ffprobe, Path(result["frames"][0])))
            self.assertEqual((info["video"]["width"], info["video"]["height"]), (36, 64))
            self.assertEqual(result["frame_resolution"], "native")
            self.assertEqual([self.red(x) for x in result["frames"]], list(range(0, 36, 3)))

    def test_true_last_frame_not_format_duration_or_fixed_offset(self):
        with tempfile.TemporaryDirectory(prefix="tail-review-test-") as folder:
            root = Path(folder)
            source = self.fixture(root, audio=True)
            result = take.extract_last_frame(self.ffmpeg, self.ffprobe, source, root / "last.png")
            self.assertEqual(result["decoded_frame_index"], 59)
            self.assertEqual(self.red(root / "last.png"), 177)

    def test_vfr_nonzero_start_and_exclusive_outpoint(self):
        with tempfile.TemporaryDirectory(prefix="tail-vfr-test-") as folder:
            root = Path(folder)
            source = self.fixture(root, "setpts='(if(lt(N,30),N,30+(N-30)*2))/60/TB+2/TB'")
            result = take.extract_last_frame(self.ffmpeg, self.ffprobe, source, root / "out.png", .5)
            self.assertEqual(result["decoded_frame_index"], 29)
            self.assertEqual(self.red(root / "out.png"), 87)
            result = take.extract_last_frame(self.ffmpeg, self.ffprobe, source, root / "last.png")
            self.assertEqual(result["decoded_frame_index"], 59)
            self.assertEqual(self.red(root / "last.png"), 177)

    def test_decimal_boundary_excludes_exact_point_after_nonzero_origin(self):
        with tempfile.TemporaryDirectory(prefix="decimal-boundary-test-") as folder:
            root = Path(folder)
            source = self.fixture(root, "setpts=PTS+2/TB")
            result = take.extract_last_frame(self.ffmpeg, self.ffprobe, source, root / "boundary.png", .3)
            self.assertEqual(result['decoded_frame_index'], 17)
            burst = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, 0, .3, 30)
            self.assertEqual(burst['frame_count'], 18)


if __name__ == "__main__":
    unittest.main()
