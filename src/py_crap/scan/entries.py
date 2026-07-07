from __future__ import annotations

from typing import Optional

from py_crap.merge.merger import MergedEntry
from py_crap.mutation.annotator import annotate
from py_crap.mutation.mutmut_parser import MutmutReport, parse_mutmut_report
from py_crap.score.crap import CRAPEntry, MissingPolicy, score


class Entries:
    def __init__(
        self,
        merged: list[MergedEntry],
        policy: MissingPolicy,
        mutation_report_path: str = "",
    ) -> None:
        self.list = score(merged, policy)
        self._mutation_report_path = mutation_report_path
        self._apply_mutation(merged)

    def _apply_mutation(self, merged: list[MergedEntry]) -> None:
        if not self._mutation_report_path:
            return
        report = parse_mutmut_report(self._mutation_report_path)
        self.list = list(annotate(self.list, report, merged))

    def threshold_exceeded(self, threshold: float) -> bool:
        return any(e.effective_score() > threshold for e in self.list)

    def for_table(self) -> list[CRAPEntry]:
        return sorted(
            self.list,
            key=lambda e: (e.effective_score(), e.mutation_score),
            reverse=True,
        )

    def for_pr_comment(self) -> list[CRAPEntry]:
        return sorted(
            self.list,
            key=lambda e: e.effective_score(),
            reverse=True,
        )
