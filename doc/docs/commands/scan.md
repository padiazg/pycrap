# scan

The `scan` command is the main entry point. It analyzes Python modules, computes CRAP scores, and outputs the results.

## Usage

```shell
py-crap scan [path] [flags]
```

**Arguments:**

| Argument | Description | Default |
| - | - | - |
| `path` | Directory to scan | `.` (current directory) |

## Flags

| Flag | Short | Description | Default |
| - | - | - | - |
| `--threshold` | `-t` | Score above which a function is marked as problematic | `30.0` |
| `--fail-above` | | Exit with code 1 if any function exceeds the threshold | `false` |
| `--format` | `-f` | Output format: `table`, `json`, `github`, `sarif`, or `pr-comment` | `table` |
| `--top` | | Show only the N worst offenders (0 = all). `CoverageUntrusted` entries always survive | `0` |
| `--min` | | Hide entries below this score. `CoverageUntrusted` entries are never hidden | `0` |
| `--missing` | | Policy for functions without coverage: `pessimistic`, `optimistic`, or `skip` | `pessimistic` |
| `--exclude` | | Exclude files matching this regex pattern (repeatable) | none |
| `--verbose` | | Enable verbose (debug-level) logging | `false` |
| `--output` | `-o` | Output file path (default: stdout) | stdout |
| `--mutation-report` | | Path to mutmut JSON mutation report | `""` (disabled) |
| `--detailed` | | Include mutation failure details in report output | `false` |

## Coverage Unavailable Warning

When a module fails to produce coverage data (test errors, import failures), coverage data is lost for all functions in that module. py-crap detects this and surfaces the error in all output formats:

- **table** — coverage column shows `N/A ⚡`, footer lists unavailable modules with error messages
- **json** — `coverage` is null, `coverage_warning` contains the error
- **github** — `::warning` annotation with module error
- **sarif** — result with `RuleID: "py-crap/coverage-unavailable"`
- **pr-comment** — "Coverage Unavailable" section

This is distinct from the `--missing` policy, which handles functions that have no coverage data because they were not exercised by tests.

## Examples

### Scan all packages

```shell
py-crap scan
```

### Scan a specific directory

```shell
py-crap scan ~/projects/my-api
```

### Show only the top 20 worst offenders

```shell
py-crap scan --top 20
```

### CI integration — fail on high CRAP scores

```shell
py-crap scan --fail-above --threshold 30 --format github
```

### Filter by minimum score

```shell
py-crap scan --min 10
```

### Exclude test files and generated code

```shell
py-crap scan --exclude '.*_test\.py' --exclude 'testdata/.*\.py' --exclude '__pycache__/.*'
```

### Machine-readable JSON output

```shell
py-crap scan --format json > report.json
```

### SARIF output

```shell
py-crap scan --format sarif > report.sarif
```

Outputs [SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/) compliant JSON for integration with code scanning tools, IDEs, and CI platforms that support SARIF.

### Pull request comment output

```shell
py-crap scan --format pr-comment > pr-comment.md
```

Generates a markdown table with status symbols, CRAP scores, complexity, coverage, and file locations — formatted for pasting into pull request comments.

### Write to file

```shell
py-crap scan --output report.json
py-crap scan -o report.json
```

Uses the `--output` / `-o` flag to write results to a file instead of stdout. Works with any format.

### Verbose / debug logging

```shell
py-crap scan --verbose
```

Enables debug-level logging to help diagnose issues with module discovery, coverage parsing, or path matching.

### Mutation report validation

```shell
py-crap scan --mutation-report .mutmut-cache/results.json
```

Validates coverage reliability by comparing mutation testing results against py-crap's coverage data. When a function has **survived** mutants (mutations that survived because tests didn't catch them), py-crap marks the coverage as unreliable and recalculates the CRAP score assuming 0% coverage.

Unreliable coverage is indicated by:

- A ⚠ warning next to the coverage percentage in `table` and `pr-comment` output
- An additional `coverage-untrusted` SARIF result in `sarif` format
- A mutation score in `json` output (`mutation_score` field)
- A `::warning` annotation in `github` format, emitted even when the CRAP score is below threshold
- An "Unreliable Coverage" section in `pr-comment` output listing all affected functions (always rendered when mutation report is provided)

### Detailed mutation output

```shell
py-crap scan --mutation-report .mutmut-cache/results.json --format json --detailed
```

The `--detailed` flag includes full mutation failure details in the report output:

- **JSON**: `mutation_details` array per entry with `type`, `mutator_name`, `file`, `line`, `status`, `original_text`, `replacement_text`
- **SARIF**: survived mutations appended to warning messages with type, line, and code diff
- **PR Comment**: `Survived Mutants` column in the Unreliable Coverage section, with code snippets inline
- **Table**: no change — still shows ⚠ for untrusted coverage
