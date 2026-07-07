# Concepts

py-crap computes the CRAP score by combining two independent analyses and merging them:

## Pipeline Overview

```
py-crap scan
│
├── scan.scan()                   — orchestrator
│       ├── build exclude regex from --exclude flags
│       ├── coverage runner       — run coverage run -m pytest, produce XML
│       │       │
│       │       └── coverage data per (file, func)
│       │
│       ├── complexity.Analyzer() — walk AST, compute cyclomatic complexity
│       │       │
│       │       └── complexity data per (file, func)
│       │
│       ├── merge.merge()         — join by (filepath, funcname)
│       │       │
│       │       └── merged entries with CC + Coverage
│       │
│       ├── score.score()         — apply CRAP formula + missing policy
│       │       │
│       │       └── CRAP entries
│       │
│       └── apply filters         — sort descending, apply --min and --top
│
└── report.Format()               — table / json / github / sarif / pr-comment
        |
        └── output
```

## The Modules

Each module is independently testable:

| Module | Purpose |
| - | - |
| `py_crap/scan` | Orchestrates the pipeline: coverage, complexity, merge, score, filters |
| `py_crap/complexity` | AST walking to compute cyclomatic complexity |
| `py_crap/coverage` | Coverage runner + XML parser |
| `py_crap/merge` | Join coverage and complexity by `(filepath, funcname)` using a double index |
| `py_crap/score` | CRAP formula + missing coverage policy |
| `py_crap/mutation` | mutmut JSON report parser + entry annotation |
| `py_crap/report` | Output formatters (table, JSON, GitHub, SARIF, PR comment) |
| `py_crap/cli` | Click CLI with scan and version commands |

## Important: Path Matching

Coverage and complexity produce paths in different formats. The merge layer uses a double index to match them — **never canonicalize relative paths against CWD**.

## Function Name Matching

Coverage and complexity also produce function names in different formats. Coverage stores plain function names, while complexity stores names with class prefixes (e.g. `Calculator.add`). The merge layer normalizes both sides to bare method names before matching.
