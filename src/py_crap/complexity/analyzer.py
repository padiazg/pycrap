import ast
import os
import re
from pathlib import Path
from typing import NamedTuple


class Stat(NamedTuple):
    file: str
    func_name: str
    class_name: str
    complexity: int
    line: int
    end_line: int


def complexity(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    c = 1
    for node in ast.walk(func_node):
        match node:
            case ast.If():
                c += 1
            case ast.While():
                c += 1
            case ast.For():
                c += 1
            case ast.AsyncFor():
                c += 1
            case ast.ExceptHandler():
                c += 1
            case ast.With():
                if node.items:
                    c += len(node.items) - 1
                c += 1
            case ast.AsyncWith():
                if node.items:
                    c += len(node.items) - 1
                c += 1
            case ast.BoolOp():
                c += len(node.values) - 1
            case ast.Match():
                for case in node.cases:
                    c += 1
                    if case.guard is not None:
                        c += 1
                # Subtract 1 if the last case is a wildcard (default)
                if node.cases and _is_wildcard_case(node.cases[-1]):
                    c -= 1
            case ast.Assert():
                c += 1
            case ast.comprehension() if hasattr(node, "ifs"):
                c += len(node.ifs)
    return c


SKIP_DIRS = frozenset({
    ".", "_", "__pycache__", ".venv", "venv", ".mypy_cache",
    ".ruff_cache", ".pytest_cache", "node_modules", "build",
    "dist", ".egg", ".eggs", "site-packages",
})


def _is_wildcard_case(case: ast.match_case) -> bool:
    return isinstance(case.pattern, ast.MatchAs) and case.pattern.name is None


def _build_class_map(tree: ast.AST) -> dict[int, str]:
    class_map: dict[int, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                class_map[id(child)] = node.name
    return class_map


def skip_dir(name: str) -> bool:
    return name.startswith(".") or name.startswith("_") or name in SKIP_DIRS


class Analyzer:
    def __init__(self, paths: list[str], exclude: re.Pattern | None = None):
        self.paths = paths
        self.exclude = exclude
        self.stats: list[Stat] = []

    def analyze(self) -> list[Stat]:
        for path in self.paths:
            abs_path = os.path.abspath(path)
            self._analyze_dir(abs_path)
        return self.stats

    def _analyze_dir(self, dir_path: str) -> None:
        self._analyze_files(dir_path)
        self._walk_subdirs(dir_path)

    def _analyze_files(self, dir_path: str) -> None:
        for entry in sorted(Path(dir_path).glob("*.py")):
            entry_str = str(entry)
            if self.exclude and self.exclude.search(entry_str):
                continue
            self._analyze_file(entry_str)

    def _walk_subdirs(self, dir_path: str) -> None:
        for entry in sorted(Path(dir_path).iterdir()):
            if not entry.is_dir():
                continue
            if skip_dir(entry.name):
                continue
            self._analyze_dir(str(entry))

    def _analyze_file(self, file_path: str) -> None:
        try:
            with open(file_path) as f:
                source = f.read()
        except OSError:
            return

        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            return

        class_map = _build_class_map(tree)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            self._process_func(node, file_path, class_map)

    def _process_func(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        class_map: dict[int, str],
    ) -> None:
        if self.exclude and self.exclude.search(node.name):
            return

        class_name = class_map.get(id(node), "")

        c = complexity(node)
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        name = f"{class_name}.{node.name}" if class_name else node.name

        self.stats.append(
            Stat(
                file=os.path.abspath(file_path),
                func_name=name,
                class_name=class_name,
                complexity=c,
                line=start_line,
                end_line=end_line,
            )
        )


