from __future__ import annotations

import json
import os

from py_crap.report.base import FormatOptions, Formatter
from py_crap.scan.entries import Entries


class SARIFFormatter(Formatter):
    def format(self, entries: Entries, opts: FormatOptions) -> None:
        if entries is None:
            raise ValueError("entries list shouldn't be None")

        results: list[dict] = []
        for e in entries.list:
            effective_crap = e.effective_score()
            uri = _relativize_uri(e.file, opts.base_dir)

            if e.coverage_warning:
                results.append(self._result("go-crap/coverage-unavailable", "warning", e.coverage_warning, uri, e.line))

            if effective_crap > opts.threshold:
                name = e.func_name
                msg = (
                    f"Function {name} has CRAP score {effective_crap:.1f} "
                    f"(cyclomatic complexity {e.complexity}, coverage {e.coverage:.1f}%)"
                )
                if e.coverage_untrusted:
                    msg += (
                        f" [coverage not reliable (mutation score: "
                        f"{e.mutation_score * 100:.1f}%)]"
                    )
                    msg += self._format_mutant_details(opts.detailed, e.mutation_details)
                results.append(self._result("crap/high-score", "warning", msg, uri, e.line))

            if e.coverage_untrusted:
                msg = (
                    f"Coverage not reliable for {e.func_name} "
                    f"(mutation score: {e.mutation_score * 100:.1f}%)"
                )
                msg += self._format_mutant_details(opts.detailed, e.mutation_details)
                results.append(self._result("go-crap/coverage-untrusted", "warning", msg, uri, e.line))

        log = {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "py-crap",
                            "informationUri": "https://github.com/padiazg/py-crap",
                            "defaultConfiguration": {"level": "warning"},
                            "rules": [
                                {
                                    "id": "crap/high-score",
                                    "shortDescription": {"text": "CRAP score exceeds threshold"},
                                    "fullDescription": {
                                        "text": "The CRAP score (cyclomatic complexity x coverage) exceeds the threshold, indicating a function that is complex and/or poorly tested."
                                    },
                                }
                            ],
                        }
                    },
                    "results": results,
                }
            ],
        }

        json.dump(log, opts.writer, indent=2)
        opts.writer.write("\n")

    @staticmethod
    def _result(
        rule_id: str, level: str, text: str, uri: str, line: int
    ) -> dict:
        return {
            "ruleId": rule_id,
            "level": level,
            "message": {"text": text},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": uri},
                        "region": {"startLine": line},
                    }
                }
            ],
        }

    @staticmethod
    def _format_mutant_details(detailed: bool, details: tuple) -> str:
        if not detailed or not details:
            return ""
        msg = " survived mutations:"
        for md in details:
            msg += f" {md.mutant_type}@L{md.line}"
            if md.original_text and md.replacement_text:
                msg += f" ({md.original_text!r} -> {md.replacement_text!r})"
        return msg


def _relativize_uri(file_path: str, base_dir: str) -> str:
    if not base_dir:
        return file_path
    try:
        rel = os.path.relpath(file_path, base_dir)
        return rel.replace("\\", "/")
    except ValueError:
        return file_path
