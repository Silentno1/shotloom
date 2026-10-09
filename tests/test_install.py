from pathlib import Path
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash") and shutil.which("tar"), "Bash/tar unavailable")
class InstallTests(unittest.TestCase):
    def install(self, destination, *flags, env=None):
        return subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "--target", str(destination), *flags],
                              capture_output=True, text=True, cwd=ROOT, env=env)

    def state_root(self, target):
        target = target.resolve()
        return target.with_name(f".{target.name}.shotloom-installer")

    def assert_only_active_skill(self, target):
        self.assertEqual(["shotloom/SKILL.md"],
                         sorted(str(path.relative_to(target)) for path in target.rglob("SKILL.md")))

    def tool_override(self, folder, name, body):
        tool_bin = Path(folder) / "test tools"
        tool_bin.mkdir()
        tool = tool_bin / name
        tool.write_text("#!/bin/bash\nset -eu\n" + body, encoding="utf-8")
        tool.chmod(0o755)
        return dict(os.environ, PATH=str(tool_bin) + os.pathsep + os.environ["PATH"])

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
            result = self.install(target, "--force")
            self.assertEqual(0, result.returncode, result.stderr)
            marker.write_text("keep v2", encoding="utf-8")
            result = self.install(target, "--force")
            self.assertEqual(0, result.returncode, result.stderr)
            state = self.state_root(target)
            backups = list(state.glob("backup-*/shotloom/user-note.txt"))
            self.assertEqual({"keep v1", "keep v2"}, {p.read_text() for p in backups})
            self.assertTrue(all((path.parent / "SKILL.md").is_file() for path in backups))
            self.assertFalse(state.is_relative_to(target))
            self.assertFalse(list(state.glob("stage-*")))
            self.assert_only_active_skill(target)
            self.assertFalse(list(installed.rglob("*.pyc")))

    def test_copy_failure_preserves_install_and_retains_stage_outside_scan_root(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            self.assertEqual(0, self.install(target).returncode)
            marker = target / "shotloom/user-note.txt"
            marker.write_text("keep original", encoding="utf-8")
            real_tar = shlex.quote(shutil.which("tar"))
            # Let the complete staged skill appear, then report a source-read failure.
            env = self.tool_override(folder, "tar", f'{real_tar} "$@"\n'
                                     'case " $* " in *" -cf "*) exit 73 ;; esac\n')
            result = self.install(target, "--force", env=env)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Copy failed", result.stderr)
            self.assertEqual("keep original", marker.read_text())
            state = self.state_root(target)
            self.assertEqual(1, len(list(state.glob("stage-*/shotloom/SKILL.md"))))
            self.assertFalse(list(state.glob("backup-*")))
            self.assert_only_active_skill(target)

    def test_failed_swap_restores_original_and_keeps_stage_outside_scan_root(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            self.assertEqual(0, self.install(target).returncode)
            marker = target / "shotloom/user-note.txt"
            marker.write_text("restore this", encoding="utf-8")
            real_mv = shlex.quote(shutil.which("mv"))
            env = self.tool_override(folder, "mv",
                                     'case "$1" in *".shotloom-installer/stage-"*) exit 74 ;; esac\n'
                                     f'exec {real_mv} "$@"\n')
            result = self.install(target, "--force", env=env)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Previous installation restored", result.stderr)
            self.assertEqual("restore this", marker.read_text())
            self.assertEqual(1, len(list(self.state_root(target).glob("stage-*/shotloom/SKILL.md"))))
            self.assert_only_active_skill(target)

    def test_failed_backup_move_leaves_original_install_untouched(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            self.assertEqual(0, self.install(target).returncode)
            marker = target / "shotloom/user-note.txt"
            marker.write_text("keep original", encoding="utf-8")
            real_mv = shlex.quote(shutil.which("mv"))
            env = self.tool_override(folder, "mv",
                                     'case "$2" in *".shotloom-installer/backup-"*) exit 75 ;; esac\n'
                                     f'exec {real_mv} "$@"\n')
            result = self.install(target, "--force", env=env)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("keep original", marker.read_text())
            self.assert_only_active_skill(target)

    def test_failed_restore_retains_original_backup_and_reports_its_path(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            self.assertEqual(0, self.install(target).returncode)
            marker = target / "shotloom/user-note.txt"
            marker.write_text("recover this backup", encoding="utf-8")
            real_mv = shlex.quote(shutil.which("mv"))
            env = self.tool_override(folder, "mv",
                                     'case "$1" in *".shotloom-installer/"*) exit 76 ;; esac\n'
                                     f'exec {real_mv} "$@"\n')
            result = self.install(target, "--force", env=env)
            self.assertNotEqual(0, result.returncode)
            state = self.state_root(target)
            backups = list(state.glob("backup-*/shotloom/user-note.txt"))
            self.assertEqual(1, len(backups))
            self.assertEqual("recover this backup", backups[0].read_text())
            self.assertIn("Restore failed", result.stderr)
            self.assertIn(str(backups[0].parent), result.stderr)
            self.assertEqual(1, len(list(state.glob("stage-*/shotloom/SKILL.md"))))
            self.assertFalse(list(target.rglob("SKILL.md")))

    def test_symlinked_target_keeps_state_outside_resolved_scan_root(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "real skills"
            target.mkdir()
            alias = Path(folder) / "skills alias"
            alias.symlink_to(target, target_is_directory=True)
            self.assertEqual(0, self.install(alias).returncode)
            result = self.install(alias, "--force")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(1, len(list(self.state_root(target).glob("backup-*/shotloom/SKILL.md"))))
            self.assert_only_active_skill(target)

    def test_state_symlink_into_scan_root_is_refused_before_copying(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            target.mkdir()
            state = self.state_root(target)
            state.symlink_to(target, target_is_directory=True)
            result = self.install(target)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("installer storage", result.stderr)
            self.assertEqual([], list(target.iterdir()))

    def test_cross_device_storage_is_refused_without_moving_original(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-install-") as folder:
            target = Path(folder) / "skills"
            self.assertEqual(0, self.install(target).returncode)
            marker = target / "shotloom/user-note.txt"
            marker.write_text("keep original", encoding="utf-8")
            env = self.tool_override(folder, "stat",
                                     'case "$3" in *".shotloom-installer") printf "2\\n" ;; '
                                     '*) printf "1\\n" ;; esac\n')
            result = self.install(target, "--force", env=env)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("same filesystem", result.stderr)
            self.assertEqual("keep original", marker.read_text())
            self.assertFalse(list(self.state_root(target).glob("backup-*")))
            self.assert_only_active_skill(target)

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
