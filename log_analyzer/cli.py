

import os
import sys

from .analyzer import analyze_logs
from .io_utils import read_file
from .output import iter_rows, print_csv, print_json, print_table
from .parser_args import build_parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- Read input ---
    try:
        if args.file == "-":
            lines = sys.stdin.read().splitlines(True)
        else:
            lines = read_file(args.file)
    except (FileNotFoundError, PermissionError, OSError):
        print(f"Error: file '{args.file}' not found", file=sys.stderr)
        return 2

    counts = analyze_logs(lines)
    full_total = sum(counts.values())

    # Optional level filter
    levels = args.level if args.level else None

    # Build rows
    rows = iter_rows(counts, args.sort, args.reverse, levels=levels)
    if args.top is not None:
        if args.top <= 0:
            print("Error: --top must be greater than 0", file=sys.stderr)
            return 2
        rows = rows[:args.top]

    out_fh = None
    try:
        # --- Output destination ---
        if args.output:
            if (not args.force) and os.path.exists(args.output):
                print(f"Error: output file already exists: {args.output}", file=sys.stderr)
                return 2

            try:
                out_fh = open(args.output, "w", encoding="utf-8", newline="")
            except PermissionError:
                print(
                    f"Error: cannot write to '{args.output}' (file may be open in Excel). Close it and try again.",
                    file=sys.stderr,
                )
                return 2

            target = out_fh
        else:
            target = sys.stdout

        # --- Output format ---
        if args.format == "csv":
            print_csv(rows, file=target, total=full_total)
        elif args.format == "json":
            print_json(rows, file=target, total=full_total)
        else:            
            print_table(rows, file=target, total=full_total)
            
        return 0

    finally:
        if out_fh is not None:
            out_fh.close()


def cli_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli_main()





    
































              
        
