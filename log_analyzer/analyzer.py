

from .parser import parse_line
from collections import Counter

def analyze_logs(lines):
    counter = Counter()

    for line in lines:
        level = parse_line(line)
        if level:
            counter[level] += 1

    return counter

LEVEL_ORDER = ("ERROR", "WARNING", "INFO", "DEBUG")

def order_counts(counts: dict[str, int], *, sort: str = "level", reverse: bool = False) -> list[tuple[str, int]]:
    """
    Returns a list of (level, count) tuples in the desired order.
    sort:
      - "level": ERROR, WARNING, INFO, DEBUG (fixed order)
      - "count": by count (numeric)
    reverse: reverse final order
    """
    items = [(lvl, counts.get(lvl, 0)) for lvl in LEVEL_ORDER]

    if sort == "count":
        items.sort(key=lambda x: x[1], reverse=not reverse)  # largest first by default
    else:
        if reverse:
            items.reverse()

    return items











   
