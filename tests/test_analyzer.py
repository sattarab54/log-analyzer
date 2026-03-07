

from log_analyzer.analyzer import analyze_logs


def test_analyze_logs_counts_levels():
    lines = [
        "INFO User logged in\n",
        "ERROR Database connection failed\n",
        "WARNING Disk space low\n",
        "INFO File uploaded\n",
        "ERROR Timeout occurred\n",
        "INFO User logged out\n",
    ]
    counts = analyze_logs(lines)

    assert counts["INFO"] == 3
    assert counts["ERROR"] == 2
    assert counts["WARNING"] == 1
    assert counts.get("DEBUG", 0) == 0
    

def test_analyze_logs_ignores_unknown_lines():
    lines = [
        "hello\n",
        "INFO ok\n",
        "nothing\n",
    ]
    counts = analyze_logs(lines)

    assert counts["INFO"] == 1

def test_analyze_logs_case_insensitive():
    lines = [
        "info something\n",
        "Error failure\n",
        "warning disk space\n",
        "DEBUG test\n",
        "InFo mixed case\n",
    ]

    counts = analyze_logs(lines)

    assert counts["INFO"] == 2
    assert counts["ERROR"] == 1
    assert counts["WARNING"] == 1
    assert counts["DEBUG"] == 1
