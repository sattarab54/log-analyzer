

import re
from datetime import datetime

LOG_PATTERN = re.compile(
    r'^\[?(INFO|WARNING|ERROR|DEBUG)\]?\b',
    re.IGNORECASE
)

def parse_line(line: str):
    match = LOG_PATTERN.search(line.strip())
    if match:
        return match.group(1).upper()
    return None

def parse_cli_date(value: str):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Invalid date format")








