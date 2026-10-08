#!/usr/bin/env python3
"""Validate production level, authority, reference approval, and embedded sound contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from sound_contract_check import validate_sound_contract
from drama_contracts import meaningful, text


LEVELS = {"concept", "continuity", "formal"}
APPROVALS = {"pending", "approved"}


def validate_director_gate(data):
    """One shared implementation; missing sibling fails closed, never skips the gate."""
    path = Path(__file__).resolve().parents[2] / "director/scripts/director_style.py"
    try:
        spec = importlib.util.spec_from_file_location("drama_director_style_gate", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.validate_handoff(data, "generation")
    except (OSError, ValueError, ImportError, AttributeError) as exc:
        return [f"director-style gate unavailable: {exc}"]


def validate_source_lock(data: dict) -> list[str]:
    if not isinstance(data, dict):
        return ["source lock must be an object"]
    errors: list[str] = [f"director_style: {e}" for e in validate_director_gate(data)]
    media_type = data.get("media_type", "video")
    if media_type not in ("image", "video", "audio"):
        errors.append("media_type must be image, video or audio; omitted legacy value means video")
    level = data.get("production_level")
    if not isinstance(level, str) or level not in LEVELS:
        errors.append(f"production_level must be one of {sorted(LEVELS)}")
    sources = data.get("authority_sources_and_versions")
    if not isinstance(sources, list) or not sources or not all(meaningful(s) for s in sources):
        errors.append("authority_sources_and_versions must be a non-empty array")
    if media_type != "audio" and (not isinstance(data.get("appearance_family"), str) or not data["appearance_family"].strip()):
        errors.append("appearance_family must be a non-empty string")
    for field in ("required_endpoint", "review_criteria"):
        if not meaningful(data.get(field)):
            errors.append(f"{field} is required")

    manifest = data.get("reference_manifest", [])
    if not isinstance(manifest, list):
        errors.append("reference_manifest must be an array")
        manifest = []
    seen: set[str] = set()
    for index, ref in enumerate(manifest):
        label = f"reference_manifest[{index}]"
        if not isinstance(ref, dict):
            errors.append(f"{label} must be an object")
            continue
        ref_id = ref.get("id")
        if not isinstance(ref_id, str) or not ref_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if ref_id in seen:
            errors.append(f"duplicate reference id: {ref_id}")
        seen.add(ref_id)
        approval = ref.get("approval_state")
        if not isinstance(approval, str) or approval not in APPROVALS:
            errors.append(f"{ref_id}.approval_state must be pending or approved")
        if level in ("continuity", "formal") and approval != "approved":
            errors.append(f"{ref_id}: {level} work requires approved references")
        for field in ("primary_role", "allowed_transfer", "forbidden_transfer", "priority"):
            value = ref.get(field)
            valid = (text(value) if field == "primary_role" else
                     (meaningful(value) or (type(value) is int and value >= 0)) if field == "priority" else meaningful(value))
            if not valid:
                errors.append(f"{ref_id}.{field} is required")

    if media_type == "audio":
        brief = data.get("audio_brief")
        if not isinstance(brief, dict):
            errors.append("audio_brief must be an object")
        else:
            for field in ("purpose", "content", "timing", "voice_or_source_identity", "acoustic_perspective", "usage_authority"):
                if not meaningful(brief.get(field)):
                    errors.append(f"audio_brief.{field} is required")
            if brief.get("delivery_role") not in ("guide", "master_candidate"):
                errors.append("audio_brief.delivery_role must be guide or master_candidate")
            ids = brief.get("sound_ids")
            if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x.strip() for x in ids):
                errors.append("audio_brief.sound_ids must be a non-empty array of sound ids")
            elif len(set(ids)) != len(ids):
                errors.append("audio_brief.sound_ids must be unique")
        if "sound_ownership_plan" in data:
            errors.append("standalone audio must reference, not redefine, the picture sound partition")
        return errors

    sound = data.get("sound_ownership_plan")
    if media_type == "image" and sound is None:
        return errors
    if not isinstance(sound, dict):
        errors.append("sound_ownership_plan must be an object, even when it contains an empty sound_events array")
    else:
        errors.extend(f"sound_ownership_plan: {item}" for item in validate_sound_contract(sound))
        if media_type == "image" and any(sound.get(key) for key in ("sound_events", "compiled_generation_audio_ids", "post_handoff_ids")):
            errors.append("static image sound ownership is not applicable; keep future-video audio in its own source lock")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_lock")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.source_lock).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("source lock must be a JSON object")
        errors = validate_source_lock(data)
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
