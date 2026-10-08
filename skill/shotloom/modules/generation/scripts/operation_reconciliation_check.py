#!/usr/bin/env python3
"""Compare supplied video-operation plans with independent readback; no platform calls."""

import argparse
import json
import math
from pathlib import Path


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def check(data):
    errors, unknown = [], []
    unchecked = ["prompt semantics", "asset approval", "readback authenticity/freshness", "media quality"]

    def result():
        return {"status": "blocked" if errors else "unverified" if unknown else "matched_structurally",
                "errors": errors, "unverified": unknown, "not_checked": unchecked}

    if not isinstance(data, dict):
        errors.append("packet must be an object")
        return result()
    plan = data.get("planned_settings")
    if not isinstance(plan, dict):
        errors.append("planned_settings must be an object")
        plan = {}
    duration = plan.get("duration_s")
    valid_duration = number(duration) and duration > 0
    if not valid_duration:
        errors.append("planned_settings.duration_s must be a positive finite number")
    observed = data.get("observed_settings")
    if observed is None:
        unknown.append("observed_settings missing")
    elif not isinstance(observed, dict):
        errors.append("observed_settings must be an object")
    else:
        for key, value in plan.items():
            if key not in observed:
                unknown.append(f"observed setting missing: {key}")
            elif key == "duration_s":
                actual = observed[key]
                if not number(actual) or actual <= 0:
                    errors.append("observed_settings.duration_s must be a positive finite number")
                elif valid_duration and not math.isclose(value, actual, rel_tol=0, abs_tol=1e-6):
                    errors.append("setting mismatch: duration_s")
            elif value != observed[key] or type(value) is not type(observed[key]):
                errors.append(f"setting mismatch: {key}")
    if not nonempty(data.get("readback_evidence")):
        unknown.append("independent readback_evidence missing")
    if "prompt_duration_s" in data:
        value = data["prompt_duration_s"]
        if not number(value) or value <= 0:
            errors.append("prompt_duration_s must be a positive finite number when supplied")
        elif valid_duration and not math.isclose(value, duration, rel_tol=0, abs_tol=1e-6):
            errors.append("prompt duration differs from planned generation duration")

    segments = data.get("segments", [])
    if not isinstance(segments, list):
        errors.append("segments must be an array")
        segments = []
    valid_segments, ids = [], set()
    for index, segment in enumerate(segments):
        prefix = f"segments[{index}]"
        if not isinstance(segment, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not all(nonempty(segment.get(k)) for k in ("id", "track")):
            errors.append(f"{prefix} requires nonempty id and track")
            continue
        if segment["id"] in ids:
            errors.append(f"duplicate segment id: {segment['id']}")
        ids.add(segment["id"])
        start, end = segment.get("start_s"), segment.get("end_s")
        if not number(start) or not number(end) or not 0 <= start < end:
            errors.append(f"{prefix} requires finite 0 <= start_s < end_s")
            continue
        if valid_duration and end > duration + 1e-6:
            errors.append(f"{prefix} ends beyond generation duration")
        group = segment.get("overlap_group")
        if group is not None and not nonempty(group):
            errors.append(f"{prefix}.overlap_group must be a nonempty string when supplied")
        valid_segments.append(segment)
    for index, current in enumerate(valid_segments):
        for prior in valid_segments[:index]:
            if current["track"] != prior["track"]:
                continue
            if min(current["end_s"], prior["end_s"]) <= max(current["start_s"], prior["start_s"]) + 1e-6:
                continue
            group = current.get("overlap_group")
            if not nonempty(group) or group != prior.get("overlap_group"):
                errors.append(f"undeclared same-track overlap: {prior['id']} / {current['id']}")

    fields = ("label", "source_id", "candidate_id", "content_version")

    def references(key, planned=False):
        items = data.get(key)
        if items is None and not planned:
            unknown.append(f"{key} missing")
            return None
        if not isinstance(items, list):
            errors.append(f"{key} must be an array (empty when no references)")
            return None
        mapped, slots = {}, set()
        for index, item in enumerate(items):
            prefix = f"{key}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            required = fields + (("primary_role",) if planned else ())
            if not all(nonempty(item.get(k)) for k in required):
                errors.append(f"{prefix} requires nonempty {', '.join(required)}")
                continue
            slot = item.get("slot")
            if type(slot) is not int or slot < 1:
                errors.append(f"{prefix}.slot must be a positive integer")
                continue
            if item["label"] in mapped or slot in slots:
                errors.append(f"{prefix} duplicate label or slot")
            mapped[item["label"]] = item
            slots.add(slot)
        return mapped

    expected_refs = references("planned_references", planned=True)
    actual_refs = references("observed_references")
    if expected_refs is not None and actual_refs is not None:
        if expected_refs.keys() != actual_refs.keys():
            errors.append("reference label set mismatch")
        for label in expected_refs.keys() & actual_refs.keys():
            for field in fields + ("slot",):
                if expected_refs[label][field] != actual_refs[label][field]:
                    errors.append(f"reference {label} mismatch: {field}")
    return result()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet")
    args = parser.parse_args()
    try:
        output = check(json.loads(Path(args.packet).read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        output = {"status": "blocked", "errors": [str(exc)]}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["status"] == "matched_structurally" else 2


if __name__ == "__main__":
    raise SystemExit(main())
