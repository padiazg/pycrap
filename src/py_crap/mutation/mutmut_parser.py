import json
from typing import NamedTuple


class Mutant(NamedTuple):
    file: str
    line: int
    mutator_name: str
    type: str
    status: str
    original_text: str
    replacement_text: str


class MutmutReport(NamedTuple):
    mutants: list[Mutant]
    mutants_killed: int
    mutants_survived: int
    mutants_timeout: int
    mutants_total: int
    test_efficacy: float


def parse_mutmut_report(path: str) -> MutmutReport:
    with open(path) as f:
        data = json.load(f)

    mutants: list[Mutant] = []
    killed = survived = timeout = skipped = 0

    for entry in data:
        file = entry.get("file", "")
        line = entry.get("line", 0)
        mutator = entry.get("mutator", "")
        mtype = entry.get("type", mutator)
        status = entry.get("status", "SURVIVED").upper()
        original = entry.get("original_source", entry.get("original_text", ""))
        replacement = entry.get("replacement_source", entry.get("replacement_text", ""))

        mutants.append(
            Mutant(
                file=file,
                line=line,
                mutator_name=mutator,
                type=mtype,
                status=status,
                original_text=original,
                replacement_text=replacement,
            )
        )

        match status:
            case "KILLED":
                killed += 1
            case "SURVIVED" | "LIVED":
                survived += 1
            case "TIMEOUT":
                timeout += 1
            case _:
                skipped += 1

    total = killed + survived + timeout + skipped
    efficacy = killed / total * 100 if total > 0 else 0.0

    return MutmutReport(
        mutants=mutants,
        mutants_killed=killed,
        mutants_survived=survived,
        mutants_timeout=timeout,
        mutants_total=total,
        test_efficacy=efficacy,
    )
