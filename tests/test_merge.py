from py_crap.complexity.analyzer import Stat
from py_crap.coverage.parser import FunctionCoverage, ModuleCoverage
from py_crap.merge.merger import PathIndex, merge


def test_path_index_by_absolute():
    fc = FunctionCoverage(
        file="/abs/path/foo.py", package="foo", name="foo_fn", line=1, coverage=80.0
    )
    mc = ModuleCoverage(dir="/abs/path", module_path="foo", functions=[fc])
    idx = PathIndex([mc])

    result = idx.lookup("/abs/path/foo.py")
    assert len(result) == 1
    assert result[0].name == "foo_fn"


def test_path_index_by_suffix():
    fc = FunctionCoverage(
        file="/long/prefix/path/foo.py", package="foo", name="foo_fn", line=1, coverage=80.0
    )
    mc = ModuleCoverage(dir="/long/prefix/path", module_path="foo", functions=[fc])
    idx = PathIndex([mc])

    result = idx.lookup("/other/prefix/path/foo.py")
    assert len(result) == 1
    assert result[0].name == "foo_fn"


def test_merge_basic():
    stats = [
        Stat(
            file="/abs/path/foo.py", func_name="foo_fn", class_name="",
            complexity=3, line=1, end_line=10,
        ),
    ]

    fc = FunctionCoverage(
        file="/abs/path/foo.py", package="foo", name="foo_fn", line=1, coverage=80.0
    )
    mc = ModuleCoverage(dir="/abs/path", module_path="foo", functions=[fc])

    result = merge([mc], stats)
    assert len(result) == 1
    assert result[0].func_name == "foo_fn"
    assert result[0].complexity == 3
    assert result[0].coverage == 80.0
    assert result[0].coverage_warning == ""


def test_merge_no_coverage():
    stats = [
        Stat(
            file="/abs/path/foo.py", func_name="foo_fn", class_name="",
            complexity=3, line=1, end_line=10,
        ),
    ]

    result = merge([], stats)
    assert len(result) == 1
    assert result[0].func_name == "foo_fn"
    assert result[0].coverage is None


def test_merge_coverage_error():
    stats = [
        Stat(
            file="/abs/path/foo.py", func_name="foo_fn", class_name="",
            complexity=3, line=1, end_line=10,
        ),
    ]

    mc = ModuleCoverage(
        dir="/abs/path", module_path="foo", functions=[],
        error="go test failed",
    )

    result = merge([mc], stats)
    assert len(result) == 1
    assert result[0].coverage is None
    assert "coverage unavailable" in result[0].coverage_warning
