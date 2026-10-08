from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skill" / "shotloom" / "scripts" / "prompt_lint.py"
SPEC = importlib.util.spec_from_file_location("shotloom_prompt_lint", MODULE_PATH)
assert SPEC and SPEC.loader
prompt_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prompt_lint)


class PromptLintTests(unittest.TestCase):
    def test_seedance_20_golden_prompt_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "seedance-20-video.md").read_text(encoding="utf-8")
        errors = prompt_lint.lint_video(text, "seedance-20", True, False)
        errors.extend(prompt_lint.reference_mapping_warning(text))
        self.assertEqual([], errors)

    def test_seedance_25_golden_prompt_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "seedance-25-video.md").read_text(encoding="utf-8")
        errors = prompt_lint.lint_video(text, "seedance-25", True, False)
        errors.extend(prompt_lint.reference_mapping_warning(text))
        self.assertEqual([], errors)

    def test_seedream_golden_prompt_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "seedream-50-first-frame.md").read_text(encoding="utf-8")
        errors = prompt_lint.lint_image(text, "seedream-50")
        errors.extend(prompt_lint.reference_mapping_warning(text))
        self.assertEqual([], errors)

    def test_seedance_20_rejects_over_duration(self) -> None:
        text = "总时长：16 秒。参考职责。进入状态。动作。机位。结束状态。环境声。禁止。验收检查。"
        errors = prompt_lint.lint_video(text, "seedance-20", False, False)
        self.assertTrue(any("15" in error for error in errors))

    def test_seedance_25_rejects_timeline_gap(self) -> None:
        text = (
            "总时长：12 秒。参考职责。进入状态。动作。机位。结束状态。环境声。禁止。验收。"
            "0-4 秒：开始。5-12 秒：结束。"
        )
        errors = prompt_lint.lint_video(text, "seedance-25", False, False)
        self.assertTrue(any("空档" in error for error in errors))

    def test_text_to_video_does_not_require_reference_map(self) -> None:
        text = (
            "总时长：8 秒。进入状态：空旷站台。动作：一张车票被风吹起。"
            "摄影机固定。结束状态：车票停在轨道边。环境声只有风声。"
            "禁止人物和字幕。验收检查：车票运动连续。"
        )
        self.assertEqual([], prompt_lint.lint_video(text, "seedance-20", False, False))

    def test_reference_token_without_role_map_is_rejected(self) -> None:
        errors = prompt_lint.reference_mapping_warning("Use @Image1 and make a video.")
        self.assertTrue(errors)

    def test_director_card_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "director-card.md").read_text(encoding="utf-8")
        self.assertEqual([], prompt_lint.lint_director(text))

    def test_multi_person_director_card_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "director-card.md").read_text(encoding="utf-8")
        self.assertEqual([], prompt_lint.lint_director(text, True))

    def test_director_cli_does_not_require_model(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "--kind",
                "director",
                str(ROOT / "examples" / "golden-scene" / "director-card.md"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_voice_contract_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "voice-contract.md").read_text(encoding="utf-8")
        self.assertEqual([], prompt_lint.lint_audio(text))

    def test_project_state_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "project-state.md").read_text(encoding="utf-8")
        self.assertEqual([], prompt_lint.lint_state(text))

    def test_take_review_fixtures_pass(self) -> None:
        for name in ("take-01-review.md", "take-02-review.md"):
            with self.subTest(name=name):
                text = (ROOT / "examples" / "golden-scene" / name).read_text(encoding="utf-8")
                self.assertEqual([], prompt_lint.lint_review(text))

    def test_handoff_fixture_passes(self) -> None:
        text = (ROOT / "examples" / "golden-scene" / "review-and-handoff.md").read_text(encoding="utf-8")
        self.assertEqual([], prompt_lint.lint_handoff(text))

    def test_dialogue_mode_requires_listener(self) -> None:
        text = (
            "总时长：8秒。进入状态。动作。摄影机固定。结尾状态。环境声。"
            "台词：你好。语速平稳。不要字幕。禁止额外人物。验收检查。"
        )
        errors = prompt_lint.lint_video(text, "seedance-20", False, False, dialogue=True)
        self.assertTrue(any("听者" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
