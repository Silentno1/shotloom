#!/usr/bin/env python3
"""Deterministic prompt-schema and input-envelope checks; never a semantic quality score."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


BASE_FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]
REF_FIELDS = ["subject_definitions", "summary", "retention_analysis", "detailed_description", "overall_soundscape", "non_diegetic_music"]


def read_manifest(path: str | None) -> dict:
    if not path:
        return {"first_frames": 0, "last_frames": 0, "reference_images": [], "reference_videos": [], "reference_audios": []}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    return normalize_manifest(value)


def normalize_manifest(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ValueError("manifest must be an object")
    result = {}
    for key in ("first_frames", "last_frames"):
        item = value.get(key, 0)
        if type(item) is not int or item < 0:
            raise ValueError(f"{key} must be a non-negative integer")
        result[key] = item
    for key in ("reference_images", "reference_videos", "reference_audios"):
        item = value.get(key, [])
        if not isinstance(item, list) or not all(isinstance(entry, dict) for entry in item):
            raise ValueError(f"{key} must be an array of objects")
        result[key] = item
    return result


def field_order(text: str) -> list[str]:
    known = set(BASE_FIELDS + REF_FIELDS)
    return [match.group(1) for match in re.finditer(r"(?m)^([a-z_]+)\s*:", text) if match.group(1) in known]


def field_sections(text: str, expected: list[str]) -> dict[str, str]:
    matches = [
        match for match in re.finditer(r"(?m)^([a-z_]+)\s*:\s*", text)
        if match.group(1) in expected
    ]
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = text[match.end():end].strip()
    return sections


def label_numbers(text: str, label: str) -> set[int]:
    return {int(n) for n in re.findall(rf"<{label}\s+(\d+)>", text, re.I)}


def check_h3(text: str, mode: str, duration: float, manifest: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if not isinstance(text, str):
        return ["prompt must be text"], warnings
    if mode not in ("T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA"):
        return ["unsupported H3 mode"], warnings
    if type(duration) not in (int, float) or not math.isfinite(duration):
        return ["H3 duration must be a finite number"], warnings
    try:
        manifest = normalize_manifest(manifest)
    except ValueError as exc:
        return [str(exc)], warnings
    if not 4 <= duration <= 15:
        errors.append("H3 output duration must be between 4 and 15 seconds")
    expected = REF_FIELDS if mode == "Ref2VA" else BASE_FIELDS
    actual = field_order(text)
    if actual != expected:
        errors.append(f"field order must be exactly {expected}; got {actual}")
    sections = field_sections(text, expected)
    for field in expected:
        if not sections.get(field):
            errors.append(f"required H3 field is empty: {field}")
    if re.search(r"@(?:图片|视频|音频)\s*\d+", text):
        errors.append("Seedance-style @ media labels are not valid in the H3 contract")

    first_count, last_count = manifest["first_frames"], manifest["last_frames"]
    images = manifest["reference_images"]
    videos = manifest["reference_videos"]
    audios = manifest["reference_audios"]
    for kind, items in (("image", images), ("video", videos), ("audio", audios)):
        ids = [item.get("id") for item in items]
        if any(type(value) is not int or value < 1 for value in ids):
            errors.append(f"reference {kind} ids must be positive integers")
        elif ids != list(range(1, len(ids) + 1)):
            errors.append(f"reference {kind} ids must be unique and consecutive from 1")
        for index, item in enumerate(items, 1):
            if not isinstance(item.get("role"), str) or not item["role"].strip():
                errors.append(f"reference {kind} {index} needs a non-empty role")
    expected_keyframes = {"T2VA": (0, 0), "I2VA": (1, 0), "FL2VA": (1, 1), "L2VA": (0, 1)}
    if mode in expected_keyframes and (first_count, last_count) != expected_keyframes[mode]:
        errors.append(f"{mode} requires first_frames,last_frames={expected_keyframes[mode]}")
    if mode != "Ref2VA" and (images or videos or audios):
        errors.append(f"{mode} cannot use Ref2VA reference media in this manifest")
    if mode == "Ref2VA" and (first_count or last_count):
        errors.append("Ref2VA manifest cannot also declare FL2VA keyframe inputs")

    if len(images) > 9:
        errors.append("H3 Ref2VA allows at most 9 reference images")
    if len(videos) > 3:
        errors.append("H3 Ref2VA allows at most 3 reference videos")
    standalone_audios = [item for item in audios if "source_video_id" not in item]
    video_by_id = {item.get("id"): item for item in videos if type(item.get("id")) is int}
    linked_video_ids = []
    for item in audios:
        if "source_video_id" not in item:
            continue
        source_id = item["source_video_id"]
        source = video_by_id.get(source_id) if type(source_id) is int else None
        if source is None:
            errors.append("audio source_video_id must identify an existing reference video")
            continue
        linked_video_ids.append(source_id)
        span, source_duration = item.get("duration"), source.get("duration")
        if type(span) not in (int, float) or type(source_duration) not in (int, float) or not math.isfinite(span) or not math.isfinite(source_duration) or not 0 < span <= source_duration:
            errors.append("enabled video audio duration must be positive and fit its source video")
    if len(linked_video_ids) != len(set(linked_video_ids)):
        errors.append("define each enabled source-video audio track once")
    if len(standalone_audios) > 3:
        errors.append("H3 Ref2VA allows at most 3 reference audios")
    if first_count + last_count + len(images) + len(videos) + len(standalone_audios) > 12:
        errors.append("H3 input files exceed the 12-file total")
    for kind, items in (("video", videos), ("audio", standalone_audios)):
        durations = []
        for index, item in enumerate(items, 1):
            value = item.get("duration")
            if type(value) not in (int, float) or not math.isfinite(value):
                errors.append(f"reference {kind} {index} needs numeric duration")
                continue
            durations.append(float(value))
            if not 2 <= value <= 15:
                errors.append(f"reference {kind} {index} duration must be 2–15 seconds")
        if sum(durations) > 15 + 1e-9:
            errors.append(f"reference {kind} total duration exceeds 15 seconds")
    if mode == "Ref2VA" and audios and not (images or videos):
        errors.append("reference audio cannot be the only Ref2VA input")

    picture_count = first_count + last_count + len(images)
    for label, count in (("Picture", picture_count), ("Video", len(videos)), ("Audio", len(audios))):
        used = label_numbers(text, label)
        if any(number < 1 or number > count for number in used):
            errors.append(f"{label} label exceeds manifest count {count}: {sorted(used)}")
    description_field = "detailed_description" if mode == "Ref2VA" else "integrated_multimodal_description"
    description = sections.get(description_field, "")
    # Definitions/retention legitimately cite [Shot N]; only timed cut blocks
    # outside the main timeline are structurally unambiguous misplaced shots.
    for field, body in sections.items():
        if field != description_field and re.search(r"\[Shot\s+\d+\]\s+At\s+\d{2}:\d{2}", body, re.I):
            errors.append(f"H3 timed shot blocks belong only in {description_field}, not {field}")
    shots = list(re.finditer(r"\[Shot\s+(\d+)\]", description, re.I))
    if shots:
        numbers = [int(m.group(1)) for m in shots]
        if numbers != list(range(1, len(numbers) + 1)):
            errors.append("shot numbers must start at 1 and be consecutive")
        if re.match(r"\s+At\b", description[shots[0].end():], re.I):
            errors.append("[Shot 1] must not have a timestamp")
        times = []
        for match in shots[1:]:
            tail = description[match.end():]
            time_match = re.match(r"\s+At\s+(\d{2}):(\d{2}\.\d{3})(?=$|[\s,;，；]|[.!?。！？](?=\s|$))", tail, re.I)
            if time_match is None:
                errors.append("every shot after Shot 1 needs an At MM:SS.mmm cut timestamp")
                continue
            if float(time_match.group(2)) >= 60:
                errors.append("cut timestamp must use MM:SS.mmm with seconds below 60")
            seconds = int(time_match.group(1)) * 60 + float(time_match.group(2))
            times.append(seconds)
            if seconds <= 0 or seconds >= duration:
                errors.append(f"shot cut {seconds:.3f}s must fall inside the output duration")
        if times != sorted(times) or len(times) != len(set(times)):
            errors.append("shot cut timestamps must be strictly increasing")
    if not shots:
        errors.append("H3 description requires [Shot 1], including a single-shot description")
    final_shot = len(shots) or 1
    alignment = {
        "I2VA": "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.",
        "FL2VA": f"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot {final_shot}) aligns with the {duration:.2f}-second mark of the target video.",
        "L2VA": f"How the reference pictures align with the target video — <Picture 1> (from [Shot {final_shot}]) aligns with the {duration:.2f}-second mark of the target video.",
    }
    if mode in alignment and not text.startswith(alignment[mode] + "\n\n"):
        errors.append(f"{mode} requires the official first-line keyframe alignment and a blank line")
    if mode == "Ref2VA":
        defined = label_numbers(sections.get("subject_definitions", ""), "Subject")
        used = label_numbers("\n".join(value for key, value in sections.items() if key != "subject_definitions"), "Subject")
        if defined and defined != set(range(1, max(defined) + 1)):
            errors.append("Subject ids must be consecutive from 1")
        if used - defined:
            errors.append(f"undefined Subject labels used: {sorted(used - defined)}")
    return errors, warnings


def check_generic() -> tuple[list[str], list[str]]:
    return ["generic mode cannot validate a proprietary platform; use current evidence and an exact adapter"], []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["h3", "generic"], required=True)
    parser.add_argument("--mode", default="T2VA", choices=["T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA"])
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--manifest")
    args = parser.parse_args()
    try:
        text = Path(args.prompt).read_text(encoding="utf-8")
        manifest = read_manifest(args.manifest)
        if args.platform == "h3":
            errors, warnings = check_h3(text, args.mode, args.duration, manifest)
        else:
            errors, warnings = check_generic()
        print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
        return 0 if not errors else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
