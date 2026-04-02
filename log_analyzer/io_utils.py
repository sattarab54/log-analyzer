
from __future__ import annotations

from pathlib import Path
from datetime import datetime

def read_file(path: str) -> list[str]:
    """
    Read a text file and return lines INCLUDING their trailing newline characters,
    matching sys.stdin.read().splitlines(True) behavior.
    """
    text = Path(path).read_text(encoding="utf-8")
    return text.splitlines(True)

def parse_date(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def is_within_range(line_date, since=None, until=None):
    if since and line_date < since:
        return False
    if until and line_date > until:
        return False
    return True
