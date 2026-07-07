from __future__ import annotations

import os

from py_crap.report.base import FormatOptions, Formatter
from py_crap.scan.entries import Entries
from py_crap.score.crap import CRAPEntry


class GithubFormatter(Formatter):
    def format(self, entries: Entries, opts: FormatOptions) -> None:
        if entries is None:
            raise ValueError("entries list shouldn't be None")

        for e in entries.list:
            effective_crap = e.effective_score()
            file = _resolve_file(e, opts.base_dir)

            if e.coverage_warning:
                opts.writer.write(
                    f"::warning file={file},line={e.line}::{e.coverage_warning}\n"
                )

            if e.coverage_untrusted:
                msg = (
                    f"{file}:{e.line} {e.func_name} "
                    f"[coverage not reliable (mutation score: {e.mutation_score * 100:.1f}%)]"
                )
                opts.writer.write(
                    f"::warning file={file},line={e.line}::{msg}\n"
                )

            if effective_crap > opts.threshold:
                msg = (
                    f"{file}:{e.line} {e.func_name} "
                    f"CRAP score {effective_crap:.1f} (CC={e.complexity}, "
                    f"cov={e.coverage:.1f}%) exceeds threshold {opts.threshold:.0f}"
                )
                if e.coverage_untrusted:
                    msg += (
                        f" [coverage not reliable (mutation score: "
                        f"{e.mutation_score * 100:.1f}%)]"
                    )
                opts.writer.write(
                    f"::warning file={file},line={e.line}::{msg}\n"
                )


def _resolve_file(e: CRAPEntry, base_dir: str) -> str:
    if not base_dir:
        return e.file
    try:
        rel = os.path.relpath(e.file, base_dir)
        return rel
    except ValueError:
        return e.file
