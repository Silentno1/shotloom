from __future__ import annotations

import importlib.util
import json
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

    def test_invalid_root_is_rejected(self) -> None:
        path = self.write_json(["not", "an", "object"])
        with self.assertRaises(ValueError):
            dialogue_audit.load_transcript(path)
        path.unlink()


if __name__ == "__main__":
    unittest.main()
