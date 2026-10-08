#!/usr/bin/env python3
"""Extract structural evidence locations without interpreting or scoring a screenplay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HEADING = re.compile(r"^(?:#{1,6}\s+|(?:INT\.|EXT\.|内景|外景|场景|第\s*\d+\s*场))(.+)$", re.I)
DIALOGUE = re.compile(r"^\s*([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9_· .-]{0,30})\s*[：:]\s*(.+)$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script")
    parser.add_argument("--output")
    args = parser.parse_args()
    path = Path(args.script)
    text = path.read_text(encoding="utf-8")
    scenes, dialogue = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if HEADING.match(line):
            scenes.append({"line": number, "text": line})
        match = DIALOGUE.match(raw)
        if match:
            dialogue.append({"line": number, "speaker": match.group(1).strip(), "text": match.group(2).strip()})
    result = {
        "status": "evidence-only",
        "warning": "This inventory is not screenplay interpretation and must not auto-select or lock a directing method.",
        "source": str(path.resolve()),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "line_count": len(text.splitlines()),
        "scene_headings": scenes,
        "dialogue_lines": dialogue,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
