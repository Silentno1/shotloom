#!/usr/bin/env python3
"""Read-only consistency check of declared video-review coverage; never a quality verdict."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


DECISIONS = {"retain", "repair", "regenerate", "unverified"}
KINDS = {"targeted", "selected_range", "take", "sequence", "final_render"}
METHODS = {"normal_playback", "normal_listening", "overview", "sampled_frames",
           "source_frames", "native_detail", "slow_playback", "neighbor_comparison"}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def texts(value):
    return isinstance(value, list) and bool(value) and all(text(v) for v in value)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def span(value, duration):
    return (isinstance(value, list) and len(value) == 2 and all(number(x) for x in value)
            and 0 <= value[0] < value[1] <= duration)


def gaps(target, intervals):
    """Union intervals, then return uncovered half-open ranges (seconds)."""
    cursor, end = target
    result = []
    for start, stop in sorted(intervals):
        start, stop = max(start, target[0]), min(stop, end)
        if stop <= start or stop <= cursor:
            continue
        if start > cursor + 1e-6:
            result.append([cursor, start])
        cursor = max(cursor, stop)
    if cursor < end - 1e-6:
        result.append([cursor, end])
    return result


def check(data, actual_source_hash=None):
    errors, unresolved = [], []
    uncovered = {}
    not_checked = ["truth of declared viewing/listening and evidence contents",
                   "risk/check selection completeness", "visual/audio quality and defect salience",
                   "project tolerance and approval authenticity", "actual source duration and time-origin accuracy"]
    if actual_source_hash is None:
        not_checked.append("actual source file hash")

    def result():
        status = "failed" if errors else "unverified" if unresolved else "passed_consistency_only"
        return {"ok": status == "passed_consistency_only", "status": status,
                "errors": errors, "unverified": unresolved, "uncovered_ranges": uncovered,
                "acceptance_granted": False, "not_checked": not_checked}

    if not isinstance(data, dict):
        errors.append("review must be an object")
        return result()
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for key in ("baseline_ref", "time_origin"):
        if not text(data.get(key)):
            errors.append(f"{key} required")
    source, scope = data.get("source"), data.get("scope")
    if not isinstance(source, dict) or not isinstance(scope, dict):
        errors.append("source and scope must be objects")
        return result()
    duration = source.get("duration_seconds")
    source_hash = source.get("sha256")
    if not text(source.get("path")) or not digest(source_hash) or not number(duration) or duration <= 0:
        errors.append("source needs path, SHA-256 and positive finite duration_seconds")
        return result()
    if actual_source_hash is not None and actual_source_hash != source_hash:
        errors.append("actual source hash differs from reviewed version")
    kind = scope.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        errors.append("scope.kind invalid")
    target = scope.get("range")
    if not span(target, duration):
        errors.append("scope.range must be a valid half-open source interval")
        return result()
    if isinstance(kind, str) and kind in {"take", "sequence", "final_render"} and target != [0, duration]:
        errors.append("whole-object scope must cover [0,duration]; use selected_range or targeted for a fragment")
    modalities = scope.get("modalities")
    if not texts(modalities) or any(v not in {"picture", "sound"} for v in modalities) or len(set(modalities)) != len(modalities):
        errors.append("scope.modalities must contain unique picture/sound entries")
        return result()
    decision = data.get("verdict")
    if not isinstance(decision, str) or decision not in DECISIONS:
        errors.append("verdict invalid")
    elif decision == "unverified":
        unresolved.append("reviewer conclusion remains unverified")

    coverage = data.get("coverage")
    normal = {key: [] for key in modalities}
    if not isinstance(coverage, list):
        errors.append("coverage must be an array")
        coverage = []
    for i, entry in enumerate(coverage):
        label = f"coverage[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        media, method = entry.get("modality"), entry.get("method")
        valid = (isinstance(media, str) and media in modalities and isinstance(method, str)
                 and method in METHODS and span(entry.get("range"), duration))
        if not valid:
            errors.append(f"{label} has invalid modality, method or range")
            continue
        if entry.get("source_sha256") != source_hash:
            errors.append(f"{label} refers to a different source version")
        if not texts(entry.get("evidence")):
            unresolved.append(f"{label} has no review evidence")
            continue
        required_method = "normal_playback" if media == "picture" else "normal_listening"
        if method == required_method and entry.get("source_sha256") == source_hash:
            normal[media].append(entry["range"])
    for media, intervals in normal.items():
        uncovered[media] = gaps(target, intervals)
        if uncovered[media]:
            unresolved.append(f"{media}: normal-speed review has uncovered intervals")

    required, checks = data.get("required_checks"), data.get("checks")
    if not isinstance(required, list) or not all(text(v) for v in required) or len(set(required)) != len(required):
        errors.append("required_checks must be an array of unique non-empty ids")
        required = []
    if not required and not text(data.get("check_selection_reason")):
        errors.append("empty required_checks needs check_selection_reason")
    if not isinstance(checks, list):
        errors.append("checks must be an array")
        checks = []
    by_id = {}
    for i, entry in enumerate(checks):
        label = f"checks[{i}]"
        if not isinstance(entry, dict) or not text(entry.get("id")):
            errors.append(f"{label} needs id")
            continue
        cid = entry["id"]
        if cid in by_id:
            errors.append(f"duplicate check id: {cid}")
        by_id[cid] = entry
        if entry.get("source_sha256") != source_hash:
            errors.append(f"{cid} refers to a different source version")
        if not texts(entry.get("targets")) or not text(entry.get("trigger")) or not span(entry.get("range"), duration):
            errors.append(f"{cid} needs targets, trigger and valid range")
        elif entry["range"][0] < target[0] or entry["range"][1] > target[1]:
            errors.append(f"{cid} lies outside the declared review scope")
        state = entry.get("status")
        if not isinstance(state, str) or state not in {"checked", "unverified", "not_applicable"}:
            errors.append(f"{cid}.status invalid")
        elif state == "checked":
            if not text(entry.get("observed")) or not texts(entry.get("evidence")):
                unresolved.append(f"{cid}: checked claim lacks observation or evidence")
        elif state == "not_applicable":
            if not text(entry.get("reason")):
                errors.append(f"{cid}: not_applicable needs reason")
        else:
            unresolved.append(f"{cid}: not yet verified")
    for cid in required:
        if cid not in by_id:
            unresolved.append(f"required check missing: {cid}")

    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array (empty only after actual review)")
        findings = []
    finding_ids, dispositions = set(), []
    for i, entry in enumerate(findings):
        label = f"findings[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        fid = entry.get("id")
        if not text(fid) or fid in finding_ids:
            errors.append(f"{label} needs a unique id")
        else:
            finding_ids.add(fid)
        if entry.get("source_sha256") != source_hash:
            errors.append(f"{label} refers to a different source version")
        for key in ("subject", "observation", "requirement_ref", "impact", "rationale"):
            if not text(entry.get(key)):
                errors.append(f"{label}.{key} required")
        if not span(entry.get("range"), duration) or not texts(entry.get("evidence")):
            errors.append(f"{label} needs valid range and evidence")
        elif entry["range"][0] < target[0] or entry["range"][1] > target[1]:
            errors.append(f"{label} lies outside the declared review scope")
        severity, salience, treatment = entry.get("severity"), entry.get("salience"), entry.get("disposition")
        if not isinstance(severity, str) or severity not in {"minor", "major", "critical", "uncertain"}:
            errors.append(f"{label}.severity invalid")
        if not isinstance(salience, str) or salience not in {"normal_playback", "detail_only", "unknown"}:
            errors.append(f"{label}.salience invalid")
        if not isinstance(treatment, str) or treatment not in DECISIONS:
            errors.append(f"{label}.disposition invalid")
            continue
        dispositions.append(treatment)
        if severity == "uncertain" or salience == "unknown" or treatment == "unverified":
            unresolved.append(f"{label}: defect or impact remains unverified")
        if treatment == "retain" and isinstance(severity, str) and severity in {"major", "critical"} and not text(entry.get("acceptance_ref")):
            errors.append(f"{label}: retaining major/critical finding requires version-specific acceptance_ref")
        if treatment in {"repair", "regenerate"} and not text(entry.get("next_action")):
            errors.append(f"{label}: repair/regeneration needs next_action, not an executed repair claim")
    if decision == "retain" and any(d != "retain" for d in dispositions):
        errors.append("retain contradicts unresolved repair/regeneration findings on this source version")
    if decision == "repair" and "regenerate" in dispositions:
        errors.append("repair-only verdict contradicts an unresolved regeneration finding")
    if isinstance(decision, str) and decision in {"repair", "regenerate"} and decision not in dispositions:
        errors.append("repair/regenerate verdict needs a matching evidenced finding")
    return result()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review")
    parser.add_argument("--verify-source", action="store_true", help="read and hash the declared local source")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.review).read_text(encoding="utf-8"))
        actual = None
        if args.verify_source:
            if not isinstance(data, dict) or not isinstance(data.get("source"), dict) or not text(data["source"].get("path")):
                raise ValueError("source.path required for verification")
            value = hashlib.sha256()
            with Path(data["source"]["path"]).open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    value.update(block)
            actual = value.hexdigest()
        output = check(data, actual)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 2 if output["status"] == "failed" else 3 if output["status"] == "unverified" else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "status": "failed", "errors": [str(exc)], "acceptance_granted": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
