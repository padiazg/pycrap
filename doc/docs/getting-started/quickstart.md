# Quick Start

This guide walks through your first CRAP score scan in under two minutes.

## 1. Install py-crap

!!! tip pip not found
    If `pip` is not found, try `pip3` or `python3 -m pip` instead.
    Inside an active virtual environment `pip` always works.

```shell
pip install py-crap
```

## 2. Run a Scan

Point `py-crap scan` at a directory:

```shell
py-crap scan
```

Example output:

```
┌───┬────────┬────┬───────────────────┬───────────────────┬─────────────────────────┐
│   │ CRAP   │ CC │ COVERAGE          │ FUNCTION          │ LOCATION                │
├───┼────────┼────┼───────────────────┼───────────────────┼─────────────────────────┤
│ ✗ │ 156.25 │ 12 │ ░░░░░░░░░░        │ analyze_complex   │ src/core/complex.py:5   │
│ ▲ │  42.50 │  5 │ ████░░░░░░        │ scan_modules      │ src/core/scan.py:28     │
│ ✓ │   4.00 │  2 │ ██████████ 100.0% │ execute           │ src/cli/main.py:170     │
└───┴────────┴────┴───────────────────┴───────────────────┴─────────────────────────┘

1/3 function(s) exceed threshold CRAP 30.
```

Columns:

- **Status** — `✗` above threshold, `▲` between half-threshold and threshold, `✓` below threshold
- **CRAP** — the computed CRAP score
- **CC** — cyclomatic complexity
- **Coverage** — test coverage as a percentage with a visual bar
- **Function** — function name (with `Class.` prefix for methods)
- **Location** — file path and line number

## 3. Filter Results

### Show only the worst offenders

```shell
py-crap scan --top 10
```

### Hide entries below a minimum score

```shell
py-crap scan --min 10
```

### Exclude test files and testdata

```shell
py-crap scan --exclude '.*_test\.py' --exclude 'testdata/.*\.py'
```

### Exclude generated files

```shell
py-crap scan --exclude '__pycache__/.*' --exclude '\.pb\..*\.py'
```

## 4. Fail CI on High Scores

```shell
py-crap scan --fail-above --threshold 30
```

Exits with code 1 if any function's CRAP score exceeds 30.

## 5. Machine-Readable Output

### JSON

```shell
py-crap scan --format json
```

Output:

```json
{
  "$schema": "https://raw.githubusercontent.com/padiazg/py-crap/main/schemas/report-v1.json",
  "version": "1.0.0",
  "entries": [
    {
      "file": "src/core/complex.py",
      "package": "core",
      "function": "analyze_complex",
      "line": 5,
      "cyclomatic": 12,
      "coverage": 0.0,
      "crap": 156.25
    }
  ]
}
```

### GitHub Actions annotations

```shell
py-crap scan --format github --threshold 15
::warning file=src/core/scanner.py,line=149::src/core/scanner.py:149 run_tests CRAP score 19.6 (CC=7, cov=36.4%) exceeds threshold 15
::warning file=src/core/analyzer.py,line=62::src/core/analyzer.py:62 Analyzer.analyze CRAP score 17.1 (CC=14, cov=75.0%) exceeds threshold 15
```

Emits `::warning` annotations that GitHub Actions renders as PR comments.

### SARIF

```shell
py-crap scan --format sarif > report.sarif
```

Outputs [SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/) compliant JSON. Compatible with Azure DevOps, GitHub code scanning, VS Code, and other tools that support the SARIF standard.

### Pull request comments

```shell
py-crap scan --format pr-comment
```

Generates a markdown table with status symbols, CRAP scores, complexity, coverage, function names, and file locations. Formatted for pasting directly into pull request comments.

### Write to file

```shell
py-crap scan --output report.json
py-crap scan -o report.json
```

The `--output` / `-o` flag writes results to a file instead of stdout. Works with any format.

## 6. Control Missing Coverage Policy

When a function has no coverage data, decide how to handle it:

```shell
# Assume 0% coverage (default) — worst case
py-crap scan --missing pessimistic

# Assume 100% coverage — best case
py-crap scan --missing optimistic

# Skip functions with no coverage
py-crap scan --missing skip
```
