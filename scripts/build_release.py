#!/usr/bin/env python3
"""Create a local one-folder skill zip. Does not upload, install or publish."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill/shotloom"


def build(destination: Path) -> tuple[Path, str]:
    match = re.search(r'version:\s*"([0-9A-Za-z.-]+)"', (SKILL / "SKILL.md").read_text(encoding="utf-8"))
    if match is None:
        raise ValueError("SKILL.md must declare a safe package version")
    version = match.group(1)
    # Preflight the complete inventory before creating a release file. In
    # particular, reject linked directories and dangling links as well as files.
    files = []
    for path in sorted(SKILL.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"release must not contain symlinks: {path.relative_to(SKILL)}")
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
            continue
        files.append(path)
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"shotloom-{version}.zip"
    # Refuse replacement, including symlinks; no silently overwritten release.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, str(Path("shotloom") / path.relative_to(SKILL)))
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("zip integrity check failed")
    return archive, hashlib.sha256(archive.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if subprocess.run([sys.executable, "-B", str(ROOT / "scripts/validate.py")], cwd=ROOT).returncode:
        return 1
    try:
        path, digest = build(args.output)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Created local package: {path}\nSHA-256: {digest}\nNot published; tests and production evidence remain separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
