

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
        rows.sort(key=lambda t: (-t[1], t[0]))

    elif sort == "percent":
        total = sum(counts.values())
        rows.sort(
            key=lambda t: (-(t[1] / total if total else 0), t[0])
        )
    elif sort == "alpha":
        rows.sort(key=lambda t: t[0])
            
    if reverse:
        rows.reverse()
       
    return rows

def print_table(
    rows: Iterable[tuple[str, int]],
    file: TextIO,
    total: int,
    show_total: bool = True,
    show_header: bool = True,
    show_percent: bool = True,
    percent_decimals: int = 1,
) -> None:
    if show_header:
        if show_percent:
            print("level  count  percent", file=file)
        else:
            print("level  count", file=file)

    for level, count in rows:
        percent = round((count / total) * 100, percent_decimals) if total else 0.0

        if show_percent:
            print(f"{level}: {count} ({percent:.{percent_decimals}f}%)", file=file)
        else:
            print(f"{level}: {count}", file=file)

    if show_total:
        print("-" * 20, file=file)
        print(f"TOTAL: {total}", file=file)

def print_csv(
    rows: Iterable[tuple[str, int]],
    file: TextIO,
    total: int,
    show_total: bool = True,
    show_header: bool = True,
    show_percent: bool = True,
    percent_decimals: int = 1,
) -> None:
    rows = list(rows)
    
    if show_header:
        if show_percent:
            print("level,count,percent", file=file)
        else:
            print("level,count", file=file)

    for level, count in rows:
        percent = round((count / total) * 100, percent_decimals) if total else 0.0

        if show_percent:
            print(f"{level},{count},{percent:.{percent_decimals}f}", file=file)
        else:
            print(f"{level},{count}", file=file)

    if show_total:
        if show_percent:
            total_percent = f"{100:.{percent_decimals}f}" if total else f"{0:.{percent_decimals}f}"
            print(f"TOTAL,{total},{total_percent}", file=file)
        else:
            print(f"TOTAL,{total}", file=file)
        
def print_json(
    rows: Iterable[tuple[str, int]],
    file: TextIO,
    total: int,
    show_percent: bool = True,
    percent_decimals: int = 1,
) -> None:
    rows = list(rows)

    data = {
        "rows": [],
        "total": total,
    }

    for level, count in rows:
        row = {
            "level": level,
            "count": count,
        }

        if show_percent:
            row["percent"] = round((count / total) * 100, percent_decimals) if total else 0.0

        data["rows"].append(row)

    json.dump(data, file, indent=2, sort_keys=False)
    print(file=file)
    






