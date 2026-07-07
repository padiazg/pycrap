# py-crap

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

CRAP score calculator for Python projects. Calculates the CRAP score (cyclomatic complexity × coverage) for every function in a Python project. Inspired by [go-crap](https://github.com/padiazg/go-crap) (Go) and [cargo-crap](https://github.com/Boehs/cargo-crap) (Rust).

## Installation

> If `pip` is not found, try `pip3` or `python3 -m pip` instead.
> Inside an active virtual environment `pip` always works.

```shell
pipx install py-crap    # recommended — auto-isolates in venv
# or
pip install py-crap      # requires active venv (PEP 668)
```

Or build from source:

```shell
git clone https://github.com/padiazg/py-crap.git
cd py-crap
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```shell
py-crap scan [path] [flags]
```

Scans the Python project at the given path (defaults to `.`) and outputs a ranked table of functions by CRAP score.

### Example

```shell
# Scan current project
py-crap scan

# Show only the 10 worst offenders
py-crap scan --top 10

# Fail CI if any function exceeds threshold
py-crap scan --fail-above --threshold 30

# Exclude test files
py-crap scan --exclude '.*_test\.py'
```

### Flags

| Flag | Short | Description | Default |
| - | - | - | - |
| `--threshold` | `-t` | Score above which a function is marked as problematic | `30.0` |
| `--fail-above` | | Exit with code 1 if any function exceeds the threshold | `false` |
| `--format` | `-f` | Output format: `table`, `json`, `github`, `sarif`, or `pr-comment` | `table` |
| `--top` | | Show only the N worst offenders (0 = all) | `0` |
| `--min` | | Hide entries below this score | `0` |
| `--missing` | | Policy for functions without coverage: `pessimistic`, `optimistic`, or `skip` | `pessimistic` |
| `--exclude` | | Exclude files matching this regex (repeatable). Use `.*` for any path depth. e.g. `.*_test\.py` to exclude test files | none |
| `--verbose` | | Enable verbose (debug-level) logging | `false` |
| `--output` | `-o` | Output file path (default: stdout) | stdout |
| `--mutation-report` | | Path to mutmut JSON mutation report to validate coverage reliability | `""` |
| `--detailed` | | Include mutation failure details (original code, replacement, line) in report output | `false` |
| `--help` | `-h` | Help for scan | — |

### Output Formats

| Format | Description |
| - | - |
| `table` | Human-readable terminal output with status symbols and coverage bars |
| `json` | Structured output with `$schema` URL, suitable for CI pipelines |
| `github` | GitHub Actions workflow annotations (`::warning`) |
| `sarif` | SARIF 2.1.0 compliant JSON for static analysis tools |
| `pr-comment` | Markdown table formatted for pull request comments |

### Coverage Unavailable Warning

When a Python module fails to build or run tests, its coverage data is unavailable.
py-crap detects this and reports it in all output formats:

- `table` — coverage column shows `N/A ‼` with a footer listing unavailable modules
- `json` — `coverage` is `null` and `coverage_warning` contains the error message
- `github` — `::warning` annotation with the module error
- `sarif` — result with `RuleID: "py-crap/coverage-unavailable"`
- `pr-comment` — separate "Coverage Unavailable" section

### Example: SARIF output

```shell
py-crap scan --format sarif > crap.sarif
```

### Example: PR comment output

```shell
py-crap scan --format pr-comment > pr-comment.md
```

### Example: Mutation report validation

```shell
py-crap scan --mutation-report mutmut-report.json
```

When a function has **lived** mutants (mutations that survived because tests didn't catch them), py-crap marks the coverage as unreliable (`⚠`) and recalculates the CRAP score assuming 0% coverage. This catches functions that appear well-tested but have blind spots.

### Example: Detailed mutation output

```shell
py-crap scan --mutation-report mutmut-report.json --format json --detailed
```

The `--detailed` flag includes full mutation failure details in the output: `type`, `line`, `original_code`, and `replacement_code` for each survived mutant. In `json` format, these appear as a `mutation_details` array per entry. In `sarif` and `pr-comment` formats, survived mutations with code snippets are appended to the warning messages.

## What is CRAP?

CRAP = **C**yclomatic **R**eadability **A**nd **P**redictability. It measures how expensive a function is to test.

$CRAP(CC, coverage) = CC^2 \times \left(1 - \frac{coverage}{100}\right)^3 + CC$

A function with high cyclomatic complexity and low coverage scores the worst. A simple, fully tested function scores the best.

| CRAP Range | Meaning |
| - | - |
| 0 – 10 | Well-tested, simple function |
| 10 – 30 | Moderate complexity, should be tested |
| 30 – 50 | High CRAP — refactoring or more tests needed |
| 50+ | Critical — likely hard to test, complex logic |

## How It Works

```
py-crap scan
  │
  ├── scan.Scan()              — unified pipeline, discovers modules, filters, and ranks
  │   ├── coverage.run()       — auto-run coverage, parse XML report
  │   ├── complexity.analyze() — walk AST, compute cyclomatic complexity
  │   ├── merge.merge()        — join by (filepath, funcname), propagate coverage warnings
  │   ├── score.score()        — apply CRAP formula + missing policy
  │   ├── mutation.annotate()  — validate coverage with mutation testing (optional)
  │   └── report.format()      — table / json / github / sarif / pr-comment
```

- **`py_crap/complexity`** — AST walking to compute cyclomatic complexity (adapted from go-crap's gocyclo)
- **`py_crap/coverage`** — auto-runs `coverage run -m pytest`, parses Cobertura XML
- **`py_crap/merge`** — double-index join of coverage and complexity data, propagates coverage-unavailable warnings
- **`py_crap/score`** — CRAP formula + missing coverage policy + CRAPEntry
- **`py_crap/mutation`** — parses mutmut JSON mutation reports and annotates CRAP entries with coverage reliability
- **`py_crap/report`** — output formatters (table, JSON, GitHub, SARIF, PR comment)
- **`py_crap/cli`** — click CLI with scan and version commands

## CI Integration

```yaml
# .github/workflows/crap.yml
- run: py-crap scan --fail-above --threshold 30 --format github
```

- `--fail-above` exits with code 1 when any function exceeds the threshold
- `--format github` emits `::warning` annotations that render as PR comments
- `--format sarif` outputs SARIF 2.1.0 for integration with code scanning tools
- `--format pr-comment` generates a markdown table for pull request comments
- `--output -o` writes results to a file instead of stdout
- `--mutation-report` validates coverage reliability against mutation testing results
- `--detailed` includes mutation failure details (code, line, type) in report output
- Coverage-unavailable warnings are emitted for modules where `coverage run` fails

### Badge

Add a status badge to your `README.md` to show the latest master analysis:

```markdown
[![CRAP analysis](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/crap.yml/badge.svg?branch=master)](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/crap.yml)
```

Requires the workflow to trigger on `push: branches: [master]` (not `branches-ignore`).

## Prior art and references

- [Savoia, A. & Evans, B. (2007). *The CRAP Metric.*](https://www.artima.com/weblogs/viewpost.jsp?thread=210575)
- [Crap4j](http://www.crap4j.org/) — the original Java implementation.
- [go-crap](https://github.com/padiazg/go-crap) — CRAP score calculator for Go.
- [cargo-crap](https://github.com/minikin/cargo-crap) — CRAP score calculator for Rust.

## License

This project is licensed under the [MIT License](LICENSE).

## Full Documentation

For a complete guide covering all flags, examples, and the CRAP formula in detail, see [the documentation site](https://padiazg.github.io/py-crap).
