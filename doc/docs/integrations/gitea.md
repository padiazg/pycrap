# Gitea

Use py-crap in Gitea Actions to enforce CRAP score thresholds.

## Example workflow

```yaml
name: crap-check
on: [push, pull_request]

jobs:
  crap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install py-crap
        run: pip install py-crap
      - name: Install project
        run: pip install -e .
      - name: Check CRAP
        run: py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
```

## Gitea Annotations

Use the `github` format for Gitea Actions (it supports the same `::warning` annotation syntax):

```yaml
      - name: Annotate
        run: py-crap scan --format github --threshold 30 --exclude '.*_test\.py'
```
