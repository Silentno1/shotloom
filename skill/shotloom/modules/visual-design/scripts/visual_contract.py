#!/usr/bin/env python3
"""Validate an explicit visual contract without scoring or recommending a style."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from drama_contracts import meaningful


COMMON_REQUIRED = {
    "production_method",
    "final_appearance",
    "appearance_family",
    "space_and_perspective",
    "motion_cadence",
    "vfx_compositing",
    "forbidden_drift",
}

FAMILY_REQUIRED = {
    "photographic": {"capture_behavior", "anatomy_and_performance", "light_and_color", "materials"},
    "hand_drawn_2d": {"line_language", "shape_language", "layer_and_paint", "deformation"},
    "standard_3d": {"volume_and_perspective", "rig_and_deformation", "light_and_color", "materials"},
    "three_render_two": {
        "volume_and_perspective",
        "line_language",
        "shadow_language",
        "materials",
        "texture_adhesion",
        "two_d_effects",
        "motion_cadence",
        "deformation",
    },
    "stop_motion": {"material_persistence", "replacement_cadence", "contact_and_scale"},
    "motion_graphics": {"hierarchy_and_typography", "interpolation_and_timing", "information_legibility"},
    "mixed_media": {"layer_ownership", "boundary_rules", "retained_anchors"},
    "other": {"family_specific_contract"},
}


def validate_contract(data: dict) -> list[str]:
    if not isinstance(data, dict):
        return ["contract must be an object"]
    errors = []
    media_type = data.get("media_type", "video")
    if media_type not in ("image", "video"):
        errors.append("media_type must be image or video; omitted legacy value means video")
    temporal = {"motion_cadence", "replacement_cadence", "interpolation_and_timing", "deformation", "rig_and_deformation"} if media_type == "image" else set()
    required = COMMON_REQUIRED - temporal
    if media_type == "image" and data.get("vfx_present") is not True:
        required = required - {"vfx_compositing"}
    if "vfx_present" in data and not isinstance(data["vfx_present"], bool):
        errors.append("vfx_present must be boolean")
    missing_common = sorted(key for key in required if not meaningful(data.get(key)))
    errors.extend(f"missing or empty: {key}" for key in missing_common)
    family = data.get("appearance_family")
    if not isinstance(family, str) or family not in FAMILY_REQUIRED:
        errors.append(f"unsupported appearance_family: {family}; use an explicit maintained family or other")
    elif family in FAMILY_REQUIRED:
        missing_family = sorted(
            key for key in FAMILY_REQUIRED[family] - temporal if not meaningful(data.get(key))
        )
        errors.extend(f"missing or empty for {family}: {key}" for key in missing_family)
    if family != "three_render_two" and any(
        key in data for key in ("three_render_two_contract", "three_render_two_dimensions")
    ):
        errors.append("three-render-two payload is allowed only when appearance_family is three_render_two")
    if "upload_category" in data and not data.get("upload_platform"):
        errors.append("upload_category requires upload_platform; it is not a visual-method field")
    if data.get("upload_category"):
        options = data.get("category_options_observed")
        if not isinstance(options, list) or data["upload_category"] not in options:
            errors.append("upload_category must be one of category_options_observed")
        if not isinstance(data.get("category_verification_source"), str) or not data["category_verification_source"].strip():
            errors.append("upload_category requires category_verification_source; equality with production_method is allowed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    args = parser.parse_args()
    data = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("ERROR: contract must be a JSON object")
    errors = validate_contract(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
