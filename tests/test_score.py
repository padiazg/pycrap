from py_crap.score.crap import crap, MissingPolicy
from py_crap.merge.merger import MergedEntry


def test_crap_formula():
    # CC=1, cov=100% → 1² * (1-1)³ + 1 = 0 + 1 = 1
    assert crap(1, 100) == 1.0

    # CC=1, cov=0% → 1² * (1-0)³ + 1 = 1 + 1 = 2
    assert crap(1, 0) == 2.0

    # CC=10, cov=50% → 100 * 0.125 + 10 = 12.5 + 10 = 22.5
    assert crap(10, 50) == 22.5

    # CC=10, cov=0% → 100 * 1 + 10 = 110
    assert crap(10, 0) == 110.0


def test_missing_pessimistic():
    from py_crap.score.crap import score, CRAPEntry

    entries = [
        MergedEntry(
            file="test.py", func_name="foo", class_name="", package="test",
            complexity=5, line=1, end_line=10, coverage=None, coverage_warning="",
        ),
    ]

    result = score(entries, MissingPolicy.PESSIMISTIC)
    assert len(result) == 1
    assert result[0].coverage == 0.0
    assert result[0].crap == crap(5, 0.0)


def test_missing_optimistic():
    from py_crap.score.crap import score

    entries = [
        MergedEntry(
            file="test.py", func_name="foo", class_name="", package="test",
            complexity=5, line=1, end_line=10, coverage=None, coverage_warning="",
        ),
    ]

    result = score(entries, MissingPolicy.OPTIMISTIC)
    assert len(result) == 1
    assert result[0].coverage == 100.0
    assert result[0].crap == crap(5, 100.0)


def test_missing_skip():
    from py_crap.score.crap import score

    entries = [
        MergedEntry(
            file="test.py", func_name="foo", class_name="", package="test",
            complexity=5, line=1, end_line=10, coverage=None, coverage_warning="",
        ),
    ]

    result = score(entries, MissingPolicy.SKIP)
    assert len(result) == 1
    assert result[0].skipped


def test_happy_path():
    from py_crap.score.crap import score

    entries = [
        MergedEntry(
            file="test.py", func_name="bar", class_name="", package="test",
            complexity=3, line=1, end_line=10, coverage=80.0, coverage_warning="",
        ),
    ]

    result = score(entries, MissingPolicy.PESSIMISTIC)
    assert len(result) == 1
    assert not result[0].skipped
    assert result[0].coverage == 80.0
    assert result[0].crap == crap(3, 80.0)
