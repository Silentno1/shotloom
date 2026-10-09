from __future__ import annotations

import subprocess
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_package_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_skill_has_no_runtime_dependency_file(self) -> None:
        self.assertFalse((ROOT / "requirements.txt").exists())

    def test_entry_routes_directly_and_keeps_old_links_working(self) -> None:
        skill = ROOT / "skill/shotloom"
        routes = (
            "story-development.md", "scene-direction.md", "performance.md", "continuity.md",
            "review-and-handoff.md", "take-review.md", "post-production-handoff.md",
            "models/seedance-20.md", "models/seedance-25.md",
        )
        for route in routes:
            path = skill / "references" / route
            body = path.read_text(encoding="utf-8")
            self.assertLessEqual(len(body.splitlines()), 6)
            targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)
            self.assertTrue(targets)
            for target in targets:
                self.assertTrue((path.parent / target).is_file(), route)
        entry = (skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("modules/director/references/screenwriting-development.md", entry)
        self.assertIn("modules/edit-delivery/references/post-production.md", entry)

    def test_chinese_task_keywords_are_in_description(self) -> None:
        entry = (ROOT / "skill/shotloom/SKILL.md").read_text(encoding="utf-8")
        description = next(line for line in entry.splitlines() if line.startswith("description:"))
        for keyword in ("AI 影视", "分镜", "短剧", "漫剧", "审片"):
            self.assertIn(keyword, description)

    def test_profile_retrieval_returns_only_the_requested_profile(self) -> None:
        scripts = ROOT / "skill/shotloom/modules/director/scripts"
        for helper in ("director_style.py", "director_methods.py"):
            result = subprocess.run([sys.executable, "-B", str(scripts / helper), "profile", "nora-ephron"],
                                    text=True, capture_output=True, check=True)
            data = json.loads(result.stdout)
            profile = data["profile"] if helper == "director_methods.py" else data
            self.assertEqual(profile["id"], "nora-ephron")
            self.assertNotIn("profiles", data)
            self.assertLess(len(result.stdout.encode("utf-8")), 20000)


if __name__ == "__main__":
    unittest.main()
