"""Optional local binaries: explicit user override, then PATH; never install."""
from __future__ import annotations

import os
import shutil


def find_binary(name: str) -> str:
    if name not in ("ffmpeg", "ffprobe"):
        raise ValueError("only ffmpeg and ffprobe are supported optional tools")
    variable = f"SHOTLOOM_{name.upper()}"
    explicit = os.environ.get(variable)
    if explicit is not None:
        found = shutil.which(explicit)
        if not explicit.strip() or found is None:
            raise FileNotFoundError(f"{variable} does not name an executable; no fallback or installation performed")
        return found
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(f"optional {name} unavailable: set {variable} or PATH; no dependencies were installed")
