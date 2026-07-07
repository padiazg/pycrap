import json
import tempfile

from py_crap.mutation.mutmut_parser import parse_mutmut_report


def test_parse_mutmut_json():
    data = [
        {
            "file": "/path/to/module.py",
            "line": 10,
            "mutator": "number_replacement",
            "type": "number",
            "status": "KILLED",
            "original_source": "42",
            "replacement_source": "0",
        },
        {
            "file": "/path/to/module.py",
            "line": 15,
            "mutator": "condition_boundary",
            "type": "condition",
            "status": "SURVIVED",
            "original_source": "x > 0",
            "replacement_source": "x >= 0",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name

    report = parse_mutmut_report(path)
    assert report.mutants_total == 2
    assert report.mutants_killed == 1
    assert report.mutants_survived == 1
    assert report.test_efficacy == 50.0
