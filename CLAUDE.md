# py-crap

CRAP score calculator for Python projects. Calculates the CRAP score
(cyclomatic complexity x coverage) for every function in a Python project.
Inspired by go-crap (Go).

## Architecture

Modules are independent and independently testable:

- `py_crap/complexity` — AST walker computing McCabe cyclomatic complexity
- `py_crap/coverage` — coverage runner (`coverage run -m pytest`) + XML parser
- `py_crap/merge` — join by (filepath, funcname) with double index
- `py_crap/score` — CRAP formula + missing policy
- `py_crap/report` — formatters (table, json, github, sarif, pr-comment)
- `py_crap/mutation` — mutmut JSON parser + entry annotation
- `py_crap/scan` — unified pipeline orchestrating all steps
- `py_crap/cli` — click CLI with scan and version commands

## Critical Issue: path matching

Coverage and complexity produce paths in different formats.
See `py_crap/merge/merger.py` — NEVER canonicalize relative paths against CWD.
The double-index join approach avoids CWD resolution entirely.

## Test Generation

Use pytest for all tests. Table-driven tests preferred.
Use `pytest` with rich assertion introspection.

## Useful Commands

```shell
py-crap scan [path]                     # scan and show table
py-crap scan -f json                    # JSON output
py-crap scan --top 10                   # show only top 10
py-crap scan --fail-above -t 30         # exit 1 if threshold exceeded
pytest tests/ -v                        # run all tests
pytest tests/test_score.py -v           # specific test file
ruff check src/ tests/                  # lint
ruff format src/ tests/                 # format
```

## Attribution

`py_crap/complexity/analyzer.py` adapted from go-crap's gocyclo (BSD-3-Clause).
`py_crap/coverage/runner.py` adapted from go-crap's coverage scanner.
