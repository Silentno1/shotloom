#!/usr/bin/env python3
"""Run isolated suites; strict media CI must execute every discovered test."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def check_media_tools() -> None:
    for name in ("ffmpeg", "ffprobe"):
        requested = os.environ.get(f"SHOTLOOM_{name.upper()}", name)
        binary = shutil.which(requested) if requested.strip() else None
        if binary is None:
            raise ValueError(f"required {name} is unavailable; media verification cannot skip")
        result = subprocess.run([binary, "-version"], text=True, capture_output=True, check=True, timeout=15)
        lines = (result.stdout or result.stderr).splitlines()
        if not lines:
            raise ValueError(f"required {name} returned no version evidence")
        print(lines[0], flush=True)


def run_suite(path: Path, require_media: bool) -> int:
    suite = unittest.defaultTestLoader.discover(str(path), pattern="test_*.py")
    discovered = suite.countTestCases()
    if not discovered:
        print(f"FAIL: no tests discovered in {path}", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(f"SUMMARY: discovered={discovered}, run={result.testsRun}, skip_events={len(result.skipped)}", flush=True)
    for test, reason in result.skipped:
        print(f"SKIP: {test}: {reason}", flush=True)
    if require_media and (result.skipped or result.testsRun != discovered):
        print("FAIL: media verification requires all discovered tests with no skips", file=sys.stderr)
        return 1
    return int(not result.wasSuccessful())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-media", action="store_true", help="require FFmpeg/FFprobe and fail on any skipped test")
    parser.add_argument("--suite", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.suite is not None:
        return run_suite(args.suite, args.require_media)
    if args.require_media:
        try:
            check_media_tools()
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
    suites = [ROOT / "tests"] + sorted((ROOT / "skill/shotloom/modules").glob("*/scripts"))
    failed = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for suite in suites:
        print(f"\nSuite: {suite.relative_to(ROOT)}", flush=True)
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "--suite", str(suite)]
        if args.require_media:
            command.append("--require-media")
        result = subprocess.run(command, cwd=ROOT, env=env, check=False)
        if result.returncode:
            failed.append(str(suite.relative_to(ROOT)))
    if failed:
        print("\nFAILED: " + ", ".join(failed))
    elif args.require_media:
        print("\nPASS: all discovered tests ran with no skips; media tools were required.")
    else:
        print("\nPASS: all suites completed; inspect explicit skip summaries. This is not full media verification.")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
