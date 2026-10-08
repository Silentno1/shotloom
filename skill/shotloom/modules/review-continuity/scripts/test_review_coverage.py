"""Coverage/disposition behavior, not keyword presence or visual-quality claims."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import review_coverage_check as review


HASH = "a" * 64


def packet():
    return {
        "schema_version": 1,
        "source": {"path": "/fixture.mp4", "sha256": HASH, "duration_seconds": 10},
        "time_origin": "first decoded video frame; seconds; out exclusive",
        "baseline_ref": "fixture-only approved baseline, minor harmless details allowed",
        "scope": {"kind": "take", "range": [0, 10], "modalities": ["picture", "sound"]},
        "coverage": [
            {"modality": "picture", "range": [0, 10], "method": "normal_playback",
             "source_sha256": HASH, "evidence": ["fixture playback record"]},
            {"modality": "sound", "range": [0, 10], "method": "normal_listening",
             "source_sha256": HASH, "evidence": ["fixture listening record"]},
        ],
        "required_checks": ["handoff"],
        "checks": [{"id": "handoff", "targets": ["cup", "A", "B"], "trigger": "object transfer",
                    "range": [4, 5], "source_sha256": HASH, "status": "checked",
                    "observed": "A holds cup, both contact it, B receives; A releases",
                    "evidence": ["fixture native frames and playback 4-5"]}],
        "findings": [], "verdict": "retain",
    }


def finding(disposition="retain", severity="minor"):
    result = {"id": "F1", "range": [4, 5], "source_sha256": HASH,
              "subject": "cup", "observation": "small background edge variation",
              "requirement_ref": "fixture tolerance", "impact": "no identity/story effect or downstream use",
              "rationale": "permitted at intended playback size", "evidence": ["fixture frames"],
              "severity": severity, "salience": "detail_only", "disposition": disposition}
    if disposition in {"repair", "regenerate"}:
        result["next_action"] = "bounded authorized treatment, preserve required handoff"
    return result


class CoverageTests(unittest.TestCase):
    def test_complete_record_is_consistency_only_not_acceptance(self):
        p = packet()
        before = copy.deepcopy(p)
        result = review.check(p)
        self.assertEqual(result["status"], "passed_consistency_only")
        self.assertFalse(result["acceptance_granted"])
        self.assertIn("actual source file hash", result["not_checked"])
        self.assertEqual(p, before)

    def test_gap_between_viewed_chunks_cannot_pass(self):
        p = packet()
        first = p["coverage"][0]
        first["range"] = [0, 4]
        p["coverage"].append({**first, "range": [4.1, 10]})
        result = review.check(p)
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["uncovered_ranges"]["picture"], [[4, 4.1]])

    def test_overlapping_contiguous_chunks_cover_without_double_counting(self):
        self.assertEqual(review.gaps([0, 10], [[5, 10], [0, 6], [0, 3]]), [])
        self.assertEqual(review.gaps([2, 4], [[0, 2], [5, 10]]), [[2, 4]])

    def test_even_all_frames_do_not_replace_normal_playback(self):
        for method in ("overview", "sampled_frames", "source_frames", "slow_playback"):
            p = packet()
            p["coverage"][0]["method"] = method
            with self.subTest(method=method):
                self.assertEqual(review.check(p)["uncovered_ranges"]["picture"], [[0, 10]])

    def test_spectrum_or_missing_listening_cannot_approve_sound(self):
        p = packet()
        p["coverage"][1]["method"] = "native_detail"
        self.assertEqual(review.check(p)["status"], "unverified")

    def test_picture_only_scope_is_allowed_but_does_not_claim_sound(self):
        p = packet()
        p["scope"]["modalities"] = ["picture"]
        p["coverage"] = p["coverage"][:1]
        result = review.check(p)
        self.assertTrue(result["ok"])
        self.assertNotIn("sound", result["uncovered_ranges"])
        self.assertFalse(result["acceptance_granted"])

    def test_targeted_scope_does_not_require_unrelated_intervals(self):
        p = packet()
        p["scope"].update(kind="targeted", range=[4, 5])
        for entry in p["coverage"]:
            entry["range"] = [4, 5]
        self.assertTrue(review.check(p)["ok"])
        p["scope"]["kind"] = "take"
        self.assertEqual(review.check(p)["status"], "failed")

    def test_extracted_but_not_inspected_risk_checkpoint_is_unverified(self):
        p = packet()
        p["checks"][0].update(status="unverified", observed="")
        self.assertEqual(review.check(p)["status"], "unverified")
        p["checks"] = []
        self.assertEqual(review.check(p)["status"], "unverified")

    def test_checked_label_without_observation_is_not_enough(self):
        p = packet()
        p["checks"][0]["observed"] = ""
        self.assertFalse(review.check(p)["ok"])

    def test_not_applicable_requires_reason_not_blank_bypass(self):
        p = packet()
        p["checks"][0]["status"] = "not_applicable"
        self.assertEqual(review.check(p)["status"], "failed")
        p["checks"][0]["reason"] = "fixture approved ellipsis; no visible handoff; aftermath checked separately"
        self.assertTrue(review.check(p)["ok"])

    def test_low_risk_clip_can_have_no_extra_checkpoints_with_reason(self):
        p = packet()
        p.update(required_checks=[], checks=[], check_selection_reason="static title card; normal view covers intended function")
        self.assertTrue(review.check(p)["ok"])

    def test_stale_version_in_coverage_checks_or_findings_is_rejected(self):
        for container in ("coverage", "checks", "findings"):
            p = packet()
            p["findings"] = [finding()]
            p[container][0]["source_sha256"] = "b" * 64
            with self.subTest(container=container):
                self.assertEqual(review.check(p)["status"], "failed")

    def test_missing_viewing_evidence_leaves_gap(self):
        p = packet()
        p["coverage"][0]["evidence"] = []
        self.assertEqual(review.check(p)["uncovered_ranges"]["picture"], [[0, 10]])

    def test_minor_tolerated_finding_can_be_retained_without_new_exception(self):
        p = packet()
        p["findings"] = [finding()]
        self.assertTrue(review.check(p)["ok"])

    def test_major_retention_needs_specific_acceptance_not_minor_tolerance(self):
        p = packet()
        p["findings"] = [finding(severity="critical")]
        self.assertEqual(review.check(p)["status"], "failed")
        p["findings"][0]["acceptance_ref"] = "fixture explicit acceptance for this hash only"
        self.assertTrue(review.check(p)["ok"])
        self.assertFalse(review.check(p)["acceptance_granted"])

    def test_repair_plan_is_not_an_already_repaired_source(self):
        p = packet()
        p["findings"] = [finding("repair")]
        self.assertEqual(review.check(p)["status"], "failed")
        p["verdict"] = "repair"
        self.assertTrue(review.check(p)["ok"])

    def test_regenerate_requires_evidenced_finding_and_plan(self):
        p = packet()
        p["verdict"] = "regenerate"
        self.assertFalse(review.check(p)["ok"])
        p["findings"] = [finding("regenerate", "major")]
        self.assertTrue(review.check(p)["ok"])
        del p["findings"][0]["next_action"]
        self.assertFalse(review.check(p)["ok"])

    def test_repair_only_cannot_hide_another_finding_requiring_regeneration(self):
        p = packet()
        p["verdict"] = "repair"
        p["findings"] = [finding("repair"), {**finding("regenerate", "critical"), "id": "F2"}]
        self.assertEqual(review.check(p)["status"], "failed")
        p["verdict"] = "regenerate"
        self.assertTrue(review.check(p)["ok"])

    def test_known_failure_can_be_reported_while_other_dimensions_unverified(self):
        p = packet()
        p["verdict"] = "regenerate"
        p["findings"] = [finding("regenerate", "critical")]
        p["coverage"].pop()
        result = review.check(p)
        self.assertEqual(result["status"], "unverified")
        self.assertFalse(result["errors"])

    def test_uncertain_impact_is_not_no_defect(self):
        p = packet()
        p["findings"] = [{**finding(), "salience": "unknown"}]
        self.assertEqual(review.check(p)["status"], "unverified")

    def test_duplicate_or_out_of_scope_checks_fail(self):
        p = packet()
        p["checks"].append(copy.deepcopy(p["checks"][0]))
        self.assertFalse(review.check(p)["ok"])
        p = packet()
        p["scope"].update(kind="targeted", range=[6, 7])
        self.assertFalse(review.check(p)["ok"])

    def test_bad_shapes_fail_without_tracebacks(self):
        variants = [None, [], {}, {"schema_version": True}]
        for location, key, value in [
            ("scope", "kind", []), ("scope", "modalities", [{}]),
            ("scope", "range", [False, 10]), ("source", "duration_seconds", float("nan")),
            ("source", "duration_seconds", float("inf")),
        ]:
            p = packet()
            p[location][key] = value
            variants.append(p)
        p = packet()
        p["verdict"] = []
        variants.append(p)
        p = packet()
        p["findings"] = [{**finding(), "severity": []}]
        variants.append(p)
        for p in variants:
            with self.subTest(p=p):
                self.assertEqual(review.check(p)["status"], "failed")

    def test_read_only_cli_verifies_hash_and_rejects_replaced_file(self):
        with tempfile.TemporaryDirectory(prefix="coverage-cli-") as folder:
            root = Path(folder)
            source = root / "fixture.bin"
            source.write_bytes(b"test-only source hash fixture, not media review")
            p = packet()
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
            p["source"].update(path=str(source), sha256=actual)
            for row in p["coverage"] + p["checks"]:
                row["source_sha256"] = actual
            record = root / "review.json"
            record.write_text(json.dumps(p), encoding="utf-8")
            initial = record.read_bytes()
            command = [sys.executable, "-B", str(Path(review.__file__)), str(record), "--verify-source"]
            completed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertNotIn("actual source file hash", result["not_checked"])
            self.assertFalse(result["acceptance_granted"])
            source.write_bytes(b"different version")
            changed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(changed.returncode, 2)
            self.assertEqual(record.read_bytes(), initial)


if __name__ == "__main__":
    unittest.main()
