#!/usr/bin/env python3
"""Validate public packaging and local wiring, not creative or source truth."""
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill/shotloom"
MODULES = ("director", "visual-design", "generation", "review-continuity", "edit-delivery")
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1"}


def validate() -> list[str]:
    errors = []
    required = [ROOT / p for p in ("README.md", "README.zh-CN.md", "ATTRIBUTION.md", "LICENSE", "docs/baseline-map.json")]
    required += [SKILL / p for p in ("SKILL.md", "agents/openai.yaml", "references/environment.md", "references/production-state.md")]
    required += [SKILL / "modules" / name / "WORKFLOW.md" for name in MODULES]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required resource: {path.relative_to(ROOT)}")
    if errors:
        return errors
    entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    pieces = entry.split("---", 2)
    if not entry.startswith("---\n") or len(pieces) != 3:
        errors.append("missing or unclosed entry frontmatter")
    elif not re.search(r"^name:\s*shotloom\s*$", pieces[1], re.M) or not re.search(r"^description:\s*\S", pieces[1], re.M):
        errors.append("entry requires name shotloom and a description")
    for name in MODULES:
        if f"modules/{name}/WORKFLOW.md" not in entry:
            errors.append(f"entry does not route module: {name}")
    if list((SKILL / "modules").rglob("SKILL.md")):
        errors.append("internal modules must not introduce competing discoverable skills")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            try:
                compile(content, str(path), "exec")
            except SyntaxError as exc:
                errors.append(f"Python syntax: {path.relative_to(ROOT)}: {exc}")
        if path.suffix == ".json":
            try:
                json.loads(content)
            except ValueError as exc:
                errors.append(f"JSON syntax: {path.relative_to(ROOT)}: {exc}")
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if re.match(r"^(https?://|mailto:|#)", link):
                    continue
                target = link.split("#", 1)[0]
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    errors.append(f"broken link: {path.relative_to(ROOT)} -> {link}")
                if path.is_relative_to(SKILL) and not resolved.is_relative_to(SKILL.resolve()):
                    errors.append(f"runtime link escapes installable folder: {path.relative_to(SKILL)} -> {link}")
        if path.is_relative_to(SKILL):
            # Author-home and installed-sibling dependencies are forbidden;
            # model manufacturer names and documented syntax are not.
            local_content = re.sub(r"https?://[^\s<)\"']+", "", content)
            patterns = (r"/Users/[A-Za-z0-9]", r"/home/[A-Za-z0-9]", r"[A-Za-z]:\\Users\\",
                        r"(?i)Obsidian", r"(?i)LibTV", r"(?i)xiaoyunque", "小云雀",
                        r"\.codex/skills/", r"\.agents/skills/", r"api_key\s*=\s*['\"]?[A-Za-z0-9]")
            for pattern in patterns:
                if re.search(pattern, local_content):
                    errors.append(f"private/runtime dependency text: {path.relative_to(SKILL)} ({pattern})")
            if path.is_symlink() and not path.resolve().is_relative_to(SKILL.resolve()):
                errors.append(f"runtime symlink escapes package: {path.relative_to(SKILL)}")
    manifest = json.loads((ROOT / "docs/baseline-map.json").read_text(encoding="utf-8"))
    seen = set()
    for row in manifest["files"]:
        if "target" not in row:
            if row["disposition"] != "replaced_by_single_public_entry_metadata":
                errors.append("unexplained excluded baseline resource")
            continue
        target = row["target"]
        if target in seen or not (SKILL / target).is_file():
            errors.append(f"missing or duplicated baseline target: {target}")
        seen.add(target)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL\n" + "\n".join(f"- {item}" for item in errors))
        return 1
    print("PASS: public package structure, baseline coverage, local links, privacy and syntax; not production quality")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
