#!/usr/bin/env python3
"""Validate conditional appearance-dimension accounting without judging artistic quality."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


THREE_RENDER_TWO_DIMENSIONS = {
    "volume_perspective",
    "contours",
    "shadow_bands",
    "materials",
    "texture_adhesion",
    "two_d_effects",
    "cadence",
    "deformation",
}
DESTINATIONS = {"prompt", "reference", "not_applicable", "unsupported", "review_required"}


def validate_packet(packet: dict) -> list[str]:
    if not isinstance(packet, dict):
        return ["appearance packet must be an object"]
    errors = []
    family = packet.get("appearance_family")
    if not isinstance(family, str) or not family.strip():
        return ["appearance_family must be a non-empty string"]
    dimensions = packet.get("three_render_two_dimensions")
    if family != "three_render_two":
        if "three_render_two_dimensions" in packet:
            errors.append("three_render_two_dimensions must be absent for non-three-render-two families")
        return errors
    if not isinstance(dimensions, dict):
        return ["three_render_two_dimensions must be an object for three_render_two"]
    missing = sorted(THREE_RENDER_TWO_DIMENSIONS - set(dimensions))
    extra = sorted(set(dimensions) - THREE_RENDER_TWO_DIMENSIONS)
    errors.extend(f"missing three-render-two dimension: {name}" for name in missing)
    errors.extend(f"unknown three-render-two dimension: {name}" for name in extra)
    for name in sorted(THREE_RENDER_TWO_DIMENSIONS & set(dimensions)):
        entry = dimensions[name]
        if not isinstance(entry, dict):
            errors.append(f"{name} must be an object")
            continue
        destination = entry.get("destination")
        if not isinstance(destination, str) or destination not in DESTINATIONS:
            errors.append(f"{name} destination must be one of {sorted(DESTINATIONS)}")
        note = entry.get("note")
        if not isinstance(note, str) or not note.strip():
            errors.append(f"{name} needs a non-empty note explaining its destination")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet")
    args = parser.parse_args()
    data = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("ERROR: packet must be a JSON object")
    errors = validate_packet(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
