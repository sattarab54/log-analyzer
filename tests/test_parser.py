
from log_analyzer.parser import parse_line


def test_parse_line_info():
    assert parse_line("INFO User logged in") == "INFO"


def test_parse_line_warning():
    assert parse_line("WARNING Disk space low") == "WARNING"


def test_parse_line_error():
    assert parse_line("ERROR Database connection failed") == "ERROR"


def test_parse_line_debug():
    assert parse_line("DEBUG Something happened") == "DEBUG"


def test_parse_line_returns_none_when_no_level():
    assert parse_line("User logged in") is None
