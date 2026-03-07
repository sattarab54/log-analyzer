

from pathlib import Path
import pytest
from log_analyzer.cli import main
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
    assert text[0].strip() == "level,count"
    assert "INFO,3" in text
    assert "ERROR,2" in text
    assert "WARNING,1" in text
    assert "DEBUG,0" in text

def test_cli_table_writes_to_output_file(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    out_file = tmp_path / "out.txt"

    main(["-f", str(log_file), "--output", str(out_file)])  # default table

    assert capsys.readouterr().out.strip() == ""

    text = out_file.read_text(encoding="utf-8").splitlines()
    assert "INFO: 3" in text
    assert "ERROR: 2" in text
    assert "WARNING: 1" in text
    assert "DEBUG: 0" in text

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
    assert out.index("INFO: 3") < out.index("ERROR: 2")
    assert out.index("ERROR: 2") < out.index("WARNING: 1")

def test_cli_sort_by_count_reverse(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--sort", "count", "--reverse"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out.index("DEBUG: 0") < out.index("WARNING: 1")

def test_cli_default_table_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    # default is table
    main(["-f", str(log_file)])

    out = capsys.readouterr().out.strip().splitlines()
    # Example expected:
    # INFO: 3
    # ERROR: 2
    # WARNING: 1
    assert "INFO: 3" in out
    assert "ERROR: 2" in out
    assert "WARNING: 1" in out


def test_cli_csv_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "csv"])

    out = capsys.readouterr().out.strip().splitlines()
    # Example expected:
    # level,count
    # INFO,3
    # ERROR,2
    # WARNING,1
    assert out[0].strip() == "level,count"
    assert "INFO,3" in out
    assert "ERROR,2" in out
    assert "WARNING,1" in out
    assert "DEBUG,0" in out

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
    assert text[0] == "level,count"
    assert "INFO,3" in text
    assert "ERROR,2" in text
    assert "WARNING,1" in text

def test_cli_level_filter_single(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--level", "ERROR"])
    out = capsys.readouterr().out.strip().splitlines()
    assert "ERROR: 2" in out
    assert not any(line.startswith("INFO:") for line in out)
    assert not any(line.startswith("WARNING:") for line in out)

def test_cli_level_filter_multiple(tmp_path, capsys):
    log_file = write_sample(tmp_path)
    main(["-f", str(log_file), "--level", "ERROR", "--level", "INFO"])
    out = capsys.readouterr().out.strip().splitlines()
    assert "ERROR: 2" in out
    assert "INFO: 3" in out
    assert not any(line.startswith("WARNING:") for line in out)

def test_cli_json_output(tmp_path, capsys):
    log_file = write_sample(tmp_path)

    main(["-f", str(log_file), "--format", "json"])
    out = capsys.readouterr().out.strip()

    data = json.loads(out)
    assert data["INFO"] == 3
    assert data["ERROR"] == 2
    assert data["WARNING"] == 1
    assert data.get("DEBUG", 0) == 0

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
    assert "INFO: 3" in out
    assert "ERROR: 2" in out
    assert "WARNING: 1" in out

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
    assert out[0].strip() == "level,count"
    # order depends on your LEVEL_ORDER; just check the rows exist
    assert "INFO,2" in out
    assert "ERROR,1" in out
    assert "WARNING,1" in out

def test_cli_missing_input_file_returns_2(capsys):
    rc = main(["-f", "does_not_exist.log"])
    assert rc == 2
    
def test_cli_output_exists_returns_2(tmp_path):
    from log_analyzer.cli import main

    out_file = tmp_path / "out.txt"
    out_file.write_text("already here", encoding="utf-8")
    rc = main(["-f", "data/sample.log", "--output", str(out_file)])
    assert rc == 2




    

































