#!/usr/bin/env python3
"""Read local image dimensions and check explicitly supplied, evidence-scoped aspect bounds.

Does not upload, transform assets, validate artistic content or guarantee gateway acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from runtime_tools import find_binary


def check_geometry(width: int, height: int, minimum: float, maximum: float) -> list[str]:
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (minimum, maximum)) or not 0 < minimum <= maximum:
        raise ValueError("aspect bounds must be finite, positive and ordered")
    if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in (width, height)):
        raise ValueError("image width and height must be positive integers")
    ratio = width / height
    return [] if minimum <= ratio <= maximum else [f"image aspect ratio {ratio:g} (={width}/{height}) is outside [{minimum:g}, {maximum:g}]"]


def find_ffprobe() -> str:
    return find_binary("ffprobe")


def inspect_image(path: Path, minimum: float, maximum: float, ffprobe: str) -> dict:
    if not path.is_file():
        raise ValueError(f"local image does not exist: {path}")
    # Read dimensions from the submitted file, not its filename, node thumbnail
    # or desired video output ratio. Animated images are outside this check.
    result = subprocess.run([
        ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height", "-of", "json", str(path)
    ], check=True, text=True, capture_output=True)
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise ValueError(f"cannot read image dimensions: {path}")
    width, height = streams[0].get("width"), streams[0].get("height")
    errors = check_geometry(width, height, minimum, maximum)
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "width": width, "height": height, "aspect_ratio": width / height, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+")
    parser.add_argument("--min-aspect", type=float, required=True)
    parser.add_argument("--max-aspect", type=float, required=True)
    parser.add_argument("--evidence", required=True, help="source of these bounds, including surface/mode/date")
    args = parser.parse_args()
    try:
        if not args.evidence.strip():
            raise ValueError("constraint evidence must not be empty")
        check_geometry(1, 1, args.min_aspect, args.max_aspect)
        ffprobe = find_ffprobe()
        images = [inspect_image(Path(p), args.min_aspect, args.max_aspect, ffprobe) for p in args.images]
        ok = all(not item["errors"] for item in images)
        print(json.dumps({"ok": ok, "constraint_evidence": args.evidence,
                          "bounds": [args.min_aspect, args.max_aspect], "images": images,
                          "scope": "encoded image dimensions only; no server acceptance or visual approval"}, ensure_ascii=False, indent=2))
        return 0 if ok else 2
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
