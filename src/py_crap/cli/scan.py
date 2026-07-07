from __future__ import annotations

import sys

import click

from py_crap.report.base import FormatOptions
from py_crap.report.github import GithubFormatter
from py_crap.report.json_report import JSONFormatter
from py_crap.report.pr_comment import PRCommentFormatter
from py_crap.report.sarif import SARIFFormatter
from py_crap.report.table import TableFormatter
from py_crap.scan.scan import Options
from py_crap.scan.scan import scan as run_scan


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "-t", "--threshold",
    default=30.0,
    show_default=True,
    help="Score above which a function is marked as problematic",
)
@click.option(
    "--fail-above",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any function exceeds the threshold",
)
@click.option(
    "-f", "--format",
    type=click.Choice(["table", "json", "github", "sarif", "pr-comment"]),
    default="table",
    show_default=True,
    help="Output format",
)
@click.option(
    "--top",
    type=int,
    default=0,
    help="Show only the N worst offenders (0 = all)",
)
@click.option(
    "--min",
    type=float,
    default=0,
    help="Hide entries below this score",
)
@click.option(
    "--missing",
    type=click.Choice(["pessimistic", "optimistic", "skip"]),
    default="pessimistic",
    show_default=True,
    help="Policy for functions without coverage",
)
@click.option(
    "--exclude",
    multiple=True,
    default=None,
    help="Exclude files matching this regex (repeatable)",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose (debug-level) logging",
)
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Output file path (default: stdout)",
)
@click.option(
    "--mutation-report",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to mutmut JSON mutation report",
)
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Include mutation failure details in report output",
)
def scan_cmd(
    path: str,
    threshold: float,
    fail_above: bool,
    format: str,
    top: int,
    min: float,
    missing: str,
    exclude: tuple[str, ...],
    verbose: bool,
    output: str | None,
    mutation_report: str | None,
    detailed: bool,
) -> None:
    """Analyze Python modules and calculate CRAP scores."""
    if verbose:
        _log("debug", f"Scanning path: {path}")

    options = Options(
        path=path,
        exclude=list(exclude) if exclude else [],
        missing=missing,
        top=top,
        min_score=min,
        mutation_report=mutation_report or "",
        verbose=verbose,
    )

    entries = run_scan(options)

    writer = open(output, "w") if output else sys.stdout

    formatter = _resolve_formatter(format)
    opts = FormatOptions(
        writer=writer,
        base_dir=path,
        threshold=threshold,
        detailed=detailed,
    )

    try:
        formatter.format(entries, opts)
    finally:
        if output:
            writer.close()

    if fail_above and entries.threshold_exceeded(threshold):
        sys.exit(1)


def _resolve_formatter(fmt: str):
    match fmt:
        case "table" | "":
            return TableFormatter()
        case "json":
            return JSONFormatter()
        case "github":
            return GithubFormatter()
        case "sarif":
            return SARIFFormatter()
        case "pr-comment":
            return PRCommentFormatter()
        case _:
            raise ValueError(f"unknown format: {fmt}")


def _log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}", file=sys.stderr)
