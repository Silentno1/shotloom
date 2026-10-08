#!/usr/bin/env python3
"""Validate provenance for changing platform/model capability claims."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


LEVELS = {"official-current", "interface-observed", "project-verified", "community-observation", "unknown"}
HARD_EVIDENCE = {"official-current", "interface-observed", "project-verified"}


def parse_date(value: object, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO date")
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be an ISO date")
        return None
    if parsed > date.today():
        errors.append(f"{label} cannot be in the future")
    return parsed


def validate_evidence(data: dict) -> list[str]:
    if not isinstance(data, dict):
        return ["platform evidence must be an object"]
    errors: list[str] = []
    for field in ("platform", "model", "surface"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")
    claims = data.get("claims")
    if not isinstance(claims, list):
        return errors + ["claims must be an array"]
    required = data.get("required_claims", [])
    if not isinstance(required, list) or not all(isinstance(item, str) and item.strip() for item in required):
        errors.append("required_claims must be an array of non-empty claim ids")
        required = []
    by_id: dict[str, dict] = {}
    for index, claim in enumerate(claims):
        label = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if claim_id in by_id:
            errors.append(f"duplicate claim id: {claim_id}")
        by_id[claim_id] = claim
        if "value" not in claim:
            errors.append(f"{claim_id}.value is required")
        level = claim.get("evidence_level")
        if not isinstance(level, str) or level not in LEVELS:
            errors.append(f"{claim_id}.evidence_level must be one of {sorted(LEVELS)}")
        if level != "unknown":
            parse_date(claim.get("verified_at"), f"{claim_id}.verified_at", errors)
            if not isinstance(claim.get("source"), str) or not claim["source"].strip():
                errors.append(f"{claim_id}.source is required for {level}")
        if level == "official-current" and isinstance(claim.get("source"), str) and not claim["source"].startswith(("https://", "http://")):
            errors.append(f"{claim_id}.source must be a first-party URL for official-current")
        if level == "project-verified":
            if not isinstance(claim.get("artifact"), str) or not claim["artifact"].strip():
                errors.append(f"{claim_id}.artifact is required for project-verified")
            if not isinstance(claim.get("result_hash"), str) or len(claim["result_hash"].strip()) < 8:
                errors.append(f"{claim_id}.result_hash is required for project-verified")
    for claim_id in required:
        claim = by_id.get(claim_id)
        if claim is None:
            errors.append(f"required claim is missing: {claim_id}")
        elif not isinstance(claim.get("evidence_level"), str) or claim["evidence_level"] not in HARD_EVIDENCE:
            errors.append(f"required claim {claim_id} needs official-current, interface-observed or project-verified evidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("evidence must be a JSON object")
        errors = validate_evidence(data)
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
