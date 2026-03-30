
from . import __version__
import os
import sys

from .analyzer import analyze_logs
from .io_utils import read_file
from .output import iter_rows, print_csv, print_json, print_table
from .parser_args import build_parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if args.percent_decimals < 0:
            print("Error: --percent_decimals must be >= 0", file=sys.stderr)
            return 2

    if not args.version and not args.file:
        print("Error: -f/--file is required", file=sys.stderr)
        return 2
        
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
    levels = []

    if args.level:
        levels.extend(args.level)

    if args.levels:
        extra_levels = [item.strip().upper() for item in args.levels.split(",") if item.strip()]
        valid_levels = {"ERROR", "WARNING", "INFO", "DEBUG"}

        for level in extra_levels:
            if level not in valid_levels:
                print(f"Error: invalid level in --levels: {level}", file=sys.stderr)
                return 2

        levels.extend(extra_levels)

    levels = levels if levels else None
        
    # Build rows
    rows = iter_rows(counts, args.sort, args.reverse, levels=levels)
    if args.min_count is not None:
        if args.min_count < 0:
            print("Error: --mini-count must be >= 0", file=sys.stderr)
            return 2
        rows = [(lvl, cnt) for lvl, cnt in rows if cnt >= args.min_count]
    
    if args.top is not None:
        if args.top <= 0:
            print("Error: --top must be greater than 0", file=sys.stderr)
            return 2
        rows = rows[:args.top]

    full_total = sum(cnt for _, cnt in rows)
    show_total = not args.no_total

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
        
        show_header = not args.no_header
        decimals = args.percent_decimals
        show_percent = not args.no_percent

        if args.format == "csv":
            print_csv(
                rows,
                file=target,
                total=full_total,
                show_total=show_total,
                show_header=show_header,
                show_percent=show_percent,
                percent_decimals=decimals,                
            )
        elif args.format == "json":
            print_json(
                rows,
                file=target,
                total=full_total,                
                percent_decimals=decimals,
                show_percent=show_percent,                
            )
        else:
            print_table(
                rows,
                file=target,
                total=full_total,
                show_total=show_total,
                show_header=show_header,
                show_percent=show_percent,
                percent_decimals=decimals,                
            )
            
        return 0

    finally:
        if out_fh is not None:
            out_fh.close()


def cli_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli_main()





    
































              
        
