from __future__ import annotations

from rich.console import Console
from rich.table import Table as RichTable

from py_crap.report.base import FormatOptions, Formatter
from py_crap.scan.entries import Entries
from py_crap.score.crap import CRAPEntry


class TableFormatter(Formatter):
    def format(self, entries: Entries, opts: FormatOptions) -> None:
        if entries is None:
            raise ValueError("entries list shouldn't be None")

        sorted_entries = entries.for_table()

        table = RichTable()
        table.add_column("", no_wrap=True)
        table.add_column("CRAP", justify="right")
        table.add_column("CC", justify="right")
        table.add_column("Coverage", justify="left")
        table.add_column("Function")
        table.add_column("Location")

        failed = 0
        warning_set: set[str] = set()
        warning_seen = False

        for e in sorted_entries:
            if e.effective_score() > opts.threshold:
                failed += 1
            status = status_symbol(e.effective_score(), opts.threshold)
            cov_bar = coverage_bar(e.coverage)
            cov_str = _format_cov_string(e)

            loc = _format_location(e, opts.base_dir)
            table.add_row(
                status,
                f"{e.effective_score():.2f}",
                str(e.complexity),
                f"{cov_bar} {cov_str}",
                e.func_name,
                loc,
            )
            if e.coverage_warning:
                warning_seen = True

        console = Console(file=opts.writer)
        console.print("")
        console.print(table)

        total = len(sorted_entries)
        if total > 0:
            console.print(
                f"{failed}/{total} function(s) exceed threshold CRAP {opts.threshold:.0f}."
            )

        if warning_seen:
            console.print("")
            for e in sorted_entries:
                if e.coverage_warning and e.coverage_warning not in warning_set:
                    warning_set.add(e.coverage_warning)
                    console.print(f"coverage unavailable for {e.coverage_warning}")


def status_symbol(crap_score: float, threshold: float) -> str:
    if crap_score > threshold:
        return "\u2717"
    if crap_score > threshold / 2:
        return "\u25b2"
    return "\u2713"


def coverage_bar(pct: float) -> str:
    filled = int(pct / 10)
    empty = 10 - filled
    return "\u2588" * filled + "\u2591" * empty


def _format_cov_string(e: CRAPEntry) -> str:
    if e.coverage_warning:
        return "N/A \u26a1"
    cov_str = f"{e.coverage:.1f}%"
    if e.coverage_untrusted:
        cov_str += " \u26a0"
    return cov_str


def _format_location(e: CRAPEntry, base_dir: str) -> str:
    loc = f"{e.file}:{e.line}"
    if base_dir:
        rel = _relativize(e.file, base_dir)
        if rel != e.file:
            loc = f"{rel}:{e.line}"
    return loc


def _relativize(file_path: str, base_dir: str) -> str:
    import os
    try:
        rel = os.path.relpath(file_path, base_dir)
        return rel
    except ValueError:
        return file_path
