from __future__ import annotations

import os

from py_crap.report.base import FormatOptions, Formatter
from py_crap.scan.entries import Entries

MAX_PR_COMMENT_ROWS = 25


class PRCommentFormatter(Formatter):
    def format(self, entries: Entries, opts: FormatOptions) -> None:
        if entries is None:
            raise ValueError("entries list shouldn't be None")

        sorted_entries = entries.for_pr_comment()
        crappy = [e for e in sorted_entries if e.effective_score() > opts.threshold]

        self._write_header(opts.writer, sorted_entries, crappy, opts.threshold)

        display = crappy[:MAX_PR_COMMENT_ROWS] if len(crappy) > MAX_PR_COMMENT_ROWS else crappy
        self._write_crappy_table(opts.writer, display, len(sorted_entries), opts.base_dir)

        unreliable = [e for e in sorted_entries if e.coverage_untrusted]
        self._write_unreliable(opts.writer, unreliable, opts.detailed)

        unavailable = [e for e in sorted_entries if e.coverage_warning]
        self._write_unavailable(opts.writer, unavailable)

    @staticmethod
    def _write_header(writer, sorted_entries, crappy, threshold):
        writer.write("<!-- py-crap-report -->\n\n")
        if not crappy:
            writer.write("## No crappy functions\n")
        else:
            writer.write(f"## {len(crappy)} crappy function(s)\n")
        writer.write(f"\n{len(sorted_entries)} function(s) analyzed &middot; threshold {threshold:.0f}\n\n")

    @staticmethod
    def _write_crappy_table(writer, crappy, total, base_dir):
        if not crappy:
            return

        writer.write("| | CRAP | CC | Cov % | Function | Location |\n")
        writer.write("|---|---:|---:|---:|---|---|\n")
        for e in crappy:
            loc = _format_pr_location(e, base_dir)
            cov = f"{e.coverage:.1f}%"
            if e.coverage_untrusted:
                cov += " \u26a0"
            writer.write(
                f"| \u2717 | {e.effective_score():.2f} | {e.complexity} | {cov} | "
                f"`{e.func_name}` | {loc} |\n"
            )

        if total > MAX_PR_COMMENT_ROWS:
            writer.write(f"\n&hellip;and {total - MAX_PR_COMMENT_ROWS} more\n")
        writer.write("\n")

    @staticmethod
    def _write_unreliable(writer, unreliable, detailed):
        if not unreliable:
            return

        writer.write("\n## \u26a0\ufe0f Unreliable Coverage\n\n")
        if detailed:
            writer.write("| Function | CRAP | Effective CRAP | Mutation Score | Survived Mutants |\n")
            writer.write("|---|---:|---:|---:|---|\n")
            for e in unreliable:
                mutants_str = _format_mutants_str(e.mutation_details)
                writer.write(
                    f"| `{e.func_name}` | {e.crap:.2f} | {e.effective_crap:.2f} | "
                    f"{e.mutation_score * 100:.1f}% | {mutants_str} |\n"
                )
        else:
            writer.write("| Function | CRAP | Effective CRAP | Mutation Score |\n")
            writer.write("|---|---:|---:|---:|\n")
            for e in unreliable:
                writer.write(
                    f"| `{e.func_name}` | {e.crap:.2f} | {e.effective_crap:.2f} | "
                    f"{e.mutation_score * 100:.1f}% |\n"
                )

    @staticmethod
    def _write_unavailable(writer, unavailable):
        if not unavailable:
            return
        writer.write("\n## \u26a0\ufe0f Coverage Unavailable\n\n")
        writer.write("| Function | Location | Reason |\n")
        writer.write("|---|---|---|\n")
        for e in unavailable:
            loc = _format_pr_location(e, "")
            writer.write(f"| `{e.func_name}` | {loc} | {e.coverage_warning} |\n")


def _format_pr_location(e, base_dir):
    loc = f"`{e.file}:{e.line}`"
    if base_dir:
        try:
            rel = os.path.relpath(e.file, base_dir)
            if rel != e.file:
                loc = f"`{rel}:{e.line}`"
        except ValueError:
            pass
    return loc


def _format_mutants_str(details):
    if not details:
        return ""
    parts = []
    for md in details:
        s = f"`{md.mutant_type}`@L{md.line}"
        if md.original_text and md.replacement_text:
            s += f"<br>`{md.original_text}` &rarr; `{md.replacement_text}`"
        parts.append(s)
    return ", ".join(parts)
