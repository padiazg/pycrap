# CI Integrations

Integrate py-crap into your continuous integration pipeline to enforce CRAP score thresholds across all pull requests.

## Providers

- [GitHub Actions](github-actions.md) — threshold enforcement, PR annotations, matrix builds, SARIF code scanning, fork-safe PR comments with mutation testing
- [Gitea](gitea.md) — Gitea Actions with annotation support
- [GitLab CI](gitlab.md) — quality stage with JSON artifact
- [Azure DevOps](azure-devops.md) — pipeline with artifact upload
- [CircleCI](circleci.md) — quality workflow
- [Jenkins](jenkins.md) — pipeline job

## Tips

### Cache the binary

For CI systems with persistent workspaces (not clean checkouts), skip the install step:

```shell
py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
```

### Combine exclude patterns

Multiple `--exclude` flags stack:

```shell
py-crap scan \
  --exclude '.*_test\.py' \
  --exclude 'testdata/.*\.py' \
  --exclude '__pycache__/.*' \
  --exclude '\.pb\..*\.py'
```

### Threshold tuning

Start permissive, tighten over time:

```shell
# Phase 1: observe only (never fail)
py-crap scan --format json > crap-report.json

# Phase 2: enforce at a high threshold to see what fails
py-crap scan --fail-above --threshold 100

# Phase 3: tighten to production threshold
py-crap scan --fail-above --threshold 30

# Phase 4: strictest
py-crap scan --fail-above --threshold 15
```

### Debug logging in CI

```yaml
      - name: Debug scan
        run: py-crap scan --verbose --format json --exclude '.*_test\.py'
```

Use `--verbose` when diagnosing issues with module discovery, coverage parsing, or path matching in CI environments.

### Mutation report with CI

```yaml
      - name: Install mutmut
        run: pip install mutmut
      - name: Run mutation testing
        run: mutmut run --paths-to-mutate src/ --tests-dir tests/ --runner 'python -m pytest'
      - name: Run py-crap with mutation validation
        run: py-crap scan --mutation-report .mutmut-cache/results.json --fail-above --threshold 30
      - name: Generate detailed report
        run: py-crap scan --mutation-report .mutmut-cache/results.json --format json --detailed > crap-detailed.json
```

### Report parsing

The JSON output follows this schema:

```json
{
  "$schema": "https://raw.githubusercontent.com/padiazg/py-crap/main/schemas/report-v1.json",
  "version": "1.0.0",
  "entries": [
    {
      "file": "src/pkg/foo.py",
      "package": "pkg",
      "function": "Foo",
      "line": 42,
      "cyclomatic": 8,
      "coverage": 0.25,
      "crap": 125.0,
      "coverage_untrusted": false,
      "mutation_score": 0.8,
      "effective_crap": 125.0
    }
  ]
}
```

When `--detailed` is used alongside `--mutation-report`, each entry with survived mutants includes a `mutation_details` array:

```json
{
  "mutation_details": [
    {
      "type": "number",
      "mutator_name": "number_replacement",
      "file": "src/pkg/foo.py",
      "line": 50,
      "status": "SURVIVED",
      "original_text": "42",
      "replacement_text": "0"
    }
  ]
}
```

Use `jq` to filter or summarize:

```shell
# Count functions exceeding threshold
py-crap scan --format json --threshold 30 | jq '[.entries[] | select(.crap > 30)] | length'

# Worst offenders
py-crap scan --format json --top 5 | jq '.entries[] | "\(.file):\(.line) \(.function) CRAP=\(.crap)"'
```
