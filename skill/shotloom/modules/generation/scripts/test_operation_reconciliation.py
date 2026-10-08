#!/usr/bin/env python3
import copy
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import operation_reconciliation_check as checker


class ReconciliationTests(unittest.TestCase):
    def packet(self):
        ref = {"label": "ref-A", "slot": 1, "source_id": "node-A",
               "candidate_id": "candidate-2", "content_version": "immutable-v2"}
        return {
            "planned_settings": {"duration_s": 6, "model": "test-model", "mode": "reference"},
            "observed_settings": {"duration_s": 6, "model": "test-model", "mode": "reference"},
            "prompt_duration_s": 6,
            "readback_evidence": "test fixture only; request-r2 snapshot",
            "segments": [{"id": "beat1", "track": "picture", "start_s": 0, "end_s": 4}],
            "planned_references": [{**ref, "primary_role": "composition"}],
            "observed_references": [copy.deepcopy(ref)],
        }

    def assert_status(self, packet, expected):
        result = checker.check(packet)
        self.assertEqual(result["status"], expected, result)
        return result

    def test_consistent_operation_and_unused_handle(self):
        result = self.assert_status(self.packet(), "matched_structurally")
        self.assertIn("media quality", result["not_checked"])

    def test_prompt_8_4_seconds_vs_setting_6(self):
        packet = self.packet()
        packet["prompt_duration_s"] = 8.4
        result = self.assert_status(packet, "blocked")
        self.assertIn("prompt duration", " ".join(result["errors"]))

    def test_twenty_second_plan_vs_fifteen_second_operation(self):
        packet = self.packet()
        for name in ("planned_settings", "observed_settings"):
            packet[name]["duration_s"] = 15
        packet["prompt_duration_s"] = 15
        packet["segments"] = [{"id": f"shot-{i}", "track": "picture", "start_s": i, "end_s": i+1}
                              for i in range(20)]
        self.assert_status(packet, "blocked")

    def test_actual_duration_differs_from_plan(self):
        packet = self.packet()
        packet["observed_settings"]["duration_s"] = 5
        self.assert_status(packet, "blocked")

    def test_invalid_duration_types_and_nonfinite(self):
        for value in (True, "6", -1, 0, float("nan"), float("inf")):
            for field in ("planned_settings", "observed_settings"):
                with self.subTest(value=value, field=field):
                    packet = self.packet()
                    packet[field]["duration_s"] = value
                    self.assert_status(packet, "blocked")

    def test_invalid_explicit_prompt_duration(self):
        for value in (None, False, "6", float("nan")):
            packet = self.packet()
            packet["prompt_duration_s"] = value
            self.assert_status(packet, "blocked")

    def test_omitted_prompt_duration_is_not_invented(self):
        packet = self.packet()
        del packet["prompt_duration_s"]
        self.assert_status(packet, "matched_structurally")

    def test_missing_actual_readback_is_unverified(self):
        for field in ("observed_settings", "observed_references", "readback_evidence"):
            packet = self.packet()
            del packet[field]
            self.assert_status(packet, "unverified")

    def test_missing_observed_setting_is_unverified(self):
        packet = self.packet()
        del packet["observed_settings"]["model"]
        self.assert_status(packet, "unverified")

    def test_wrong_model_or_mode(self):
        for field in ("model", "mode"):
            packet = self.packet()
            packet["observed_settings"][field] = "different"
            self.assert_status(packet, "blocked")

    def test_other_tracks_may_overlap(self):
        packet = self.packet()
        packet["segments"].append({"id": "sound1", "track": "sound", "start_s": 0, "end_s": 6})
        self.assert_status(packet, "matched_structurally")

    def test_same_track_overlap_requires_declaration_on_both(self):
        packet = self.packet()
        packet["segments"].append({"id": "beat2", "track": "picture", "start_s": 3, "end_s": 6})
        self.assert_status(packet, "blocked")
        packet["segments"][0]["overlap_group"] = "intentional dissolve"
        self.assert_status(packet, "blocked")
        packet["segments"][1]["overlap_group"] = "intentional dissolve"
        self.assert_status(packet, "matched_structurally")

    def test_nested_overlaps_cannot_hide_behind_adjacent_interval(self):
        packet = self.packet()
        packet["segments"] = [
            {"id": "long", "track": "picture", "start_s": 0, "end_s": 6},
            {"id": "short1", "track": "picture", "start_s": 1, "end_s": 2},
            {"id": "short2", "track": "picture", "start_s": 3, "end_s": 4}]
        result = self.assert_status(packet, "blocked")
        self.assertEqual(len(result["errors"]), 2)

    def test_adjacent_shots_and_gaps_are_valid(self):
        packet = self.packet()
        for start in (4, 5):
            packet["segments"] = packet["segments"][:1] + [
                {"id": "beat2", "track": "picture", "start_s": start, "end_s": 6}]
            self.assert_status(packet, "matched_structurally")

    def test_bad_interval_and_duplicate_id(self):
        for start, end in ((-1, 3), (2, 2), (3, 2), (True, 2), (0, float("inf"))):
            packet = self.packet()
            packet["segments"][0].update(start_s=start, end_s=end)
            self.assert_status(packet, "blocked")
        packet = self.packet()
        packet["segments"].append({"id": "beat1", "track": "sound", "start_s": 0, "end_s": 2})
        self.assert_status(packet, "blocked")

    def test_selected_candidate_version_source_and_order_changes(self):
        for field, value in (("candidate_id", "candidate-3"), ("content_version", "v3"),
                             ("source_id", "node-B"), ("slot", 2), ("label", "ref-B")):
            with self.subTest(field=field):
                packet = self.packet()
                packet["observed_references"][0][field] = value
                self.assert_status(packet, "blocked")

    def test_extra_or_missing_reference(self):
        packet = self.packet()
        packet["observed_references"] = []
        self.assert_status(packet, "blocked")
        packet = self.packet()
        packet["observed_references"].append({**packet["observed_references"][0], "label": "ref-B", "slot": 2})
        self.assert_status(packet, "blocked")

    def test_duplicate_label_or_slot(self):
        for field in ("planned_references", "observed_references"):
            packet = self.packet()
            packet[field].append(copy.deepcopy(packet[field][0]))
            self.assert_status(packet, "blocked")

    def test_same_content_can_fill_distinct_explicit_slots(self):
        packet = self.packet()
        for field in ("planned_references", "observed_references"):
            packet[field].append({**packet[field][0], "label": "ref-B", "slot": 2})
        packet["planned_references"][1]["primary_role"] = "lighting"
        self.assert_status(packet, "matched_structurally")

    def test_no_references_is_explicit_valid_case(self):
        packet = self.packet()
        packet["planned_references"] = []
        packet["observed_references"] = []
        self.assert_status(packet, "matched_structurally")

    def test_missing_candidate_version_or_role_is_not_a_pass(self):
        for field in ("candidate_id", "content_version", "primary_role"):
            packet = self.packet()
            del packet["planned_references"][0][field]
            self.assert_status(packet, "blocked")

    def test_malformed_containers_do_not_crash(self):
        self.assert_status([], "blocked")
        for field in ("planned_settings", "observed_settings", "segments",
                      "planned_references", "observed_references"):
            packet = self.packet()
            packet[field] = "wrong"
            self.assert_status(packet, "blocked")
        for field in ("segments", "planned_references", "observed_references"):
            packet = self.packet()
            packet[field] = [None, [], True]
            self.assert_status(packet, "blocked")

    def test_invalid_slot_and_overlap_group_do_not_crash(self):
        packet = self.packet()
        packet["planned_references"][0]["slot"] = True
        self.assert_status(packet, "blocked")
        packet = self.packet()
        packet["segments"][0]["overlap_group"] = []
        self.assert_status(packet, "blocked")

    def test_cli_exit_status_for_match_missing_readback_and_conflict(self):
        for status in ("matched_structurally", "unverified", "blocked"):
            packet = self.packet()
            if status == "unverified":
                del packet["readback_evidence"]
            if status == "blocked":
                packet["prompt_duration_s"] = 8.4
            output = io.StringIO()
            with patch("sys.argv", ["checker", "fixture.json"]), \
                    patch.object(checker.Path, "read_text", return_value=json.dumps(packet)), \
                    redirect_stdout(output):
                self.assertEqual(checker.main(), 0 if status == "matched_structurally" else 2)
            self.assertEqual(json.loads(output.getvalue())["status"], status)


if __name__ == "__main__":
    unittest.main()
