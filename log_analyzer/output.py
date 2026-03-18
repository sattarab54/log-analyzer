

# log_analyzer/output.py

from __future__ import annotations

import json
from typing import Iterable, TextIO

DEFAULT_LEVELS = ["ERROR", "WARNING", "INFO", "DEBUG"]


def iter_rows(
    counts: dict[str, int],
    sort: str = "level",
    reverse: bool = False,
    levels: list[str] | None = None,
) -> list[tuple[str, int]]:
    lvls = levels if levels is not None else DEFAULT_LEVELS
    rows = [(lvl, int(counts.get(lvl, 0))) for lvl in lvls]

    if sort == "count":
        # default: largest count first
        rows.sort(key=lambda t: (-t[1], t[0]))
        if reverse:
            rows.reverse()
    else:
        # keep given level order; reverse just flips that order
        if reverse:
            rows.reverse()

    return rows

def print_table(rows: Iterable[tuple[str, int]], file: TextIO, total: int) -> None:
    print("level  count percent", file=file)
    for level, count in rows:
        percent = round((count / total) * 100, 1) if total else 0.0
        print(f"{level}: {count} ({percent:.1f}%)", file=file)
    print("_" * 20, file=file)
    print(f"TOTAL: {total}", file=file)


def print_csv(rows: Iterable[tuple[str, int]], file: TextIO, total: int) -> None:
    rows = list(rows)
    
    print("level,count,percent", file=file)

    for level, count in rows:
        percent = round((count / total) *100, 1)if total else 0.0
        print(f"{level},{count},{percent}", file=file)
    print(f"TOTAL,{total},100.0" if total else "TOTAL,0,0.0", file=file)

def print_json(rows: Iterable[tuple[str, int]], file: TextIO, total: int) -> None:
    rows = list(rows)
    
    data = {
        "rows": [
            {
                "level": level,
                "count": count,
                "percent": round((count / total) * 100, 1) if total else 0.0,
            }
            for level, count in rows
        ],
        "total": total,
    }

    json.dump(data, file, indent=2, sort_keys=False)
    print(file=file)  # newline











