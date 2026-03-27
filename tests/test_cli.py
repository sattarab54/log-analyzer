

from pathlib import Path
import pytest
from log_analyzer.cli import main
from log_analyzer.analyzer import analyze_logs
import json

def write_sample(tmp_path: Path) -> Path:
    p = tmp_path / "sample.log"
    p.write_text(
        "INFO User logged in\n"
        "ERROR Database connection failed\n"
        "WARNING Disk space low\n"
        "INFO File uploaded\n"
        "ERROR Timeout occurred\n"
        "INFO User logged out\n",
        encoding="utf-8",
    )
    return p

def test_cli_csv_writes_to_output_file(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    out_file = tmp_path / "out.csv"

    main(["-f", str(log_file), "--format", "csv", "--output", str(out_file)])

    # nothing printed to screen
    assert capsys.readouterr().out.strip() == ""

    # file written
    text = out_file.read_text(encoding="utf-8").splitlines()
    assert text[0].strip() == "level,count,percent"
    assert "INFO,3,50.0" in text
    assert "ERROR,2,33.3" in text
    assert "WARNING,1,16.7" in text
    assert "DEBUG,0,0.0" in text
    assert "TOTAL,6,100.0" in text
    

def test_cli_table_writes_to_output_file(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    out_file = tmp_path / "out.txt"

    main(["-f", str(log_file), "--output", str(out_file)])  # default table

    assert capsys.readouterr().out.strip() == ""

    text = out_file.read_text(encoding="utf-8").splitlines()
    assert "INFO: 3 (50.0%)" in text
    assert "ERROR: 2 (33.3%)" in text
    assert "WARNING: 1 (16.7%)" in text
    assert "DEBUG: 0 (0.0%)" in text

def write_sample(tmp_path):
    p = tmp_path / "sample.log"
    p.write_text(
        "INFO User logged in\n"
        "ERROR Database connection failed\n"
        "WARNING Disk space low\n"
        "INFO File uploaded\n"
        "ERROR Timeout occurred\n"
        "INFO User logged out\n",
        encoding="utf-8",
    )
    return p

def test_cli_requires_file_argument():
    with pytest.raises(SystemExit):
        main([])

def test_cli_sort_by_count(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--sort", "count"])
    out = capsys.readouterr().out.strip().splitlines()
    # INFO is 3 (largest), should appear before ERROR (2), WARNING (1), DEBUG (0)
    assert out.index("INFO: 3 (50.0%)") < out.index("ERROR: 2 (33.3%)")
    assert out.index("ERROR: 2 (33.3%)") < out.index("WARNING: 1 (16.7%)")

def test_cli_sort_by_count_reverse(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--sort", "count", "--reverse"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out.index("DEBUG: 0 (0.0%)") < out.index("WARNING: 1 (16.7%)")

def test_cli_default_table_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    # default is table
    main(["-f", str(log_file)])

    out = capsys.readouterr().out.strip().splitlines()
    # Example expected:
    # INFO: 3
    # ERROR: 2
    # WARNING: 1
    assert "INFO: 3 (50.0%)" in out
    assert "ERROR: 2 (33.3%)" in out
    assert "WARNING: 1 (16.7%)" in out
    assert "DEBUG: 0 (0.0%)" in out

def test_cli_csv_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "csv"])

    out = capsys.readouterr().out.strip().splitlines()

    assert out[0].strip() == "level,count,percent"
    assert "INFO,3,50.0" in out
    assert "ERROR,2,33.3" in out
    assert "WARNING,1,16.7" in out
    assert "DEBUG,0,0.0" in out
    assert "TOTAL,6,100.0" in out

def test_cli_requires_file_argument():
    with pytest.raises(SystemExit):
        main([])  # argparse should exit because -f/--file is required

def test_cli_writes_output_file(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    out_file = tmp_path / "out.csv"

    main(["-f", str(log_file), "--format", "csv", "--output", str(out_file)])

    # should not print to console
    captured = capsys.readouterr()
    assert captured.out.strip() == ""

    text = out_file.read_text(encoding="utf-8").splitlines()
    assert text[0] == "level,count,percent"
    assert "INFO,3,50.0" in text
    assert "ERROR,2,33.3" in text
    assert "WARNING,1,16.7" in text

def test_cli_level_filter_single(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--level", "ERROR"])
    out = capsys.readouterr().out.strip().splitlines()
    assert any(line.startswith("ERROR: 2 (100.0%)") for line in out)
    assert not any(line.startswith("INFO:") for line in out)
    assert not any(line.startswith("WARNING:") for line in out)
    assert not any(line.startswith("DEBUG:") for line in out)

def test_cli_level_filter_multiple(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--level", "ERROR", "--level", "INFO"])
    out = capsys.readouterr().out.strip().splitlines()

    assert any(line.startswith("ERROR: 2") for line in out)
    assert any(line.startswith("INFO: 3") for line in out)
    assert not any(line.startswith("WARNING:") for line in out)

def test_cli_json_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "json"])
    out = capsys.readouterr().out.strip()

    data = json.loads(out)
    rows = data["rows"]

    info_row = next(row for row in rows if row["level"] == "INFO")
    error_row = next(row for row in rows if row["level"] == "ERROR")
    warning_row = next(row for row in rows if row["level"] == "WARNING")
    debug_row = next(row for row in rows if row["level"] == "DEBUG")

    assert info_row["count"] == 3
    assert info_row["percent"] == 50.0

    assert error_row["count"] == 2
    assert error_row["percent"] == 33.3

    assert warning_row["count"] == 1
    assert warning_row["percent"] == 16.7

    assert debug_row["count"] == 0
    assert debug_row["percent"] == 0.0

    assert data["total"] == 6
        
def test_cli_reads_from_stdin_when_file_is_dash(tmp_path, capsys, monkeypatch):
    # Feed stdin with sample log content
    sample = (
        "INFO User logged in\n"
        "ERROR Database connection failed\n"
        "WARNING Disk space low\n"
        "INFO User logged out\n"
        "ERROR Timeout occurred\n"
        "INFO File uploaded\n"
    )
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(sample))

    # Use -f - to read from stdin
    main(["-f", "-"])

    out = capsys.readouterr().out.strip().splitlines()
    # Default table output includes counts for known levels
    assert "INFO: 3 (50.0%)" in out
    assert "ERROR: 2 (33.3%)" in out
    assert "WARNING: 1 (16.7%)" in out
    assert "DEBUG: 0 (0.0%)" in out

def test_cli_csv_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "csv"])

    out = capsys.readouterr().out.strip().splitlines()

    assert out[0].strip() == "level,count,percent"
    assert "INFO,3,50.0" in out
    assert "ERROR,2,33.3" in out
    assert "WARNING,1,16.7" in out
    assert "DEBUG,0,0.0" in out
    assert "TOTAL,6,100.0" in out

def test_cli_stdin_csv_format(tmp_path, capsys, monkeypatch):
    sample = (
        "info a\n"
        "Error b\n"
        "warning c\n"
        "INFO d\n"
    )
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(sample))

    main(["-f", "-", "--format", "csv"])

    out = capsys.readouterr().out.strip().splitlines()
    assert out[0].strip() == "level,count,percent"
    assert "INFO,2,50.0" in out
    assert "ERROR,1,25.0" in out
    assert "WARNING,1,25.0" in out
    assert "DEBUG,0,0.0" in out
    assert "TOTAL,4,100.0" in out

def test_cli_missing_input_file_returns_2(capsys):
    rc = main(["-f", "does_not_exist.log"])
    assert rc == 2
    
def test_cli_output_exists_returns_2(tmp_path):
    from log_analyzer.cli import main

    out_file = tmp_path / "out.txt"
    out_file.write_text("already here", encoding="utf-8")
    rc = main(["-f", "data/sample.log", "--output", str(out_file)])
    assert rc == 2

def test_analyze_logs_counts_levels() -> None:
    from log_analyzer.analyzer import analyze_logs

    lines = [
        "INFO Start application\n",
        "WARNING Disk almost full\n",
        "ERROR Cannot connect\n",
        "INFO User login\n",
        "DEBUG Cache refreshed\n",
        "ERROR Timeout\n",
    ]

    counts = analyze_logs(lines)

    assert counts["ERROR"] == 2
    assert counts["WARNING"] == 1
    assert counts["INFO"] == 2
    assert counts["DEBUG"] == 1

def test_cli_no_total_table(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--no-total"])

    out = capsys.readouterr().out.strip().splitlines()

    assert any(line.startswith("INFO: 3") for line in out)
    assert not any(line.startswith("TOTAL:") for line in out)
    
def test_cli_no_total_csv(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "csv", "--no-total"])

    out = capsys.readouterr().out.strip().splitlines()

    assert out[0].strip() == "level,count,percent"
    assert "INFO,3,50.0" in out
    assert not any(line.startswith("TOTAL,") for line in out)

def test_cli_levels_comma_separated(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--levels", "ERROR,INFO"])

    out = capsys.readouterr().out.strip().splitlines()

    assert any(line.startswith("ERROR: 2") for line in out)
    assert any(line.startswith("INFO: 3") for line in out)
    assert not any(line.startswith("WARNING:") for line in out)
    assert not any(line.startswith("DEBUG:") for line in out)

def test_cli_levels_comma_separated_lowercase(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--levels", "error,info"])

    out = capsys.readouterr().out.strip().splitlines()

    assert any(line.startswith("ERROR: 2") for line in out)
    assert any(line.startswith("INFO: 3") for line in out)
    assert not any(line.startswith("WARNING:") for line in out)

def test_cli_levels_invalid_value_returns_2(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    rc = main(["-f", str(log_file), "--levels", "ERROR,BOGUS"])

    captured = capsys.readouterr()
    assert rc == 2
    assert "invalid level in --levels: BOGUS" in captured.err


























