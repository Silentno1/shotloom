#!/usr/bin/env python3
"""Maintain an immutable take ledger and recompute canon in story order."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from drama_contracts import text, digest, interval


SCHEMA_VERSION = 2
STATUSES = {"candidate", "accepted", "rejected"}
EFFECTS = {"update", "one-shot-exception", "no-change"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def initial(project: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "base_registry": {},
        "base_state": {},
        "registry": {},
        "current_state": {},
        "shots": {},
        "canon_snapshots": {},
        "stale_takes": {},
        "last_accepted_shot": None,
        "changelog": [{"at": now(), "event": "initialized"}],
    }


def validate_update(update: dict[str, Any]) -> None:
    if not isinstance(update, dict):
        raise ValueError("update must be an object")
    if "context_id" in update:
        raise ValueError("single-context ledger: use the correct separate ledger, not update.context_id")
    try:
        json.dumps(update, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("update must contain finite JSON values") from exc
    for key in ("shot_id", "take_id", "status"):
        if not isinstance(update.get(key), str) or not update[key].strip():
            raise ValueError(f"update.{key} must be a non-empty string")
    if type(update.get("sequence_index")) is not int or update["sequence_index"] < 0:
        raise ValueError("update.sequence_index must be a non-negative integer")
    if update["status"] not in STATUSES:
        raise ValueError("update.status must be candidate, accepted, or rejected")
    effect = update.get("canon_effect", "update" if update["status"] == "accepted" else "no-change")
    if not isinstance(effect, str) or effect not in EFFECTS:
        raise ValueError("invalid canon_effect")
    if update["status"] != "accepted" and effect != "no-change":
        raise ValueError("candidate/rejected takes must use canon_effect no-change")
    for key in ("canon_patch", "registry_patch", "next_requirements"):
        if key in update and not isinstance(update[key], dict):
            raise ValueError(f"update.{key} must be an object")
    if "depends_on" in update and (
        not isinstance(update["depends_on"], list)
        or not all(isinstance(item, str) and item.startswith(("state.", "registry."))
                   and all(part.strip() == part and part for part in item.split('.')) for item in update["depends_on"])
        or len(set(update["depends_on"])) != len(update["depends_on"])
    ):
        raise ValueError("update.depends_on must be an array of state.* or registry.* paths")
    if "usable_range" in update and not interval(update["usable_range"]):
        raise ValueError("update.usable_range must be finite [in,out), 0 <= in < out")
    if "source_file" in update and not text(update["source_file"]):
        raise ValueError("update.source_file must be non-empty text when supplied")
    if "source_sha256" in update and not digest(update["source_sha256"]):
        raise ValueError("update.source_sha256 must be a lowercase SHA-256")
    if "source_sha256" in update and not text(update.get("source_file")):
        raise ValueError("source_sha256 needs source_file")
    if update["status"] == "accepted" and text(update.get("source_file")) and not digest(update.get("source_sha256")):
        raise ValueError("new accepted media records require source_sha256; legacy records are not backfilled")
    review = update.get("stale_dependency_review")
    if review is not None and (not isinstance(review, dict) or not text(review.get("source"))
            or not isinstance(review.get("shot_ids"), list) or not review["shot_ids"]
            or not all(text(x) for x in review["shot_ids"])
            or len(set(review["shot_ids"])) != len(review["shot_ids"])):
        raise ValueError("stale_dependency_review needs source and unique non-empty shot_ids")
    if update["status"] != "accepted" and (update.get("canon_patch") or update.get("registry_patch")):
        raise ValueError("candidate/rejected takes cannot carry canon or registry patches")
    if effect != "update" and (update.get("canon_patch") or update.get("registry_patch")):
        raise ValueError("only canon_effect update may carry canon or registry patches")
    provenance = update.get("selection_provenance")
    if provenance is not None:
        if not isinstance(provenance, dict):
            raise ValueError("selection_provenance must be an object")
        for field in ("cut_sha256", "selection_fingerprint"):
            value = provenance.get(field)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"selection_provenance.{field} must be a SHA-256")
        ids = provenance.get("event_ids")
        if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x.strip() for x in ids):
            raise ValueError("selection_provenance.event_ids must be a non-empty array of ids")
        if not isinstance(provenance.get("acceptance_source"), str) or not provenance["acceptance_source"].strip():
            raise ValueError("selection_provenance.acceptance_source required")


def active_records(state: dict[str, Any]) -> list[tuple[int, str, dict[str, Any]]]:
    records = []
    for shot_id, shot in state["shots"].items():
        active = shot.get("active_take")
        if not active:
            continue
        matches = [v for v in shot["versions"] if v["take_id"] == active and v["status"] == "accepted"]
        if len(matches) != 1:
            raise ValueError(f"shot {shot_id} has invalid active_take")
        record = matches[0]
        invalidated = state.get("invalidated_takes", {}).get(shot_id)
        if invalidated and invalidated.get("take_id") == active:
            record = copy.deepcopy(record)
            record["_invalidation_reason"] = invalidated["reason"]
        records.append((shot["sequence_index"], shot_id, record))
    records.sort(key=lambda item: (item[0], item[1]))
    return records


def value_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def path_entry(registry: dict[str, Any], canon: dict[str, Any], path: str) -> dict:
    parts = path.split(".")
    if not parts or parts[0] not in {"registry", "state"}:
        raise ValueError(f"dependency path must start with registry. or state.: {path}")
    value: Any = registry if parts[0] == "registry" else canon
    for part in parts[1:]:
        if not isinstance(value, dict) or part not in value:
            return {"exists": False}
        value = value[part]
    return {"exists": True, "value": copy.deepcopy(value)}


def path_value(registry: dict[str, Any], canon: dict[str, Any], path: str) -> Any:
    """Legacy encoding for comparison only; new baselines use path_entry."""
    entry = path_entry(registry, canon, path)
    return entry['value'] if entry['exists'] else {"__missing__": True}


def accepted_against(
    registry: dict[str, Any], canon: dict[str, Any], depends_on: list[str] | None = None
) -> dict[str, Any]:
    if depends_on:
        values = {path: path_entry(registry, canon, path) for path in depends_on}
        return {"mode": "paths", "encoding": "presence-v2", "depends_on": list(depends_on), "dependency_hash": value_hash(values)}
    return {"mode": "full", "registry_hash": value_hash(registry), "state_hash": value_hash(canon)}


def baseline_error(record: dict[str, Any], registry: dict[str, Any], canon: dict[str, Any]) -> str | None:
    if record.get("_invalidation_reason"):
        return record["_invalidation_reason"]
    expected = record.get("accepted_against")
    if not isinstance(expected, dict):
        return "accepted take has no entering-state baseline and requires re-review"
    depends_on = expected.get("depends_on") if expected.get("mode") == "paths" else None
    try:
        if expected.get('mode') == 'paths' and 'encoding' not in expected:
            if not isinstance(depends_on, list) or not depends_on:
                return 'legacy dependency paths invalid; explicit re-review required'
            values = {path: path_value(registry, canon, path) for path in depends_on}
            if any(value == {"__missing__": True} for value in values.values()):
                return 'legacy missing-value dependency is ambiguous; explicit re-review required'
            actual = {"mode": "paths", "depends_on": list(depends_on), "dependency_hash": value_hash(values)}
        else:
            actual = accepted_against(registry, canon, depends_on)
    except ValueError:
        return "accepted take has an invalid dependency path and requires re-review"
    if expected != actual:
        return "entering canonical state changed after this take was accepted"
    return None


def derive_before(state: dict[str, Any], sequence_index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = copy.deepcopy(state.get("base_registry", {}))
    canon = copy.deepcopy(state.get("base_state", {}))
    for index, _, record in active_records(state):
        if index >= sequence_index:
            break
        if baseline_error(record, registry, canon):
            continue
        if record.get("canon_effect") == "update":
            registry = merge(registry, record.get("registry_patch", {}))
            canon = merge(canon, record.get("canon_patch", {}))
    return registry, canon


def recompute(state: dict[str, Any]) -> dict[str, Any]:
    registry = copy.deepcopy(state.get("base_registry", {}))
    canon = copy.deepcopy(state.get("base_state", {}))
    snapshots = {}
    stale_takes = {}
    last = None
    for _, shot_id, record in active_records(state):
        reason = baseline_error(record, registry, canon)
        if reason:
            stale_takes[shot_id] = {
                "take_id": record["take_id"],
                "reason": reason,
                "expected": copy.deepcopy(record.get("accepted_against")),
                "actual": accepted_against(
                    registry,
                    canon,
                    record.get("accepted_against", {}).get("depends_on")
                    if isinstance(record.get("accepted_against"), dict)
                    else None,
                ),
            }
            snapshots[shot_id] = {
                "registry": copy.deepcopy(registry),
                "state": copy.deepcopy(canon),
                "active_take": record["take_id"],
                "stale": True,
            }
            continue
        if record.get("canon_effect") == "update":
            registry = merge(registry, record.get("registry_patch", {}))
            canon = merge(canon, record.get("canon_patch", {}))
        snapshots[shot_id] = {"registry": copy.deepcopy(registry), "state": copy.deepcopy(canon), "active_take": record["take_id"]}
        last = shot_id
    state["registry"] = registry
    state["current_state"] = canon
    state["canon_snapshots"] = snapshots
    state["stale_takes"] = stale_takes
    state["last_accepted_shot"] = last
    return state


def validate_state(state: dict[str, Any]) -> list[str]:
    if not isinstance(state, dict):
        return ["state must be an object"]
    errors = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for key in ("base_registry", "base_state", "registry", "current_state", "shots", "canon_snapshots", "stale_takes"):
        if not isinstance(state.get(key), dict):
            errors.append(f"{key} must be an object")
    indices = {}
    if isinstance(state.get("shots"), dict):
        for shot_id, shot in state["shots"].items():
            if not isinstance(shot, dict):
                errors.append(f"shot {shot_id} must be an object")
                continue
            index = shot.get("sequence_index")
            if type(index) is not int or index < 0:
                errors.append(f"shot {shot_id} needs a non-negative sequence_index")
            elif index in indices and indices[index] != shot_id:
                errors.append(f"sequence_index {index} is shared by {indices[index]} and {shot_id}")
            else:
                indices[index] = shot_id
            if not isinstance(shot.get("versions"), list):
                errors.append(f"shot {shot_id} versions must be an array")
            else:
                for record in shot["versions"]:
                    if not isinstance(record, dict):
                        errors.append(f"shot {shot_id} record must be an object")
                        continue
                    if record.get("usable_range") is not None and not interval(record["usable_range"]):
                        errors.append(f"shot {shot_id} has invalid usable_range")
                    if "source_sha256" in record and record["source_sha256"] is not None and not digest(record["source_sha256"]):
                        errors.append(f"shot {shot_id} has invalid source_sha256")
    if not errors:
        probe = recompute(copy.deepcopy(state))
        for key in ("registry", "current_state", "canon_snapshots", "stale_takes", "last_accepted_shot"):
            if probe.get(key) != state.get(key):
                errors.append(f"derived field {key} is stale; run recompute")
    return errors


def assert_no_unresolved_dependencies(state, update):
    """New acceptance cannot silently skip stale predecessors.

    An independently reviewed, explicit path set may bypass unrelated stale
    writes. Use conservative top-level write domains (including registry).
    No-op stale records still need the explicit review, never blanket skipping.
    """
    predecessors = [(sid, record) for index, sid, record in active_records(state)
                    if index < update['sequence_index'] and sid in state['stale_takes']]
    if not predecessors:
        return
    paths = update.get('depends_on')
    review = update.get('stale_dependency_review') or {}
    ids = {sid for sid, _ in predecessors}
    if not paths or set(review.get('shot_ids', [])) != ids or not text(review.get('source')):
        raise ValueError('unresolved predecessor takes: ' + ', '.join(sorted(ids))
                         + '; re-review them, or evidence an independent explicit dependency scope')
    domains = {prefix + '.' + key for _, record in predecessors
               for prefix, field in (('state', 'canon_patch'), ('registry', 'registry_patch'))
               for key in record.get(field, {})}
    if any(p == d or p.startswith(d + '.') or d.startswith(p + '.') for p in paths for d in domains):
        raise ValueError('explicit dependencies overlap unresolved predecessor writes: ' + ', '.join(sorted(ids)))


def apply_update(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    validate_update(update)
    result = recompute(copy.deepcopy(state))
    if update["status"] == "accepted":
        assert_no_unresolved_dependencies(result, update)
    shot_id, take_id = update["shot_id"].strip(), update["take_id"].strip()
    shot = result["shots"].setdefault(shot_id, {"sequence_index": update["sequence_index"], "active_take": None, "versions": []})
    if shot["sequence_index"] != update["sequence_index"]:
        raise ValueError(f"shot {shot_id} sequence_index is immutable ({shot['sequence_index']})")
    if any(v.get("take_id") == take_id for v in shot["versions"]):
        raise ValueError(f"duplicate take_id for {shot_id}: {take_id}")
    status = update["status"]
    effect = update.get("canon_effect", "update" if status == "accepted" else "no-change")
    entering_registry, entering_canon = derive_before(result, update["sequence_index"])
    record = {
        "take_id": take_id,
        "status": status,
        "recorded_at": now(),
        "source_file": update.get("source_file"),
        "source_sha256": update.get("source_sha256"),
        "source_binding_status": "declared_hash_bound" if update.get("source_sha256") else "unbound",
        "usable_range": update.get("usable_range"),
        "canon_effect": effect,
        "canon_patch": copy.deepcopy(update.get("canon_patch", {})),
        "registry_patch": copy.deepcopy(update.get("registry_patch", {})),
        "next_requirements": copy.deepcopy(update.get("next_requirements", {})),
        "exceptions": copy.deepcopy(update.get("exceptions", [])),
        "review_notes": update.get("review_notes"),
        "selection_provenance": copy.deepcopy(update.get("selection_provenance")),
        "stale_dependency_review": copy.deepcopy(update.get("stale_dependency_review")),
    }
    if status == "accepted":
        record["accepted_against"] = accepted_against(entering_registry, entering_canon, update.get("depends_on"))
        shot["active_take"] = take_id
        result.get("invalidated_takes", {}).pop(shot_id, None)
    shot["versions"].append(record)
    result["changelog"].append({"at": now(), "event": "take-recorded", "shot_id": shot_id, "take_id": take_id, "status": status})
    recompute(result)
    errors = validate_state(result)
    if errors:
        raise ValueError("; ".join(errors))
    return result


def revise_state(state: dict[str, Any], revision: dict[str, Any]) -> dict[str, Any]:
    """Explicit withdrawal/story-order change; preserves immutable source versions."""
    if not isinstance(revision, dict):
        raise ValueError("revision must be an object")
    if revision.get("expected_state_hash") != value_hash(state):
        raise ValueError("state changed or fingerprint missing; reread before revision")
    for field in ("reason", "approval_source"):
        if not isinstance(revision.get(field), str) or not revision[field].strip():
            raise ValueError(f"revision.{field} must be non-empty")
    deactivate = revision.get("deactivate_shots", [])
    order = revision.get("sequence_indices", {})
    if not isinstance(deactivate, list) or not all(isinstance(x, str) for x in deactivate):
        raise ValueError("deactivate_shots must be an array of shot ids")
    if len(set(deactivate)) != len(deactivate):
        raise ValueError("duplicate deactivation")
    if not isinstance(order, dict) or not all(isinstance(k, str) and type(v) is int and v >= 0 for k, v in order.items()):
        raise ValueError("sequence_indices must map shot ids to non-negative integers")
    if not deactivate and not order:
        raise ValueError("revision has no operations")
    if (set(deactivate) | set(order)) - set(state["shots"]):
        raise ValueError("revision names an unknown shot")
    result = copy.deepcopy(state)
    changes = []
    for sid in deactivate:
        shot = result["shots"][sid]
        if not shot.get("active_take"):
            raise ValueError(f"shot {sid} has no active take to withdraw")
        changes.append({"shot_id": sid, "withdrawn_take": shot["active_take"]})
        shot["active_take"] = None
        result.get("invalidated_takes", {}).pop(sid, None)
    for sid, index in order.items():
        shot = result["shots"][sid]
        if shot["sequence_index"] == index:
            continue
        changes.append({"shot_id": sid, "old_sequence_index": shot["sequence_index"], "new_sequence_index": index})
        shot["sequence_index"] = index
        if shot.get("active_take"):
            result.setdefault("invalidated_takes", {})[sid] = {
                "take_id": shot["active_take"], "reason": "story order changed; explicit re-review required"}
    if not changes:
        raise ValueError("revision changes nothing")
    indices = [shot["sequence_index"] for shot in result["shots"].values()]
    if len(indices) != len(set(indices)):
        raise ValueError("revision would create duplicate story sequence indices")
    result["changelog"].append({"at": now(), "event": "authorized-revision", "changes": changes,
                                "reason": revision["reason"], "approval_source": revision["approval_source"],
                                "previous_state_hash": value_hash(state)})
    recompute(result)
    errors = validate_state(result)
    if errors:
        raise ValueError("; ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    init = subs.add_parser("init")
    init.add_argument("state")
    init.add_argument("--project", required=True)
    init.add_argument("--force", action="store_true")
    apply_cmd = subs.add_parser("apply")
    apply_cmd.add_argument("state")
    apply_cmd.add_argument("update")
    revision_cmd = subs.add_parser("revise")
    revision_cmd.add_argument("state")
    revision_cmd.add_argument("revision")
    fingerprint_cmd = subs.add_parser("fingerprint")
    fingerprint_cmd.add_argument("state")
    validate_cmd = subs.add_parser("validate")
    validate_cmd.add_argument("state")
    show = subs.add_parser("show")
    show.add_argument("state")
    show.add_argument("--shot")
    next_cmd = subs.add_parser("next")
    next_cmd.add_argument("state")
    args = parser.parse_args()
    try:
        path = Path(args.state)
        if args.command == "init":
            if path.exists() and not args.force:
                raise ValueError("state exists; --force is required for intentional replacement")
            value = initial(args.project)
            atomic_write(path, value)
            output = {"ok": True, "state": str(path.resolve())}
        else:
            value = read_json(path)
            if args.command == "fingerprint":
                output = {"state_hash": value_hash(value)}
            elif args.command == "revise":
                value = revise_state(value, read_json(Path(args.revision)))
                atomic_write(path, value)
                output = {"ok": True, "last_accepted_shot": value["last_accepted_shot"], "stale_takes": value["stale_takes"]}
            elif args.command == "apply":
                value = apply_update(value, read_json(Path(args.update)))
                atomic_write(path, value)
                output = {"ok": True, "last_accepted_shot": value["last_accepted_shot"], "stale_takes": value["stale_takes"]}
            elif args.command == "validate":
                errors = validate_state(value)
                output = {"ok": not errors, "errors": errors}
                if errors:
                    print(json.dumps(output, ensure_ascii=False, indent=2))
                    return 2
            elif args.command == "show":
                output = value["shots"].get(args.shot) if args.shot else value
                if args.shot and output is None:
                    raise ValueError(f"unknown shot: {args.shot}")
            else:
                last = value.get("last_accepted_shot")
                requirements = {}
                if last:
                    active = value["shots"][last]["active_take"]
                    record = next(v for v in value["shots"][last]["versions"] if v["take_id"] == active)
                    requirements = record.get("next_requirements", {})
                output = {
                    "previous_accepted_shot": last,
                    "entering_canonical_state": value.get("current_state", {}),
                    "explicit_next_requirements": requirements,
                    "stale_takes_requiring_review": value.get("stale_takes", {}),
                }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
