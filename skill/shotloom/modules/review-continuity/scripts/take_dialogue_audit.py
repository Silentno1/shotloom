#!/usr/bin/env python3
"""Compare an approved line with a Whisper-style transcript and report timing."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text).lower()


def load_transcript(path: Path) -> tuple[str, list[dict[str, object]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("transcript JSON root must be an object")
    text = str(data.get("text", ""))
    segments = data.get("segments", [])
    if not isinstance(segments, list):
        segments = []
    return text, [item for item in segments if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Whisper-style audio.json")
    parser.add_argument("--expected", required=True, help="approved dialogue text")
    parser.add_argument("--duration", type=float, help="generated file duration in seconds")
    args = parser.parse_args()

    try:
        actual, segments = load_transcript(args.path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected_norm = normalize(args.expected)
    actual_norm = normalize(actual)
    ratio = difflib.SequenceMatcher(None, expected_norm, actual_norm).ratio()

    starts = [float(item["start"]) for item in segments if "start" in item]
    ends = [float(item["end"]) for item in segments if "end" in item]
    first = min(starts) if starts else None
    last = max(ends) if ends else None

    print(f"expected: {args.expected}")
    print(f"actual:   {actual}")
    print(f"similarity: {ratio:.3f}")
    if first is not None:
        print(f"first_speech: {first:.2f}s")
    if last is not None:
        print(f"last_speech: {last:.2f}s")
    if args.duration is not None and first is not None and last is not None:
        print(f"head_before_speech: {first:.2f}s")
        print(f"tail_after_speech: {max(0.0, args.duration - last):.2f}s")

    if expected_norm == actual_norm:
        print("PASS: normalized transcript matches approved dialogue")
        return 0

    print("FAIL: wording mismatch; manually verify names and homophones")
    matcher = difflib.SequenceMatcher(None, expected_norm, actual_norm)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            print(
                f"- {tag}: expected[{expected_norm[i1:i2]}] "
                f"actual[{actual_norm[j1:j2]}]"
            )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
