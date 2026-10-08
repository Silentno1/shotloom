#!/usr/bin/env python3
"""Check selected-cut provenance and event accounting, never approve story truth."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from drama_contracts import decimal_seconds, interval, number


EVENT_STATUSES = {"shown", "implied", "omitted_but_retained", "removed_by_approved_story_change", "unresolved"}


def fingerprint(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def check_time_mapping(item, fid, errors, unresolved):
    source = [item.get('source_in'), item.get('source_out')]
    timeline = [item.get('timeline_in'), item.get('timeline_out')]
    if not interval(source) or not interval(timeline):
        return
    mapping = item.get('time_mapping')
    kind = mapping.get('kind') if isinstance(mapping, dict) else mapping
    speed = None
    if kind == 'normal':
        speed = 1
    elif kind == 'constant' and isinstance(mapping, dict):
        speed = mapping.get('speed')
        if not number(speed) or speed <= 0:
            errors.append(f'{fid}.time_mapping.speed must be positive finite')
            return
    elif kind == 'map' and isinstance(mapping, dict):
        if not nonempty(mapping.get('reference')) or not valid_hash(mapping.get('sha256')):
            errors.append(f'{fid}.time_mapping map requires reference and SHA-256')
        for axis, span in (('source', source), ('timeline', timeline)):
            if mapping.get(axis + '_range') != span:
                errors.append(f'{fid}.time_mapping.{axis}_range must match selected interval')
        return  # actual ramp/freeze/reverse mapping still requires inspection
    elif nonempty(mapping):
        unresolved.append(f'{fid}: legacy retime text needs explicit constant speed or bound map')
        return
    else:
        errors.append(f'{fid}.time_mapping needs normal, constant speed or bound map')
        return
    source_duration = decimal_seconds(source[1]) - decimal_seconds(source[0])
    timeline_duration = decimal_seconds(timeline[1]) - decimal_seconds(timeline[0])
    if abs(source_duration / decimal_seconds(speed) - timeline_duration) > decimal_seconds('0.000001'):
        errors.append(f'{fid}: source/timeline durations contradict time_mapping')


def check(data: object, previous: object = None) -> dict:
    errors, unresolved, unverified_timing = [], [], []
    not_checked = ["actual media and hashes", "truth/clarity of event evidence", "approval authenticity", "creative quality", "contents and correctness of external retime maps"]
    if not isinstance(data, dict):
        return {"ok": False, "status": "failed", "errors": ["manifest must be an object"], "not_checked": not_checked}
    for field in ("cut_version", "cut_file", "time_origin"):
        if not nonempty(data.get(field)):
            errors.append(f"{field} must be non-empty")
    if not valid_hash(data.get("cut_sha256")):
        errors.append("cut_sha256 must be a lowercase SHA-256")
    fragments, events = {}, {}
    for key, target in (("fragments", fragments), ("events", events)):
        items = data.get(key)
        if not isinstance(items, list):
            errors.append(f"{key} must be an array")
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict) or not nonempty(item.get("id")):
                errors.append(f"{key}[{i}] needs an object with non-empty id")
                continue
            if item["id"] in target:
                errors.append(f"duplicate {key} id: {item['id']}")
            target[item["id"]] = item
    for fid, item in fragments.items():
        for field in ("source_file", "take_id"):
            if not nonempty(item.get(field)):
                errors.append(f"{fid}.{field} required")
        if not valid_hash(item.get("source_sha256")):
            errors.append(f"{fid}.source_sha256 invalid")
        for axis in ("source", "timeline"):
            start, end = item.get(axis + "_in"), item.get(axis + "_out")
            if not all(type(x) in (int, float) and math.isfinite(x) for x in (start, end)) or not 0 <= start < end:
                errors.append(f"{fid}.{axis} needs finite 0 <= in < out (out exclusive)")
        check_time_mapping(item, fid, errors, unverified_timing)
    for eid, event in events.items():
        for field in ("context_id", "story_position", "evidence", "authority_source"):
            if not nonempty(event.get(field)):
                errors.append(f"{eid}.{field} required")
        status = event.get("status")
        if not isinstance(status, str) or status not in EVENT_STATUSES:
            errors.append(f"{eid}.status invalid")
        elif status == "unresolved":
            unresolved.append(eid)
        elif status == "removed_by_approved_story_change" and not nonempty(event.get("approval_source")):
            errors.append(f"{eid} removal requires approval_source")
        refs = event.get("fragment_ids")
        if not isinstance(refs, list) or not all(nonempty(x) for x in refs):
            errors.append(f"{eid}.fragment_ids must be an array of ids")
        else:
            if len(refs) != len(set(refs)) or set(refs) - set(fragments):
                errors.append(f"{eid}.fragment_ids contains duplicates or unknown ids")
            if status == "shown" and not refs:
                errors.append(f"{eid} shown event needs selected fragment evidence")
    try:
        current_hash = fingerprint(data)
    except (TypeError, ValueError):
        current_hash = None
        errors.append("manifest must be finite JSON")
    changed = None
    if previous is not None:
        prior = check(previous)
        if prior["status"] == "failed":
            errors.append("previous manifest is invalid; cannot compare")
        else:
            def signatures(manifest):
                fs = {x["id"]: x for x in manifest["fragments"]}
                return {x["id"]: fingerprint({"event": x, "fragments": [fs[f] for f in x["fragment_ids"]]})
                        for x in manifest["events"]}
            if not errors:
                old, new = signatures(previous), signatures(data)
                changed = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
                missing_events = set(old) - set(new)
                if missing_events:
                    errors.append("previous events cannot silently disappear; retain explicit event disposition: "
                                  + ", ".join(sorted(missing_events)))
    status = "failed" if errors else "unverified" if unresolved or unverified_timing else "passed_structure_only"
    return {"ok": status == "passed_structure_only", "status": status, "errors": errors,
            "unresolved_event_ids": unresolved, "selection_fingerprint": current_hash,
            "unverified_timing": unverified_timing,
            "changed_event_ids": changed, "not_checked": not_checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--previous")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.manifest).read_text())
        previous = json.loads(Path(args.previous).read_text()) if args.previous else None
        result = check(data, previous)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["status"] == "failed" else 3 if result["status"] == "unverified" else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "status": "failed", "errors": [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
