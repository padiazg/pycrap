from py_crap.merge.merger import MergedEntry
from py_crap.mutation.mutmut_parser import Mutant, MutmutReport
from py_crap.score.crap import CRAPEntry, MutationDetail, crap


def build_mutant_file_suffix(path: str) -> str:
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    if len(parts) >= 3:
        return "/".join(parts[-3:])
    if len(parts) == 1:
        return parts[0]
    return "/".join(parts)


def classify_mutants(
    mutants: list[Mutant], start_line: int, end_line: int
) -> tuple[int, int, list[Mutant]]:
    killed = 0
    lived = 0
    lived_mutants: list[Mutant] = []
    for m in mutants:
        if start_line <= m.line <= end_line:
            match m.status:
                case "KILLED":
                    killed += 1
                case "SURVIVED" | "LIVED":
                    lived += 1
                    lived_mutants.append(m)
    return killed, lived, lived_mutants


def annotate(
    entries: list[CRAPEntry],
    report: MutmutReport,
    merged: list[MergedEntry],
) -> list[CRAPEntry]:
    if not report.mutants:
        return [e._replace(effective_crap=e.crap) for e in entries]

    end_line_map = {m.file: m.end_line for m in merged}
    mutants_by_file: dict[str, list[Mutant]] = {}
    for m in report.mutants:
        key = build_mutant_file_suffix(m.file)
        mutants_by_file.setdefault(key, []).append(m)

    result: list[CRAPEntry] = []
    for e in entries:
        if e.skipped or e.coverage == 0:
            result.append(e._replace(effective_crap=e.crap))
            continue

        end_line = end_line_map.get(e.file, e.line + 100)
        suffix = build_mutant_file_suffix(e.file)
        mutants = mutants_by_file.get(suffix, [])

        if not mutants:
            result.append(e._replace(effective_crap=e.crap))
            continue

        killed, lived, lived_muts = classify_mutants(mutants, e.line, end_line)

        if killed == 0 and lived == 0:
            result.append(e._replace(effective_crap=e.crap, mutation_score=-1.0))
            continue

        if lived > 0:
            mutation_score = killed / (killed + lived) if (killed + lived) > 0 else 0.0
            details = tuple(
                MutationDetail(
                    file=m.file,
                    mutant_type=m.type,
                    mutator_name=m.mutator_name,
                    original_text=m.original_text,
                    replacement_text=m.replacement_text,
                    status=m.status,
                    line=m.line,
                )
                for m in lived_muts
            )
            result.append(
                e._replace(
                    coverage_untrusted=True,
                    mutation_score=mutation_score,
                    effective_crap=crap(e.complexity, 0),
                    mutation_details=details,
                )
            )
        else:
            result.append(
                e._replace(
                    coverage_untrusted=False,
                    mutation_score=1.0,
                    effective_crap=e.crap,
                )
            )

    return result
