from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skill" / "shotloom" / "scripts" / "take_dialogue_audit.py"
SPEC = importlib.util.spec_from_file_location("shotloom_dialogue_audit", MODULE_PATH)
assert SPEC and SPEC.loader
dialogue_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dialogue_audit)


class DialogueAuditTests(unittest.TestCase):
    def write_json(self, payload: object) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
        with handle:
            json.dump(payload, handle, ensure_ascii=False)
        return Path(handle.name)

    def test_normalization_ignores_punctuation(self) -> None:
        self.assertEqual(dialogue_audit.normalize("店交给你了。"), dialogue_audit.normalize("店，交给你了"))

    def test_load_and_timing(self) -> None:
        path = self.write_json(
            {
                "text": "店交给你了。",
                "segments": [{"start": 1.1, "end": 2.9, "text": "店交给你了。"}],
            }
        )
        text, segments = dialogue_audit.load_transcript(path)
        self.assertEqual("店交给你了。", text)
        self.assertEqual((1.1, 2.9), dialogue_audit.timing(segments))
        path.unlink()

    def test_both_entrypoints_are_identical_after_relocation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dialogue relocation ") as folder:
            root = Path(folder) / "shotloom"
            for relative in ("scripts/take_dialogue_audit.py", "modules/review-continuity/scripts/take_dialogue_audit.py"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / "skill/shotloom" / relative, target)
            path = root / "transcript.json"
            for payload, expected, code in (({"text": "店交给你了。"}, "店交给你了。", 0),
                                             ({"text": "店交给你了。"}, "店交给我了。", 1),
                                             ({"text": ""}, "", 2),
                                             ({"text": "店交给你了。", "segments": [{"start": "bad"}]}, "店交给你了。", 2)):
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                results = [subprocess.run([sys.executable, "-I", "-B", str(root / relative), str(path),
                                          "--expected", expected, "--json"], text=True, capture_output=True, cwd=folder)
                           for relative in ("scripts/take_dialogue_audit.py", "modules/review-continuity/scripts/take_dialogue_audit.py")]
                self.assertEqual([result.returncode for result in results], [code, code])
                self.assertEqual(results[0].stdout, results[1].stdout)
                self.assertEqual(results[0].stderr, results[1].stderr)

    def test_invalid_root_is_rejected(self) -> None:
        path = self.write_json(["not", "an", "object"])
        with self.assertRaises(ValueError):
            dialogue_audit.load_transcript(path)
        path.unlink()


if __name__ == "__main__":
    unittest.main()
