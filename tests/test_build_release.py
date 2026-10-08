from pathlib import Path
import hashlib
import importlib.util
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class ReleaseTests(unittest.TestCase):
    def test_one_folder_package_has_complete_runtime_and_license(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-release-") as folder:
            path, digest = BUILD.build(Path(folder) / "path with spaces")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            with zipfile.ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(all(n.startswith("shotloom/") and ".." not in Path(n).parts for n in names))
                self.assertIn("shotloom/SKILL.md", names)
                self.assertIn("shotloom/LICENSE", names)
                self.assertIn("shotloom/modules/director/scripts/runtime_tools.py", names)
                self.assertEqual(5, sum(n.endswith("/WORKFLOW.md") for n in names))
                self.assertEqual(1, sum(n.endswith("/SKILL.md") for n in names))
                self.assertFalse(any("__pycache__" in n or n.endswith((".pyc", ".DS_Store")) for n in names))
                expected = {"shotloom/" + p.relative_to(BUILD.SKILL).as_posix()
                            for p in BUILD.SKILL.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                            and p.suffix != ".pyc" and p.name != ".DS_Store"}
                self.assertEqual(expected, set(names))

    def test_existing_archive_is_never_replaced(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-release-") as folder:
            path, digest = BUILD.build(Path(folder))
            with self.assertRaises(FileExistsError):
                BUILD.build(Path(folder))
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_symlink_preflight_does_not_leave_partial_release(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-release-") as folder:
            source = Path(folder) / "source"
            source.mkdir()
            (source / "SKILL.md").write_text('version: "0.2.0-alpha"\n', encoding="utf-8")
            (source / "linked").symlink_to(Path(folder) / "missing")
            output = Path(folder) / "output"
            with patch.object(BUILD, "SKILL", source), self.assertRaisesRegex(ValueError, "symlinks"):
                BUILD.build(output)
            self.assertFalse(output.exists())
