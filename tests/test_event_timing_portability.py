"""Exercise the optional timing CLI in isolation, with no media tools or siblings."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skill/shotloom/modules/edit-delivery/scripts/event_timing.py"


class PortableTimingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="shotloom-timing-")
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name) / "no media tools or sibling skills"
        self.folder.mkdir()
        self.helper = self.folder / "event_timing.py"
        shutil.copyfile(HELPER, self.helper)

    def run_helper(self, *arguments):
        before = {p.relative_to(self.folder): p.read_bytes() for p in self.folder.rglob("*") if p.is_file()}
        result = subprocess.run([sys.executable, "-I", "-B", str(self.helper), *arguments],
                                cwd=self.folder, env=dict(os.environ, PATH="", PYTHONDONTWRITEBYTECODE="1"),
                                text=True, capture_output=True, check=False)
        after = {p.relative_to(self.folder): p.read_bytes() for p in self.folder.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "The arithmetic helper must not change or create files")
        return result

    def test_map_cli_marks_partial_word_without_media_tools(self):
        result = self.run_helper("map", "--source-in", "10", "--source-out", "12",
                                 "--timeline-in", "3", "--rate", "2", "--event-in", "9", "--event-out", "11")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("calculation_only", data["status"])
        self.assertEqual("partial_requires_review", data["disposition"])
        self.assertEqual(["3", "7/2"], [point["exact"] for point in data["timeline_event"]])
        self.assertIn("audible words", data["not_verified"])

    def test_sound_cli_keeps_unknown_and_measured_delay_distinct(self):
        for options, expected, basis in (((), "391/200", "nominal_offset_unverified"),
                                          (("--measured-delay", ".08"), "15/8", "declared_measured_offset")):
            with self.subTest(options=options):
                result = self.run_helper("sfx", "--target", "2", "--anchor-offset", ".045", *options)
                self.assertEqual(0, result.returncode, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual("calculation_only", data["status"])
                self.assertEqual(expected, data["placement"]["exact"])
                self.assertEqual(basis, data["basis"])
                self.assertIn("listening", data["not_verified"])

    def test_unsupported_nonlinear_rate_has_no_success_payload(self):
        result = self.run_helper("sfx", "--target", "2", "--anchor-offset", ".045", "--rate", "ramp")
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("invalid_input", json.loads(result.stderr)["status"])
