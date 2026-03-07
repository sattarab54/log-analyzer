

import re

LOG_PATTERN = re.compile(
    r'^\[?(INFO|WARNING|ERROR|DEBUG)\]?\b',
    re.IGNORECASE
)

def parse_line(line: str):
    match = LOG_PATTERN.search(line.strip())
    if match:
        return match.group(1).upper()
    return None










