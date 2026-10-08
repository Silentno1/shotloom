#!/usr/bin/env python3
"""Validate sound ownership, picture-sync strategy, and generation/post partitions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from drama_contracts import meaningful


OWNERSHIP = {"native_required", "native_optional", "post_only", "intentional_silence"}
SYNC_STRATEGIES = {
    "none",
    "native_audio_driver",
    "silent_performance_cue",
    "guide_track_not_for_master",
    "external_lipsync",
}


def nonempty(value: object) -> bool:
    return meaningful(value)


def string_set(value: object, field: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{field} must be an array of non-empty sound ids")
        return set()
    if len(value) != len(set(value)):
        errors.append(f"{field} contains duplicate sound ids")
    return set(value)


def prompt_sections(prompt_text: str) -> dict[str, str]:
    headers = list(re.finditer(r"(?m)^([a-z_]+)\s*:\s*", prompt_text))
    sections: dict[str, str] = {}
    for index, match in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(prompt_text)
        sections[match.group(1)] = prompt_text[match.end():end].casefold()
    return sections


def marker_contexts(text: str, markers: list[str]) -> list[str]:
    """Retain punctuation inside exact markers (including approved Chinese lines)."""
    contexts = []
    separators = "\n.!?。！？"
    for marker in markers:
        for match in re.finditer(re.escape(marker), text):
            start = max(text.rfind(c, 0, match.start()) for c in separators) + 1
            if text[match.end() - 1] in separators:
                end = match.end()
            else:
                ends = [text.find(c, match.end()) for c in separators]
                end = min((i + 1 for i in ends if i >= 0), default=len(text))
            contexts.append(text[start:end])
    return contexts


def validate_sound_partition(data: dict) -> list[str]:
    if not isinstance(data, dict):
        return ["sound contract must be an object"]
    errors: list[str] = []
    events = data.get("sound_events")
    if not isinstance(events, list):
        return ["sound_events must be an array"]

    compiled = string_set(data.get("compiled_generation_audio_ids"), "compiled_generation_audio_ids", errors)
    post_ids = string_set(data.get("post_handoff_ids"), "post_handoff_ids", errors)
    seen: set[str] = set()
    expected_generation: set[str] = set()
    expected_post: set[str] = set()

    for index, event in enumerate(events):
        label = f"sound_events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{label} must be an object")
            continue
        sound_id = event.get("id")
        if not isinstance(sound_id, str) or not sound_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if sound_id in seen:
            errors.append(f"duplicate sound id: {sound_id}")
        seen.add(sound_id)
        for field in ("category", "continuity_scope"):
            if not isinstance(event.get(field), str) or not event[field].strip():
                errors.append(f"{sound_id}.{field} must be a non-empty string")
        ownership = event.get("audible_ownership")
        if not isinstance(ownership, str) or ownership not in OWNERSHIP:
            errors.append(f"{sound_id}.audible_ownership must be one of {sorted(OWNERSHIP)}")
            continue
        strategy = event.get("picture_sync_strategy", "none")
        if not isinstance(strategy, str) or strategy not in SYNC_STRATEGIES:
            errors.append(f"{sound_id}.picture_sync_strategy must be one of {sorted(SYNC_STRATEGIES)}")
            strategy = "none"
        selected = event.get("selected_for_generation", False)
        requires_sync = event.get("requires_picture_sync", False)
        if not isinstance(requires_sync, bool):
            errors.append(f"{sound_id}.requires_picture_sync must be boolean")
        if not isinstance(selected, bool):
            errors.append(f"{sound_id}.selected_for_generation must be boolean")
            selected = False

        if ownership == "native_required":
            expected_generation.add(sound_id)
            if not selected:
                errors.append(f"{sound_id}: native_required must be selected for generated audio")
            if strategy not in {"native_audio_driver", "none"}:
                errors.append(f"{sound_id}: native_required cannot use a post/silent picture-sync strategy")
        elif ownership == "native_optional":
            if selected:
                expected_generation.add(sound_id)
        elif ownership == "post_only":
            if selected:
                errors.append(f"{sound_id}: post_only cannot be selected for generated audio")
            if not nonempty(event.get("post_handoff")):
                errors.append(f"{sound_id}: post_only requires post_handoff")
            else:
                expected_post.add(sound_id)
            if requires_sync is True:
                if strategy not in {"silent_performance_cue", "guide_track_not_for_master", "external_lipsync"}:
                    errors.append(f"{sound_id}: synchronized post_only sound needs an explicit non-master picture-sync strategy")
                for field in ("picture_cue", "sync_anchor"):
                    if not nonempty(event.get(field)):
                        errors.append(f"{sound_id}: synchronized post_only sound requires {field}")
        elif ownership == "intentional_silence":
            if selected:
                errors.append(f"{sound_id}: intentional_silence cannot be selected for generated audio")
            if nonempty(event.get("post_handoff")):
                errors.append(f"{sound_id}: intentional_silence cannot have a post_handoff")

        if nonempty(event.get("post_handoff")) and ownership != "intentional_silence":
            expected_post.add(sound_id)

        markers = event.get("audible_prompt_markers", [])
        if not isinstance(markers, list) or not all(isinstance(item, str) and item.strip() for item in markers):
            errors.append(f"{sound_id}.audible_prompt_markers must be an array of non-empty strings")
            markers = []

    unknown_compiled = compiled - seen
    unknown_post = post_ids - seen
    if unknown_compiled:
        errors.append(f"compiled_generation_audio_ids contains unknown ids: {sorted(unknown_compiled)}")
    if unknown_post:
        errors.append(f"post_handoff_ids contains unknown ids: {sorted(unknown_post)}")
    if compiled != expected_generation:
        errors.append(
            "compiled_generation_audio_ids must exactly equal native_required plus selected native_optional ids; "
            f"expected {sorted(expected_generation)}, got {sorted(compiled)}"
        )
    if post_ids != expected_post:
        errors.append(f"post_handoff_ids must match events carrying post_handoff; expected {sorted(expected_post)}, got {sorted(post_ids)}")
    return errors


def check_sound_contract(data: dict, prompt_text: str | None = None, adapter: str = "auto") -> dict:
    """Check partitions and bounded literal coverage, never infer arbitrary prose semantics."""
    errors = validate_sound_partition(data)
    unknown: list[str] = []
    checked = ["sound ownership and generation/post partitions"]
    not_checked = ["paraphrased or unlisted sounds", "speaker binding", "model execution and actual audio quality"]
    if prompt_text is not None and not isinstance(prompt_text, str):
        errors.append("compiled prompt must be text")
    if prompt_text is not None and not errors:
        sections = prompt_sections(prompt_text)
        timeline_key = "detailed_description" if "detailed_description" in sections else "integrated_multimodal_description"
        h3 = timeline_key in sections and all(k in sections for k in ("overall_soundscape", "non_diegetic_music"))
        if adapter not in {"auto", "h3", "natural-language"}:
            errors.append("unsupported sound adapter")
        elif adapter == "natural-language" or not h3:
            unknown.append("natural-language/unknown schema: audible requests, negations and picture cues require semantic review")
        else:
            checked.append("H3 literal markers in sound fields and tagged timeline dialogue")
            timeline = sections[timeline_key]
            speech = "\n".join(re.findall(r"<d>(.*?)</d>", timeline, re.S))
            sound = "\n".join(sections[k] for k in ("overall_soundscape", "non_diegetic_music"))
            for event in data["sound_events"]:
                sid = event["id"]
                markers = [m.casefold() for m in event.get("audible_prompt_markers", [])]
                if not markers:
                    unknown.append(f"{sid}: no literal markers; prompt coverage unverified")
                    continue
                # A nearby exclusion/guide/picture cue may reverse the meaning of
                # a literal hit. Do not pretend regex can decide its semantics.
                contexts = marker_contexts(sound, markers)
                ambiguous = any(re.search(r"\b(no|not|without|silent|omit|exclude|guide|mouths)\b|无声|不要|禁止|后配|口型", c)
                                for c in contexts)
                guide = event.get("picture_sync_strategy") == "guide_track_not_for_master"
                in_speech = any(m in speech for m in markers)
                in_sound = bool(contexts)
                in_timeline = any(m in timeline for m in markers)
                native = event["audible_ownership"] == "native_required" or (
                    event["audible_ownership"] == "native_optional" and event.get("selected_for_generation") is True)
                forbidden = event["audible_ownership"] in {"post_only", "intentional_silence"} or (
                    event["audible_ownership"] == "native_optional" and not event.get("selected_for_generation"))
                if ambiguous or guide:
                    unknown.append(f"{sid}: exclusion/guide context needs review, not a literal audio verdict")
                elif forbidden and (in_speech or in_sound):
                    errors.append(f"{sid}: non-generated audible marker leaked into H3 audio request")
                elif native and not (in_speech or in_sound):
                    if in_timeline:
                        unknown.append(f"{sid}: untagged timeline wording needs audible-versus-picture review")
                    else:
                        errors.append(f"{sid}: generated-audio marker is missing from H3 audio/timeline fields")
                elif forbidden and in_timeline:
                    unknown.append(f"{sid}: timeline marker may be audible leakage or a legitimate picture cue; review required")
    elif prompt_text is None:
        not_checked.append("compiled prompt: not supplied")
    status = "failed" if errors else "unverified" if unknown else "passed_scoped_checks"
    return {"ok": status == "passed_scoped_checks", "status": status, "errors": errors,
            "unverified": unknown, "checked": checked, "not_checked": not_checked}


def validate_sound_contract(data: dict, prompt_text: str | None = None) -> list[str]:
    """Compatibility API: unresolved coverage is not an empty success list."""
    result = check_sound_contract(data, prompt_text)
    return result["errors"] + [f"UNVERIFIED: {item}" for item in result["unverified"]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    parser.add_argument("--prompt", help="compiled prompt; unsupported semantic coverage returns unverified")
    parser.add_argument("--adapter", choices=["auto", "h3", "natural-language"], default="auto")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("contract must be a JSON object")
        prompt_text = Path(args.prompt).read_text(encoding="utf-8") if args.prompt else None
        result = check_sound_contract(data, prompt_text, args.adapter)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["errors"] else 3 if result["unverified"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
