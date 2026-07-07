## Mutation Testing

Mutation testing evaluates the quality of your tests by injecting small, deliberate changes (called **mutants**) into your source code and running tests to see if they catch them.

A mutant that gets caught by tests is **killed** — meaning your test caught the change. A mutant that **survives** means your tests have a blind spot: the code path was never meaningfully asserted.

Coverage alone can lie. A function with 100% line coverage can still have untested logical paths. Mutation testing catches that gap.

## Effective CRAP Score

When a mutation report is provided, py-crap calculates two scores per function:

- **`CRAP`** — based on test coverage (what `coverage run` reports)
- **`EffectiveCRAP`** — recalculated at 0% coverage when survived mutants exist

py-crap uses `EffectiveCRAP` for all sorting and filtering (`--top`, `--min`, `--fail-above`). This ensures functions with survived mutants appear at the top of reports even if their test coverage looks good.

`CoverageUntrusted` entries always survive `--top` truncation and `--min` filtering, guaranteeing they appear in every output.

## mutmut

[Mutmut](https://mutmut.readthedocs.io/) is a mutation testing tool for Python that py-crap integrates with via JSON reports.

### Installation

```shell
pip install mutmut
```

### Generating a report

```shell
mutmut run
```

Mutmut writes results to `.mutmut-cache/results.json`. This is the file py-crap reads.

### Recommended configuration

For reliable results, these settings are recommended:

| Setting | Purpose |
|---------|---------|
| `--paths-to-mutate src/` | Only mutate your source code, not tests |
| `--tests-dir tests/` | Point mutmut at your test directory |
| `--runner 'python -m pytest'` | Use pytest as the test runner |

Combined one-liner:

```shell
mutmut run --paths-to-mutate src/ --tests-dir tests/ --runner 'python -m pytest' \
  && py-crap scan --mutation-report .mutmut-cache/results.json --exclude '.*_test\.py' --top 10
```

## Mutation reports with py-crap

Use the `--mutation-report` flag to pass a mutmut JSON report to py-crap. py-crap matches mutants to functions by file and line range, then:

1. Counts **killed** vs **survived** mutants within each function's line range
2. If any mutant **survived** → coverage is marked **untrusted** → CRAP recalculated assuming 0% coverage
3. Computes `mutation_score` = `killed / (killed + survived)`

```shell
py-crap scan --mutation-report .mutmut-cache/results.json
```

Use `--detailed` alongside `--mutation-report` to include per-mutant details (type, line, original/replacement code):

```shell
py-crap scan --mutation-report .mutmut-cache/results.json --format json --detailed
```

### How mutation data surfaces in each format

| Format | Mutation indicator |
|--------|-------------------|
| `table` | ⚠ flag next to coverage percentage |
| `json` | `mutation_score`, `coverage_untrusted`, `mutation_details` array |
| `sarif` | `coverage-untrusted` result; survived mutations with code diffs appended to warning messages |
| `pr-comment` | "Unreliable Coverage" section + "Survived Mutants" column with inline code snippets |

## CI integration

### GitHub Actions

A practical CI setup uses two jobs: one to enforce a CRAP threshold on every push, and another to generate a PR comment with mutation data on pull requests.

```yaml
name: crap
on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  threshold:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install py-crap
        run: pip install py-crap
      - name: Score
        run: py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'

  pr-comment:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install mutmut py-crap
          pip install -e .
      - name: Mutation testing
        run: mutmut run --paths-to-mutate src/ --tests-dir tests/ --runner 'python -m pytest'
      - name: Generate PR comment
        run: >-
          py-crap scan
          --format pr-comment
          --threshold 30
          --exclude '.*_test\.py'
          --output pr-comment.md
          --mutation-report .mutmut-cache/results.json || true
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: crap-comment
          path: |
            pr-comment.md
          if-no-files-found: ignore
```

The `|| true` on the py-crap step ensures the PR comment is still uploaded even when functions exceed the threshold.

## Interpreting results

### `effective_crap` vs `crap`

When no survived mutants exist, `effective_crap` equals `crap`. When mutants survived, `effective_crap` is recalculated assuming 0% coverage — reflecting the true risk of untested logic.

### Finding survived mutants

```shell
# Survived mutants per function
py-crap scan --mutation-report .mutmut-cache/results.json --format json --detailed | \
  jq '.entries[] | select(.mutation_details != null) | {file, function, mutation_details}'

# Summary of mutation scores
py-crap scan --mutation-report .mutmut-cache/results.json --format json | \
  jq '[.entries[] | select(.coverage_untrusted == true)] | length'
```

A `mutation_score` of 1.0 means all mutants were killed. A score near 0 means most survived — coverage in that function is unreliable.

### mutmut report format

py-crap expects the JSON structure produced by `mutmut run`:

```json
[
  {
    "file": "src/pkg/foo.py",
    "line": 42,
    "mutator": "number_replacement",
    "type": "number",
    "status": "KILLED",
    "original_source": "42",
    "replacement_source": "0"
  },
  {
    "file": "src/pkg/foo.py",
    "line": 50,
    "mutator": "condition_boundary",
    "type": "condition",
    "status": "SURVIVED",
    "original_source": "x > 0",
    "replacement_source": "x >= 0"
  }
]
```

Mutants are matched to functions by file path and line range. A mutant within a function's start-to-end line range is attributed to that function.
