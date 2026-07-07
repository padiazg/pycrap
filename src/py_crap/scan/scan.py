from __future__ import annotations

import re

from py_crap.complexity.analyzer import Analyzer
from py_crap.coverage.parser import ModuleCoverage
from py_crap.coverage.runner import CoverageRunner
from py_crap.merge.merger import merge
from py_crap.scan.entries import Entries
from py_crap.score.crap import MissingPolicy


class Options:
    def __init__(
        self,
        path: str = ".",
        exclude: list[str] | None = None,
        missing: str = "pessimistic",
        top: int = 0,
        min_score: float = 0,
        mutation_report: str = "",
    ) -> None:
        self.path = path
        self.exclude = exclude or []
        self.missing = missing
        self.top = top
        self.min_score = min_score
        self.mutation_report = mutation_report


def scan(options: Options) -> Entries:
    exclude_re = _build_exclude_regex(options.exclude)

    runner = CoverageRunner(options.path)
    xml_path = runner.run()

    coverages: list[ModuleCoverage] = []
    if xml_path:
        try:
            mc = _parse_coverage(xml_path, options.path)
            coverages.append(mc)
        except Exception:
            pass

    analyzer = Analyzer([options.path], exclude_re)
    stats = analyzer.analyze()

    merged = merge(coverages, stats)

    policy = _parse_missing_policy(options.missing)

    entries = Entries(merged, policy, options.mutation_report)

    if options.top > 0:
        entries.list = _apply_top_filter(entries.list, options.top)
    if options.min_score > 0:
        entries.list = _apply_min_filter(entries.list, options.min_score)

    return entries


def _build_exclude_regex(exclude: list[str]) -> re.Pattern | None:
    if not exclude:
        return None
    return re.compile("|".join(exclude))


def _parse_coverage(xml_path: str, mod_dir: str) -> ModuleCoverage:
    from py_crap.coverage.parser import parse_coverage_xml

    return parse_coverage_xml(xml_path, mod_dir)


def _parse_missing_policy(s: str) -> MissingPolicy:
    match s.lower():
        case "pessimistic" | "":
            return MissingPolicy.PESSIMISTIC
        case "optimistic":
            return MissingPolicy.OPTIMISTIC
        case "skip":
            return MissingPolicy.SKIP
        case _:
            raise ValueError(f"unknown missing policy: {s}")


def _apply_top_filter(
    entries: list, top: int
) -> list:
    trusted = [e for e in entries if not e.coverage_untrusted]
    untrusted = [e for e in entries if e.coverage_untrusted]

    sorted(
        trusted, key=lambda e: e.effective_score(), reverse=True
    )

    sorted_entries = sorted(
        entries, key=lambda e: e.effective_score(), reverse=True
    )

    result = untrusted[:]
    kept = 0
    for e in sorted_entries:
        if not e.coverage_untrusted and kept < top:
            result.append(e)
            kept += 1

    return result


def _apply_min_filter(entries: list, min_score: float) -> list:
    return [
        e
        for e in entries
        if e.coverage_untrusted or e.effective_score() >= min_score
    ]
