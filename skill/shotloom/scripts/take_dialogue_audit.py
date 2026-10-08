#!/usr/bin/env python3
"""Compare approved dialogue with a Whisper-style transcript."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text).casefold()


def load_transcript(path: Path) -> tuple[str, list[dict[str, object]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("transcript JSON root must be an object")
    transcript = str(data.get("text", ""))
    raw_segments = data.get("segments", [])
    segments = raw_segments if isinstance(raw_segments, list) else []
    return transcript, [item for item in segments if isinstance(item, dict)]


def timing(segments: list[dict[str, object]]) -> tuple[float | None, float | None]:
    starts: list[float] = []
    ends: list[float] = []
    for segment in segments:
        try:
            if "start" in segment:
                starts.append(float(segment["start"]))
            if "end" in segment:
                ends.append(float(segment["end"]))
        except (TypeError, ValueError):
            continue
    return (min(starts) if starts else None, max(ends) if ends else None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Whisper-style transcript JSON")
    parser.add_argument("--expected", required=True, help="approved dialogue")
    parser.add_argument("--duration", type=float, help="media duration in seconds")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if not normalize(args.expected):
        print("ERROR: expected dialogue is empty", file=sys.stderr)
        return 2
    try:
        actual, segments = load_transcript(args.path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected_norm = normalize(args.expected)
    actual_norm = normalize(actual)
    similarity = difflib.SequenceMatcher(None, expected_norm, actual_norm).ratio()
    first, last = timing(segments)
    exact = expected_norm == actual_norm
    differences: list[dict[str, str]] = []
    matcher = difflib.SequenceMatcher(None, expected_norm, actual_norm)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            differences.append(
                {
                    "operation": tag,
                    "expected": expected_norm[i1:i2],
                    "actual": actual_norm[j1:j2],
                }
            )

    payload: dict[str, object] = {
        "status": "PASS" if exact else "FAIL",
        "expected": args.expected,
        "actual": actual,
        "similarity": round(similarity, 3),
        "first_speech": first,
        "last_speech": last,
        "differences": differences,
    }
    if args.duration is not None and first is not None and last is not None:
        payload["head_before_speech"] = round(first, 3)
        payload["tail_after_speech"] = round(max(0.0, args.duration - last), 3)

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"expected: {args.expected}")
        print(f"actual:   {actual}")
        print(f"similarity: {similarity:.3f}")
        if first is not None:
            print(f"first_speech: {first:.2f}s")
        if last is not None:
            print(f"last_speech: {last:.2f}s")
        if "tail_after_speech" in payload:
            print(f"tail_after_speech: {payload['tail_after_speech']:.2f}s")
        print("PASS: normalized wording matches" if exact else "FAIL: wording mismatch; verify names, accents, and homophones")
        for difference in differences:
            print(
                f"- {difference['operation']}: expected[{difference['expected']}] "
                f"actual[{difference['actual']}]"
            )
    return 0 if exact else 1


if __name__ == "__main__":
    raise SystemExit(main())
