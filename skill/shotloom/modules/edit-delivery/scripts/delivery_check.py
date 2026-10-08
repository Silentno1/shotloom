#!/usr/bin/env python3
"""Check a delivery manifest for provenance and separation of creative versus compliance facts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from fractions import Fraction


REQUIRED = {
    "platform",
    "production_level",
    "verification_date",
    "verification_source",
    "master_file",
    "master_sha256",
    "technical_specs",
    "qc_result",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest(data: dict, base_dir: Path | None = None) -> list[str]:
    if not isinstance(data, dict):
        return ["delivery manifest must be an object"]
    errors = [f"missing: {key}" for key in sorted(REQUIRED) if data.get(key) in (None, "", [], {})]
    if data.get("production_level") != "formal":
        errors.append("delivery manifest production_level must be formal")
    try:
        verified = date.fromisoformat(str(data.get("verification_date", "")))
        if verified > date.today():
            errors.append("verification_date cannot be in the future")
    except ValueError:
        errors.append("verification_date must be an ISO date")
    source = data.get("verification_source")
    if not isinstance(source, str) or not source.strip():
        errors.append("verification_source must name the current interface evidence or first-party source")

    master_value = data.get("master_file")
    master = Path(master_value).expanduser() if isinstance(master_value, str) and master_value else None
    if master is not None and not master.is_absolute() and base_dir is not None:
        master = base_dir / master
    if master is None or not master.is_file():
        errors.append("master_file must exist and be a file")
    elif data.get("master_sha256") != file_hash(master):
        errors.append("master_sha256 does not match master_file")

    specs = data.get("technical_specs")
    if not isinstance(specs, dict):
        errors.append("technical_specs must be an object")
    else:
        for key in ("duration_seconds", "width", "height", "frame_rate", "container", "video_codec", "audio"):
            if specs.get(key) in (None, "", [], {}):
                errors.append(f"technical_specs.{key} is required")
        duration = specs.get("duration_seconds")
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
            errors.append("technical_specs.duration_seconds must be positive and finite")
        for key in ("width", "height"):
            if type(specs.get(key)) is not int or specs[key] <= 0:
                errors.append(f"technical_specs.{key} must be a positive integer")
        rate = specs.get("frame_rate")
        try:
            if isinstance(rate, str) and re.fullmatch(r"\d+(?:\.\d+|/\d+)?", rate):
                valid_rate = Fraction(rate) > 0
            else:
                valid_rate = type(rate) in (int, float) and math.isfinite(rate) and rate > 0
        except (ValueError, ZeroDivisionError):
            valid_rate = False
        if not valid_rate:
            errors.append("technical_specs.frame_rate must be a positive finite number or rational rate")
        for key in ("container", "video_codec"):
            if not isinstance(specs.get(key), str) or not specs[key].strip():
                errors.append(f"technical_specs.{key} must be a non-empty string")

    qc = data.get("qc_result")
    if not isinstance(qc, dict):
        errors.append("qc_result must be an object with status and checks")
    else:
        status = qc.get("status")
        if status not in ("pass", "accepted_exception"):
            errors.append("qc_result.status must be pass or accepted_exception; failed QC cannot pass delivery")
        checks = qc.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append("qc_result.checks must be a non-empty array")
        exception_checks = set()
        names = set()
        if isinstance(checks, list):
            for index, check in enumerate(checks):
                if not isinstance(check, dict) or not isinstance(check.get("name"), str) or not check["name"].strip():
                    errors.append(f"qc_result.checks[{index}] must contain name and status")
                    continue
                if check["name"] in names:
                    errors.append(f"duplicate QC check: {check['name']}")
                names.add(check["name"])
                if check.get("status") == "accepted_exception":
                    exception_checks.add(check["name"])
                if check.get("status") not in ("pass", "accepted_exception"):
                    errors.append(f"qc_result.checks[{index}] is not passing")
        exceptions = qc.get("exceptions", [])
        if not isinstance(exceptions, list):
            errors.append("qc_result.exceptions must be an array")
            exceptions = []
        documented = set()
        for index, exception in enumerate(exceptions):
            fields = ("check", "reason", "scope", "acceptance_source")
            if not isinstance(exception, dict) or not all(isinstance(exception.get(k), str) and exception[k].strip() for k in fields):
                errors.append(f"qc_result.exceptions[{index}] requires check, reason, scope and acceptance_source")
                continue
            if exception["check"] in documented:
                errors.append(f"duplicate exception evidence: {exception['check']}")
            documented.add(exception["check"])
        if documented != exception_checks:
            errors.append("exception evidence must exactly cover accepted_exception checks")
        if exception_checks and status != "accepted_exception":
            errors.append("exception subchecks require accepted_exception summary, not pass")
        if status == "accepted_exception" and not exception_checks:
            errors.append("accepted_exception requires explicit exception checks and evidence")

    if data.get("upload_category"):
        options = data.get("category_options_observed")
        if not isinstance(options, list) or not options:
            errors.append("upload_category requires non-empty category_options_observed from the actual platform")
        elif data["upload_category"] not in options:
            errors.append("upload_category must be one of category_options_observed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("manifest must be a JSON object")
        errors = validate_manifest(data, Path(args.manifest).resolve().parent)
        print(json.dumps({"ok": not errors, "status": "failed" if errors else "passed_scoped_checks", "errors": errors,
            "checked": ["manifest types/ranges", "source-file existence/hash", "QC exception evidence fields", "observed category membership"],
            "not_checked": ["actual media metadata versus supplied specs", "source/acceptance evidence authenticity", "creative quality", "platform compliance interpretation"]}, ensure_ascii=False, indent=2))
        return 0 if not errors else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
