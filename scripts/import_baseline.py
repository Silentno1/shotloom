#!/usr/bin/env python3
"""Import an explicitly supplied five-component baseline into a new public tree.

Maintainer-only bulk migration, not a runtime dependency or an automatic updater.
Existing destinations are refused. Review the capability map and semantic public
adaptations after import; textual normalization is not publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

COMPONENTS = {
    "ai-drama-director": "director",
    "ai-drama-visual-design": "visual-design",
    "ai-media-generation": "generation",
    "ai-drama-review-continuity": "review-continuity",
    "ai-drama-edit-delivery": "edit-delivery",
}


def normalize(text: str, *, entry: bool) -> str:
    for source, target in COMPONENTS.items():
        text = text.replace(source, target)
    text = text.replace("SKILL.md", "WORKFLOW.md")
    if entry and text.startswith("---\n"):
        text = text.split("---", 2)[2].lstrip()
        text = (
            "> Shotloom module, not a separately installed skill. The package "
            "[entry](../../SKILL.md) and [environment contract](../../references/environment.md) "
            "govern permissions, tool availability and storage. Formal methods may be "
            "named references or user-authored; see the shared method-selection contract.\n\n"
            "Script checks below are optional tool-assisted forms of the same decisions. "
            "Without Python or required media tools, use the documented manual checks "
            "and mark unavailable evidence; do not invent a machine pass or block unrelated planning.\n\n"
        ) + text
    substitutions = {
        "and Obsidian rules": "and the user-selected project handoff policy",
        "Obsidian handoff boundaries": "project handoff boundaries",
        "task handoffs belong in Obsidian, not production folders": "task handoffs use the user-selected location, or remain in the conversation when no location is authorized",
        "Handoffs follow Obsidian rules": "Handoffs follow the user-selected storage policy",
        "Task handoffs go to Obsidian": "Task handoffs go to the user-selected location",
        "maintenance handoffs still follow Obsidian rules": "maintenance handoffs still follow the user-selected storage policy",
        "deferred_by_user_20261002": "not_implemented",
        "按用户 2026-10-02 决定延期": "尚未实现",
        "按用户 2026-10-02 决定搁置": "尚未实现",
        "kling-3-libtv.md": "destination-bindings.md",
        "LibTV": "the selected destination",
        "libtv": "destination",
        "Xiaoyunque": "legacy host",
        "xiaoyunque": "legacy host",
        "小云雀": "旧宿主",
    }
    for source, target in substitutions.items():
        text = text.replace(source, target)
    text = text.replace("legacy legacy host", "legacy third-party")
    # Retain documentation identity in the source register, never a maintainer's
    # home-directory dependency. Registers receive a separate semantic review.
    text = re.sub(r"`/Users/[^`]+`", "`publisher manual snapshot (not bundled)`", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("output already exists; import into a new staging directory and review the diff")
    prepared = []
    rows = []
    for old, new in COMPONENTS.items():
        source = args.source_root / old
        if not (source / "SKILL.md").is_file():
            parser.error(f"missing required baseline component: {old}")
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(source)
            if rel.parts[0] == "agents":
                rows.append({"component": new, "source": str(rel), "disposition": "replaced_by_single_public_entry_metadata"})
                continue
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            raw = path.read_bytes()
            target_rel = str(rel).replace("SKILL.md", "WORKFLOW.md").replace("kling-3-libtv.md", "destination-bindings.md")
            target = Path("modules") / new / target_rel
            content = normalize(raw.decode("utf-8"), entry=rel == Path("SKILL.md"))
            prepared.append((target, content))
            rows.append({"component": new, "source": str(rel), "source_sha256": hashlib.sha256(raw).hexdigest(),
                         "target": str(target), "disposition": "retained_with_public_adaptation"})
    # Inventory all intended writes before creating the new output directory.
    output.mkdir(parents=True)
    for target, content in prepared:
        path = output / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    # Content fingerprints are data dependencies, not immutable source hashes.
    refs = output / "modules/director/references"
    guide = refs / "director-decision-methods.json"
    data = json.loads(guide.read_text(encoding="utf-8"))
    data["catalog_sha256"] = hashlib.sha256((refs / "director-profiles.json").read_bytes()).hexdigest()
    guide.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"schema_version": 1, "purpose": "complete baseline provenance; not execution or source-truth certification",
                "baseline_date": "2026-10-04", "files": rows}
    (output / "baseline-map.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(prepared)} resources into {output}; semantic public review required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
