from enum import IntEnum
from typing import NamedTuple, Optional

from py_crap.merge.merger import MergedEntry


class MissingPolicy(IntEnum):
    PESSIMISTIC = 0
    OPTIMISTIC = 1
    SKIP = 2


class MutationDetail(NamedTuple):
    file: str
    mutant_type: str
    mutator_name: str
    original_text: str
    replacement_text: str
    status: str
    line: int


class CRAPEntry(NamedTuple):
    file: str
    func_name: str
    class_name: str
    package: str
    complexity: int
    coverage: float
    line: int
    crap: float
    effective_crap: float
    mutation_score: float
    coverage_untrusted: bool
    coverage_warning: str
    skipped: bool
    mutation_details: tuple[MutationDetail, ...]

    def effective_score(self) -> float:
        return self.effective_crap or self.crap


def crap(complexity: int, coverage_pct: float) -> float:
    c = float(complexity)
    cov = coverage_pct / 100.0
    return c * c * (1 - cov) ** 3 + c


def score(
    entries: list[MergedEntry], policy: MissingPolicy
) -> list[CRAPEntry]:
    result: list[CRAPEntry] = []
    for e in entries:
        if e.coverage is None:
            match policy:
                case MissingPolicy.PESSIMISTIC:
                    cov = 0.0
                case MissingPolicy.OPTIMISTIC:
                    cov = 100.0
                case MissingPolicy.SKIP:
                    result.append(
                        CRAPEntry(
                            file=e.file,
                            func_name=e.func_name,
                            class_name=e.class_name,
                            package=e.package,
                            complexity=e.complexity,
                            coverage=0.0,
                            line=e.line,
                            crap=float(e.complexity),
                            effective_crap=float(e.complexity),
                            mutation_score=0.0,
                            coverage_untrusted=False,
                            coverage_warning=e.coverage_warning,
                            skipped=True,
                            mutation_details=(),
                        )
                    )
                    continue
        else:
            cov = e.coverage

        s = crap(e.complexity, cov)
        result.append(
            CRAPEntry(
                file=e.file,
                func_name=e.func_name,
                class_name=e.class_name,
                package=e.package,
                complexity=e.complexity,
                coverage=cov,
                line=e.line,
                crap=s,
                effective_crap=s,
                mutation_score=0.0,
                coverage_untrusted=False,
                coverage_warning=e.coverage_warning,
                skipped=False,
                mutation_details=(),
            )
        )

    return result
