

from pathlib import Path
from log_analyzer.cli import main

def test_output_writes_file(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text("INFO hi\nERROR bad\nINFO hi\n", encoding="utf-8")

    out_file = tmp_path / "out.csv"
    rc = main(["-f", str(log_file), "--format", "csv", "--output", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8")
    assert "level,count" in text


def test_output_refuses_overwrite(tmp_path, capsys):
    log_file = tmp_path / "sample.log"
    log_file.write_text("INFO hi\n", encoding="utf-8")

    out_file = tmp_path / "out.csv"
    out_file.write_text("existing", encoding="utf-8")

    rc = main(["-f", str(log_file), "--format", "csv", "--output", str(out_file)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "already exists" in err

def test_output_overwrites_with_force(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text("INFO hi\nINFO hi\n", encoding="utf-8")

    out_file = tmp_path / "out.csv"
    out_file.write_text("existing", encoding="utf-8")

    rc = main(["-f", str(log_file), "--format", "csv", "--output", str(out_file), "--force"])
    assert rc == 0
    assert "existing" not in out_file.read_text(encoding="utf-8")



