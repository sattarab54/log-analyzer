
# log-analyzer

A small CLI tool that reads a log file, counts log levels, and outputs the counts in a chosen format.
CLI tool to count log levels (INFO/WARNING/ERROR/DEBUG) in a log file.
---

## Install (editable / development)

From the project root:

```bash
pip install -e .
```

---

## Run

Show help:

```bash
logan -h
```

Run with default settings  
(uses data/sample.log, table format, sorted by level):

```bash
logan
```

Specify a log file:

```bash
logan -f data/sample.log
```

---

## Output formats

Table (default):

```bash
logan -f data/sample.log --format table
```
Example output
ERROR:   2
WARNING: 1
INFO:    3
DEBUG:   0

CSV:

```bash
logan -f data/sample.log --format csv
```
JSON:

```bash
logan -f data/sample.log --format json

Example output:

{
  "ERROR": 2,
  "WARNING": 1,
  "INFO": 3,
  "DEBUG": 0
}


Sorting

Sort by log level order (default):

```bash
logan -f data/sample.log --sort level
```

Sort by count (largest first):

```bash
logan -f data/sample.log --sort count
```

Reverse final order:

```bash
logan -f data/sample.log --sort count --reverse
```
Write Output to a file
Write out put to a file instead of printing to the console:

```
logan -f data/sample.log format table --output out.txt
---

To overwrite an existing file:

```bash
logan -f data/sample.log --output out.csv --force

if the file is open(for example in Excel),the CLIwill return an error.

Filtering Specific Levels
you can limit output to specific log levels:

```bash
logan -f data/sample.log --level ERROR WARNING

Exit Codes
o - Success
2 - CLI erroe or file wrie failure

## Design notes

`run_logic(...)` is a pure function:
- no argparse
- no printing
- no sys.exit
- returns ordered counts

`main(...)` handles CLI parsing and error handling.

Printers only print data and do not sort.

---

## Tests

Run all tests:

```bash
python -m pytest
```

---

## Final check

- CLI runs correctly  
- All tests pass  
- Editable install works (`pip install -e .`)
