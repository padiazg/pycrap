from __future__ import annotations

import json
import os

from py_crap.report.base import FormatOptions, Formatter
from py_crap.scan.entries import Entries
from py_crap.score.crap import CRAPEntry


def _relativize(file_path: str, base_dir: str) -> str:
    if not base_dir:
        return file_path
    try:
        return os.path.relpath(file_path, base_dir)
    except ValueError:
        return file_path


class JSONReport:
    def __init__(self) -> None:
        self.schema = "https://raw.githubusercontent.com/padiazg/py-crap/main/schemas/report-v1.json"
        self.version = "1.0.0"
        self.entries: list[dict] = []


class JSONFormatter(Formatter):
    def format(self, entries: Entries, opts: FormatOptions) -> None:
        if entries is None:
            raise ValueError("entries list shouldn't be None")

        report = {
            "$schema": "https://raw.githubusercontent.com/padiazg/py-crap/main/schemas/report-v1.json",
            "version": "1.0.0",
            "entries": [_convert_entry(e, opts) for e in entries.list],
        }

        opts.writer.write(json.dumps(report, indent=2))
        opts.writer.write("\n")


def _convert_entry(e: CRAPEntry, opts: FormatOptions) -> dict:
    file = _relativize(e.file, opts.base_dir) if opts.base_dir else e.file

    entry: dict = {
        "file": file,
        "function": e.func_name,
        "package": e.package,
        "line": e.line,
        "cyclomatic": e.complexity,
        "crap": e.crap,
        "effective_crap": e.effective_crap,
        "mutation_score": e.mutation_score,
        "coverage_untrusted": e.coverage_untrusted,
        "coverage_warning": e.coverage_warning,
    }

    if e.class_name:
        entry["class"] = e.class_name

    if opts.detailed and e.mutation_details:
        entry["mutation_details"] = [
            {
                "type": md.mutant_type,
                "mutator_name": md.mutator_name,
                "file": md.file,
                "line": md.line,
                "status": md.status,
                "original_text": md.original_text,
                "replacement_text": md.replacement_text,
            }
            for md in e.mutation_details
        ]

    if not e.coverage_warning:
        entry["coverage"] = e.coverage

    return entry
