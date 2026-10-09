#!/usr/bin/env python3
"""Compare normalized wording; this does not approve speech quality or listening."""

from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import sys
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text).casefold()


def load_transcript(path: Path) -> tuple[str, list[dict[str, object]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("transcript JSON root must be an object")
    text = data.get("text", "")
    if not isinstance(text, str):
        raise ValueError("transcript text must be a string")
    segments = data.get("segments", [])
    if not isinstance(segments, list):
        raise ValueError("transcript segments must be a list")
    if any(not isinstance(item, dict) for item in segments):
        raise ValueError("each transcript segment must be an object")
    return text, segments


def timing(segments: list[dict[str, object]]) -> tuple[float | None, float | None]:
    starts, ends = [], []
    for segment in segments:
        values = {}
        for key in ("start", "end"):
            if key not in segment:
                continue
            value = segment[key]
            if isinstance(value, bool) or not isinstance(value, (str, int, float)):
                raise ValueError(f"segment {key} must be finite non-negative seconds")
            try:
                number = float(value)
            except (ValueError, OverflowError) as exc:
                raise ValueError(f"segment {key} must be finite non-negative seconds") from exc
            if not math.isfinite(number) or number < 0:
                raise ValueError(f"segment {key} must be finite non-negative seconds")
            values[key] = number
        if "start" in values and "end" in values and values["end"] < values["start"]:
            raise ValueError("segment end precedes its start")
        if "start" in values:
            starts.append(values["start"])
        if "end" in values:
            ends.append(values["end"])
    return min(starts) if starts else None, max(ends) if ends else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Whisper-style transcript JSON")
    parser.add_argument("--expected", required=True, help="approved dialogue")
    parser.add_argument("--duration", type=float, help="media duration in seconds")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        if not normalize(args.expected):
            raise ValueError("expected dialogue is empty")
        if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
            raise ValueError("media duration must be positive finite seconds")
        actual, segments = load_transcript(args.path)
        first, last = timing(segments)
        if args.duration is not None and any(t is not None and t > args.duration for t in (first, last)):
            raise ValueError("transcript timing exceeds media duration")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected_norm = normalize(args.expected)
    actual_norm = normalize(actual)
    exact = expected_norm == actual_norm
    matcher = difflib.SequenceMatcher(None, expected_norm, actual_norm)
    differences = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            differences.append({"operation": tag, "expected": expected_norm[i1:i2], "actual": actual_norm[j1:j2]})
    payload = {"status": "PASS" if exact else "FAIL", "expected": args.expected, "actual": actual,
               "similarity": round(matcher.ratio(), 3), "first_speech": first, "last_speech": last,
               "differences": differences, "scope": "normalized_wording_only",
               "not_checked": ["actual listening", "voice identity", "lip sync", "creative acceptance"]}
    if args.duration is not None and first is not None and last is not None:
        payload["head_before_speech"] = round(first, 3)
        payload["tail_after_speech"] = round(args.duration - last, 3)
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"expected: {args.expected}\nactual:   {actual}\nsimilarity: {matcher.ratio():.3f}")
        for key in ("first_speech", "last_speech", "head_before_speech", "tail_after_speech"):
            if payload.get(key) is not None:
                print(f"{key}: {payload[key]:.2f}s")
        print("PASS: normalized wording matches" if exact else "FAIL: wording mismatch; verify names, accents, and homophones")
        for difference in differences:
            print(f"- {difference['operation']}: expected[{difference['expected']}] actual[{difference['actual']}]")
        print("Scope: wording only; no listening, voice, sync or creative approval.")
    return 0 if exact else 1


if __name__ == "__main__":
    raise SystemExit(main())
