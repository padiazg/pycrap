import io

from py_crap.report.base import FormatOptions
from py_crap.report.table import TableFormatter, coverage_bar, status_symbol
from py_crap.scan.entries import Entries
from py_crap.score.crap import CRAPEntry, MissingPolicy


def test_status_symbol():
    assert status_symbol(5, 30) == "\u2713"
    assert status_symbol(20, 30) == "\u25b2"
    assert status_symbol(40, 30) == "\u2717"


def test_coverage_bar():
    bar = coverage_bar(100)
    assert bar.count("\u2588") == 10

    bar = coverage_bar(0)
    assert bar.count("\u2591") == 10

    bar = coverage_bar(50)
    assert bar.count("\u2588") == 5
    assert bar.count("\u2591") == 5


def test_table_formatter_empty():
    entries = Entries([], MissingPolicy.PESSIMISTIC)
    buf = io.StringIO()
    fmt = TableFormatter()
    opts = FormatOptions(writer=buf, threshold=30)

    fmt.format(entries, opts)
    output = buf.getvalue()
    assert "CRAP" in output


def test_table_formatter_with_entries():
    entries = Entries([], MissingPolicy.PESSIMISTIC)
    entries.list = [
        CRAPEntry(
            file="test.py", func_name="foo", class_name="", package="test",
            complexity=5, coverage=50.0, line=1, crap=22.5, effective_crap=22.5,
            mutation_score=0.0, coverage_untrusted=False, coverage_warning="",
            skipped=False, mutation_details=(),
        ),
    ]

    buf = io.StringIO()
    fmt = TableFormatter()
    opts = FormatOptions(writer=buf, threshold=30)

    fmt.format(entries, opts)
    output = buf.getvalue()
    assert "foo" in output
    assert "22.50" in output
