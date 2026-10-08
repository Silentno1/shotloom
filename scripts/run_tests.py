#!/usr/bin/env python3
"""Run each module in an isolated Python process; test files have shared names."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    suites = [ROOT / "tests"] + sorted((ROOT / "skill/shotloom/modules").glob("*/scripts"))
    failed = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for suite in suites:
        print(f"\nSuite: {suite.relative_to(ROOT)}", flush=True)
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(suite), "-p", "test_*.py", "-q"],
                                cwd=ROOT, env=env, check=False)
        if result.returncode:
            failed.append(str(suite.relative_to(ROOT)))
    print("\nFAILED: " + ", ".join(failed) if failed else "\nPASS: all test suites completed; inspect reported skips and scope.")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
