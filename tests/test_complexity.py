import ast
import os

from py_crap.complexity.analyzer import Analyzer, complexity

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")


def test_complexity_simple():
    with open(os.path.join(TESTDATA_DIR, "simple.py")) as f:
        tree = ast.parse(f.read())
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

    assert complexity(funcs[0]) == 1  # simple()
    assert complexity(funcs[1]) == 2  # with_if()
    assert complexity(funcs[2]) == 4  # complex_func()


def test_complexity_loops_and_bool():
    with open(os.path.join(TESTDATA_DIR, "complex.py")) as f:
        tree = ast.parse(f.read())
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    assert complexity(funcs[0]) == 9  # very_complex: 8 ifs + 1
    assert complexity(funcs[1]) == 4  # match with 3 non-wildcard cases + 1 base
    assert complexity(funcs[2]) == 3  # with_loops: 1 + for + while
    assert complexity(funcs[3]) == 3  # with_bool_ops: 1 + and + or


def test_complexity_analyzer_full():
    analyzer = Analyzer([TESTDATA_DIR])
    stats = analyzer.analyze()

    stat_map = {s.func_name: s for s in stats}

    assert "simple" in stat_map
    assert stat_map["simple"].complexity == 1

    assert "with_if" in stat_map
    assert stat_map["with_if"].complexity == 2

    assert "complex_func" in stat_map
    assert stat_map["complex_func"].complexity == 4

    assert "very_complex" in stat_map
    assert stat_map["very_complex"].complexity == 9

    assert "with_loops" in stat_map
    assert stat_map["with_loops"].complexity == 3

    assert "with_bool_ops" in stat_map
    assert stat_map["with_bool_ops"].complexity == 3


def test_complexity_methods():
    analyzer = Analyzer([TESTDATA_DIR])
    stats = analyzer.analyze()

    stat_map = {s.func_name: s for s in stats}

    assert "Calculator.add" in stat_map
    assert stat_map["Calculator.add"].complexity == 1

    assert "Calculator.divide" in stat_map
    assert stat_map["Calculator.divide"].complexity == 2  # 1 + if

    assert "Calculator.complex_calc" in stat_map
    assert stat_map["Calculator.complex_calc"].complexity == 3  # 1 + for + if

    assert "AdvancedCalculator.power" in stat_map
    assert stat_map["AdvancedCalculator.power"].complexity == 2  # 1 + for


def test_complexity_exceptions():
    analyzer = Analyzer([TESTDATA_DIR])
    stats = analyzer.analyze()

    stat_map = {s.func_name: s for s in stats}

    assert "parse_int" in stat_map
    assert stat_map["parse_int"].complexity == 3  # 1 + 2 except handlers

    assert "read_and_parse" in stat_map
    assert stat_map["read_and_parse"].complexity == 3  # 1 + with + except (tuple handler = 1)
