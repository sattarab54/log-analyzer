
from __future__ import annotations

from typing import Iterable, Iterator, Optional


def iter_rows(
    counts: dict[str, int],
    sort: bool,
    reverse: bool,
    levels: Optional[list[str]] = None,
) -> list[tuple[str, int]]:
    """
    Convert counts dict into a list of (level, count) rows.
    If sort=True, sort by count (then level) and apply reverse if requested.
    If sort=False, keep a stable, predictable order by level name.
    """
    rows = list(counts.items())

    # If caller provided explicit levels ordering, keep that order
    # (counts may contain 0s already if CLI used .get(lvl,0))
    if levels:
        # Preserve order of levels argument
        level_set = set(levels)
        ordered = [(lvl, counts.get(lvl, 0)) for lvl in levels if lvl in level_set]
        return ordered

    if sort:
        rows.sort(key=lambda x: (x[1], x[0]), reverse=reverse)
    else:
        rows.sort(key=lambda x: x[0])
    return rows


def print_table(rows: Iterable[tuple[str, int]], *, file) -> None:
    print("level  count", file=file)
    for level, count in rows:
        print(f"{level:5}  {count}", file=file)


def print_csv(rows: Iterable[tuple[str, int]], *, file) -> None:
    print("level,count", file=file)
    for level, count in rows:
        print(f"{level},{count}", file=file)


def print_json(rows: Iterable[tuple[str, int]], *, file) -> None:
    # Keep it simple: list of objects
    import json

    data = [{"level": level, "count": count} for level, count in rows]
    json.dump(data, file)
    print(file=file)  # newline











    
