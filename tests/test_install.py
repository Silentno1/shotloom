from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash") and shutil.which("tar"), "Bash/tar unavailable")
class InstallTests(unittest.TestCase):
    def install(self, destination, *flags):
        return subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "--target", str(destination), *flags],
                              capture_output=True, text=True, cwd=ROOT)

    def test_install_refuse_and_repeated_force_preserve_distinct_backups(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "path with spaces"
            result = self.install(target)
            self.assertEqual(0, result.returncode, result.stderr)
            installed = target / "shotloom"
            self.assertTrue((installed / "modules/director/scripts/director_style.py").is_file())
            self.assertTrue((installed / "LICENSE").is_file())
            marker = installed / "user-note.txt"
            marker.write_text("keep v1", encoding="utf-8")
            self.assertNotEqual(0, self.install(target).returncode)
            self.assertEqual("keep v1", marker.read_text())
            self.assertEqual(0, self.install(target, "--force").returncode)
            marker.write_text("keep v2", encoding="utf-8")
            self.assertEqual(0, self.install(target, "--force").returncode)
            backups = list(target.glob("shotloom.backup-*/shotloom/user-note.txt"))
            self.assertEqual({"keep v1", "keep v2"}, {p.read_text() for p in backups})
            self.assertFalse(list(installed.rglob("*.pyc")))

    def test_missing_option_value_is_usage_error(self):
        result = subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "--target"], capture_output=True, text=True)
        self.assertEqual(2, result.returncode)

    def test_self_install_is_refused_without_touching_source(self):
        source = ROOT / "skill/shotloom/SKILL.md"
        original = source.read_bytes()
        result = self.install(ROOT / "skill", "--force")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("source folder itself", result.stderr)
        self.assertEqual(original, source.read_bytes())
