from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill/shotloom/modules/director/scripts"))
from runtime_tools import find_binary


class RuntimeToolTests(unittest.TestCase):
    def test_missing_binary_reports_optional_no_install(self):
        with patch.dict(os.environ, {}, clear=True), patch("runtime_tools.shutil.which", return_value=None):
            with self.assertRaisesRegex(FileNotFoundError, "no dependencies were installed"):
                find_binary("ffmpeg")

    def test_explicit_override_is_used_without_shell_parsing(self):
        with patch.dict(os.environ, {"SHOTLOOM_FFPROBE": "path with spaces/probe"}, clear=True), patch("runtime_tools.shutil.which", return_value="resolved-probe") as which:
            self.assertEqual("resolved-probe", find_binary("ffprobe"))
            which.assert_called_once_with("path with spaces/probe")

    def test_invalid_override_never_falls_back(self):
        with patch.dict(os.environ, {"SHOTLOOM_FFMPEG": "wrong"}, clear=True), patch("runtime_tools.shutil.which", return_value=None) as which:
            with self.assertRaisesRegex(FileNotFoundError, "no fallback"):
                find_binary("ffmpeg")
            which.assert_called_once_with("wrong")

    def test_unsupported_tool_is_not_resolved(self):
        with self.assertRaises(ValueError):
            find_binary("anything")
