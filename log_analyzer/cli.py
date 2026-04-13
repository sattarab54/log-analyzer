
from . import __version__
import os
import sys
import json

from .analyzer import analyze_logs
from .io_utils import read_file, parse_date, is_within_range
from .output import iter_rows, print_csv, print_json, print_table
from .parser_args import build_parser
from datetime import datetime, timedelta

def parse_cli_date(value):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError

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

    # --- Date filter ---
    from datetime import datetime

    since_date = None
    until_date = None

    try:
        if args.since:
            since_date = parse_cli_date(args.since)
        if args.until:
            until_date = parse_cli_date(args.until)
    except ValueError:
        print("Error: invalid date. use YYYY-MM-DD or YYYY/MM/DD", file=sys.stderr)
        return 2

    if since_date and until_date and since_date > until_date:
        print("Error: --since cannot be later than --until", file=sys.stderr)
        return 2
    
    if since_date or until_date:
        filtered_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(maxsplit=1)

            try:
                line_date = parse_date(parts[0])
            except (ValueError, IndexError):
                continue

            if since_date and line_date < since_date:
                continue

            if until_date and line_date > until_date:
                continue

            if len(parts) > 1:
                filtered_lines.append(parts[1])                                
            else:
                filtered_lines.append("")

        lines = filtered_lines    
                                 
    counts = analyze_logs(lines)
    full_total = sum(counts.values())

    output_path = args.output or args.output_json_file

    if args.output_json_file:
        print(
            "Warning: --output-json-file is deprecated. Use --output instead.",
            file=sys.stderr,
        )

    inferred_format = None

    if output_path:        
        _, ext = os.path.splitext(output_path.lower())

        if ext == ".json":
            inferred_format = "json"
        elif ext == ".csv":
            inferred_format = "csv"
        elif ext == ".txt":
            inferred_format = "table"
        elif ext:
            print(f"Error: cannot infer output format from '{ext}'", file=sys.stderr)
            return 2
    
    final_format = args.format

    # Priority 1: explicit override
    if args.output_format != "auto":
        final_format = args.output_format

    # Priority 2: inferred from extension
    elif inferred_format:
        final_format = inferred_format
    
    if output_path and inferred_format == "json" and not (args.summary_json or args.full_json):
        args.full_json = True
           
    if args.indent is not None and not (args.summary_json or args.full_json):
        print(
            "Error: --indent requires --summary-json or --full-json",
            file=sys.stderr,
        )
        return 2

    if args.indent is not None and args.indent < 0:
        print("Error: --indent must be >= 0", file=sys.stderr)
        return 2

    if args.full_json and args.summary_json:
        print(
            "Error: cannot use --full-json with --summary-json",
            file=sys.stderr,
        )
        return 2
                           
    if args.summary_json or args.full_json:
        payload = {
            "total": full_total,
            "levels": {}
        }

        for level in ["ERROR", "WARNING", "INFO", "DEBUG"]:
            count = counts.get(level, 0)
            percent = (count / full_total * 100) if full_total else 0
            payload["levels"][level] = {
                "count": count,
                "percent": round(percent, args.percent_decimals)
            }
        
        if args.indent is not None:
            json_output = json.dumps(payload, indent=args.indent)
        else:
            json_output = json.dumps(payload)

        try:
            if output_path:
                if os.path.exists(output_path) and not (args.force or args.append):
                    print(f"Error: output file already exists: {output_path}", file=sys.stderr)
                    return 2

                dir_path = os.path.dirname(output_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_output)

            elif args.output_json_file:
                dir_path = os.path.dirname(args.output_json_file)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

                with open(args.output_json_file, "w", encoding="utf-8") as f:
                    f.write(json_output)

            else:
                print(json_output)

        except (PermissionError, OSError):
            target_path = output_path if output_path else args.output_json_file
            print(
                f"Error: cannot write to '{target_path}'",
                file=sys.stderr,
            )
            return 2

        return 0
                       
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

    seen = set()
    clean_levels = []

    for level in levels:
        if level not in seen:
            seen.add(level)
            clean_levels.append(level)

    levels = clean_levels if clean_levels else None
        
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
            if args.append and args.force:
                print("Error: cannot use --append with --force", file=sys.stderr)
                return 2
             
            if (not args.force and not args.append) and os.path.exists(args.output):
                print(f"Error: output file already exists: {args.output}", file=sys.stderr)
                return 2

            try:
                mode = "a" if args.append else "w"
                out_fh = open(args.output, mode, encoding="utf-8", newline="")
                
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

        if args.summary_only:
            print(f"TOTAL: {full_total}", file=target)
            return 0

        if final_format == "csv":
            print_csv(
                rows,
                file=target,
                total=full_total,
                show_total=show_total,
                show_header=show_header,
                show_percent=show_percent,
                percent_decimals=decimals,                
            )
        elif final_format == "json":
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





    
































              
        
