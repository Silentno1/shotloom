"""CI must distinguish passing discovered tests from skipped media suites."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("shotloom_test_runner", Path(__file__).resolve().parents[1] / "scripts/run_tests.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class TestRunnerTests(unittest.TestCase):
    def run_sample(self, strict, *, skip=False, class_skip=False, fail=False, empty=False):
        class Sample(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                if class_skip:
                    raise unittest.SkipTest("fixture class unavailable")

            def test_sample(self):
                if skip:
                    self.skipTest("fixture unavailable")
                if fail:
                    self.fail("fixture failure")

        suite = unittest.TestSuite([] if empty else [Sample("test_sample")])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(runner.unittest.defaultTestLoader, "discover", return_value=suite), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.run_suite(Path("fixture-suite"), strict)
        return code, out.getvalue() + err.getvalue()

    def test_strict_pass_runs_every_discovered_test(self):
        code, output = self.run_sample(True)
        self.assertEqual(code, 0)
        self.assertIn("discovered=1, run=1, skip_events=0", output)

    def test_strict_rejects_individual_skip(self):
        code, output = self.run_sample(True, skip=True)
        self.assertEqual(code, 1)
        self.assertIn("fixture unavailable", output)

    def test_strict_rejects_entire_class_skip(self):
        code, output = self.run_sample(True, class_skip=True)
        self.assertEqual(code, 1)
        self.assertIn("discovered=1, run=0, skip_events=1", output)

    def test_portable_reports_optional_skip(self):
        code, output = self.run_sample(False, class_skip=True)
        self.assertEqual(code, 0)
        self.assertIn("fixture class unavailable", output)

    def test_empty_and_failing_suites_fail(self):
        for strict in (False, True):
            self.assertEqual(self.run_sample(strict, empty=True)[0], 1)
            self.assertEqual(self.run_sample(strict, fail=True)[0], 1)

    def test_missing_required_media_tools_fail(self):
        with mock.patch.object(runner.shutil, "which", return_value=None), self.assertRaisesRegex(ValueError, "cannot skip"):
            runner.check_media_tools()

    def test_required_tool_versions_are_recorded(self):
        out = io.StringIO()
        result = subprocess.CompletedProcess([], 0, stdout="test media version\n", stderr="")
        with mock.patch.dict(os.environ, {"SHOTLOOM_FFMPEG": "custom-ffmpeg", "SHOTLOOM_FFPROBE": "custom-ffprobe"}), mock.patch.object(runner.shutil, "which", side_effect=lambda name: name), mock.patch.object(runner.subprocess, "run", return_value=result) as run, contextlib.redirect_stdout(out):
            runner.check_media_tools()
        self.assertEqual(run.call_count, 2)
        self.assertEqual([call.args[0][0] for call in run.call_args_list], ["custom-ffmpeg", "custom-ffprobe"])
        self.assertEqual(out.getvalue().count("test media version"), 2)


if __name__ == "__main__":
    unittest.main()
