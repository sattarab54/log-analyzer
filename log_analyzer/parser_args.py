


import argparse
from .analyzer import LEVEL_ORDER

LEVEL_CHOICES = LEVEL_ORDER

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Log Analyzer CLI")

    parser.add_argument("-f", "--file", required=False, help="Log file path")

    parser.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format",
    )

    parser.add_argument(
        "--output-json-file",
        help="Write summary JSON output to a file",
    )
        
    parser.add_argument(
        "--level",
        action="append",
        type=str.upper,
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        
        help="Filter by log level(s)"
    )

    parser.add_argument(
        "--levels",
        help="Comma-separated log levels, for example ERROR,INFO",
    )
    
    parser.add_argument(
        "--since",
        help="Filter logs from this date (inclusive), format YYYY-MM-DD",
    )

    parser.add_argument(
        "--until",
        help="Filter logs up to this date (inclusive), format YYYY-MM-DD",
    )

    parser.add_argument(
        "--sort",
        choices=["level", "count", "percent", "alpha"],
        default="level",
        help="Sort output by level order, count, percent, or alphabetically",
    )

    parser.add_argument(
        "--top",
        type=int,
        help="Show top N results after sorting"
    )
    parser.add_argument(
        "--min-count",
        type=int,
        help="Show only levels with count >= N"
    )

    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse the final output order",
    )

    parser.add_argument(
        "--output",
        help="Write output to a file instead of stdout",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it already exists",
    )

    parser.add_argument(
        "--no-total",
        action="store_true",
        help="Do not show total row in output",
    )

    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show only the total summary",
    )
    
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Do not show header row in table or CSV output",
    )

    parser.add_argument(
        "--percent-decimals",
        type=int,
        default=1,
        help="Number of decimal places for percent output",
    )
    parser.add_argument(
        "--no-percent",
        dest="no_percent",
        action="store_true",
        help="Do not include percent column in output",
    )

    parser.add_argument(
        "--summary-json",
        action="store_true",
        help="Show only total summary in JSON format",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser
















