

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

    # Optional level filter
    levels = args.level if args.level else None

    # Build rows
    rows = iter_rows(counts, args.sort, args.reverse, levels=levels)

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
            print_csv(rows, file=target)
        elif args.format == "json":
            print_json(rows, file=target)
        else:            
            total = sum(count for _, count in rows)
            print("level count percent", file=target)
            for level, count in rows:
                percent = (count / total) * 100
                print(f"{level}: {count} ({percent: .1f}%)", file=target)
            print("_" * 16, file=target)
            print(f"TOTAL: {total}", file=target)

        return 0

    finally:
        if out_fh is not None:
            out_fh.close()


def cli_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli_main()





    
































              
        
