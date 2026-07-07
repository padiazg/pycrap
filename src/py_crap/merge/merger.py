from typing import NamedTuple, Optional

from py_crap.complexity.analyzer import Stat
from py_crap.coverage.parser import FunctionCoverage, ModuleCoverage


class MergedEntry(NamedTuple):
    file: str
    func_name: str
    class_name: str
    package: str
    complexity: int
    line: int
    end_line: int
    coverage: Optional[float]
    coverage_warning: str


class PathIndex:
    def __init__(self, coverages: list[ModuleCoverage]):
        self.by_absolute: dict[str, list[FunctionCoverage]] = {}
        self.by_suffix: dict[str, list[FunctionCoverage]] = {}
        self._build(coverages)

    def _build(self, coverages: list[ModuleCoverage]) -> None:
        for mc in coverages:
            for fn in mc.functions:
                abs_path = fn.file
                self.by_absolute.setdefault(abs_path, []).append(fn)
                suffix = self._build_suffix(abs_path)
                self.by_suffix.setdefault(suffix, []).append(fn)

    @staticmethod
    def _build_suffix(path: str) -> str:
        parts = [p for p in path.replace("\\", "/").split("/") if p]
        if len(parts) >= 3:
            return "/".join(parts[-3:])
        if len(parts) == 1:
            return parts[0]
        return "/".join(parts)

    def lookup(self, abs_path: str) -> list[FunctionCoverage]:
        if abs_path in self.by_absolute:
            return self.by_absolute[abs_path]
        suffix = self._build_suffix(abs_path)
        return self.by_suffix.get(suffix, [])


def normalize_func_name(name: str) -> str:
    return name.split(".")[-1]


def merge(
    coverages: list[ModuleCoverage], stats: list[Stat]
) -> list[MergedEntry]:
    idx = PathIndex(coverages)

    errored: dict[str, str] = {}
    for mc in coverages:
        if mc.error:
            errored[mc.dir] = mc.error

    entries: list[MergedEntry] = []
    for stat in stats:
        cov: Optional[float] = None
        cov_warn = ""

        fns = idx.lookup(stat.file)
        for fn in fns:
            if normalize_func_name(fn.name) == stat.func_name.split(".")[-1]:
                cov = fn.coverage
                break

        if cov is None:
            for mod_dir, err_msg in errored.items():
                if stat.file.startswith(mod_dir):
                    cov_warn = f"coverage unavailable for {mod_dir}: {err_msg}"
                    break

        pkg = _infer_package(stat.file)

        entries.append(
            MergedEntry(
                file=stat.file,
                func_name=stat.func_name,
                class_name=stat.class_name,
                package=pkg,
                complexity=stat.complexity,
                line=stat.line,
                end_line=stat.end_line,
                coverage=cov,
                coverage_warning=cov_warn,
            )
        )

    return entries


def _infer_package(file_path: str) -> str:
    parts = [p for p in file_path.replace("\\", "/").split("/") if p]
    if len(parts) >= 2:
        return parts[-2]
    if parts:
        return parts[-1]
    return ""
