
from __future__ import annotations

from pathlib import Path


def read_file(path: str) -> list[str]:
    """
    Read a text file and return lines INCLUDING their trailing newline characters,
    matching sys.stdin.read().splitlines(True) behavior.
    """
    text = Path(path).read_text(encoding="utf-8")
    return text.splitlines(True)
