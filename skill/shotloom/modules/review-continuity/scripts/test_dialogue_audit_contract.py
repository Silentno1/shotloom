"""Wording checks must not manufacture a pass from empty or malformed evidence."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import take_dialogue_audit as audit


class DialogueContractTests(unittest.TestCase):
    def run_audit(self, payload, expected="店交给你了。", extra=()):
        with tempfile.TemporaryDirectory(prefix="dialogue-contract-") as folder:
            path = Path(folder) / "transcript.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            argv = ["audit", str(path), "--expected", expected, "--json", *extra]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = audit.main()
            return status, out.getvalue(), err.getvalue()

    def test_casefold_and_punctuation_match_with_limited_scope(self):
        status, out, err = self.run_audit({"text": "STRASSE!"}, "Straße.")
        self.assertEqual(status, 0, err)
        data = json.loads(out)
        self.assertEqual(data["scope"], "normalized_wording_only")
        self.assertIn("actual listening", data["not_checked"])
        self.assertIsNone(data["first_speech"])

    def test_empty_expected_is_not_a_pass(self):
        for expected in ("", "  ", "，。!"):
            with self.subTest(expected=expected):
                status, _, err = self.run_audit({"text": ""}, expected)
                self.assertEqual(status, 2)
                self.assertIn("empty", err)

    def test_empty_actual_and_different_words_fail(self):
        for actual in ("", "店就交给你了。"):
            with self.subTest(actual=actual):
                status, out, _ = self.run_audit({"text": actual})
                self.assertEqual(status, 1)
                self.assertEqual(json.loads(out)["status"], "FAIL")

    def test_invalid_transcript_shapes_fail_cleanly(self):
        for payload in ([], None, {"text": None}, {"text": 3}, {"segments": {}}, {"segments": ["bad"]}):
            with self.subTest(payload=payload):
                status, _, err = self.run_audit(payload)
                self.assertEqual(status, 2)
                self.assertNotIn("Traceback", err)

    def test_bad_timing_is_not_silently_ignored(self):
        for value in ("bad", "nan", "inf", -1, True, None, [], 10 ** 400):
            for key in ("start", "end"):
                with self.subTest(value=value, key=key):
                    status, _, err = self.run_audit({"text": "店交给你了。", "segments": [{key: value}]})
                    self.assertEqual(status, 2)
                    self.assertNotIn("Traceback", err)

    def test_reversed_or_out_of_media_timing_is_rejected(self):
        for segment in ({"start": 2, "end": 1}, {"start": 1, "end": 3}, {"start": 3}):
            with self.subTest(segment=segment):
                status, _, _ = self.run_audit({"text": "店交给你了。", "segments": [segment]}, extra=["--duration", "2"])
                self.assertEqual(status, 2)

    def test_invalid_media_duration_is_rejected(self):
        for duration in ("0", "-1", "nan", "inf"):
            with self.subTest(duration=duration):
                status, _, _ = self.run_audit({"text": "店交给你了。"}, extra=["--duration", duration])
                self.assertEqual(status, 2)

    def test_valid_timing_reports_head_and_tail(self):
        status, out, err = self.run_audit({"text": "店交给你了。", "segments": [
            {"start": "1.1", "end": 2.9}]}, extra=["--duration", "4"])
        self.assertEqual(status, 0, err)
        data = json.loads(out)
        self.assertEqual(data["head_before_speech"], 1.1)
        self.assertEqual(data["tail_after_speech"], 1.1)


if __name__ == "__main__":
    unittest.main()
