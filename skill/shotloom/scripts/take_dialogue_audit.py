#!/usr/bin/env python3
"""Compatibility entry; the review/continuity module owns the implementation."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_target = Path(__file__).resolve().parents[1] / "modules/review-continuity/scripts/take_dialogue_audit.py"
_spec = spec_from_file_location("shotloom_review_dialogue", _target)
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)
normalize = _module.normalize
load_transcript = _module.load_transcript
timing = _module.timing
main = _module.main

if __name__ == "__main__":
    raise SystemExit(main())
