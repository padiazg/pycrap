# GitHub Actions

Use py-crap in GitHub Actions workflows to enforce CRAP score thresholds and generate pull request comments.

## Threshold enforcement

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
      - name: Install project
        run: pip install -e .
      - name: Run CRAP check
        run: py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
```

## GitHub Annotations

Use `--format github` to emit `::warning` annotations:

```yaml
      - name: Annotate PR
        run: py-crap scan --format github --threshold 30 --exclude '.*_test\.py'
```

GitHub Actions renders these as inline warnings on the affected files in pull request diffs.

## SARIF upload

Upload SARIF output to GitHub code scanning:

```yaml
      - name: Generate SARIF
        run: py-crap scan --format sarif --threshold 30 --exclude '.*_test\.py' --output py-crap.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: py-crap.sarif
```

## PR Comment

Generate a markdown summary and post it as a PR comment:

```yaml
  pr-comment:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install py-crap
        run: pip install py-crap
      - name: Install project
        run: pip install -e .
      - name: Generate PR comment
        run: py-crap scan --format pr-comment --threshold 30 --output pr-comment.md --exclude '.*_test\.py' || true
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: pr-comment
          path: pr-comment.md
```

## Fork-safe PR comment with mutation testing

For PRs from forked repositories, use `pull_request_target` with artifact passing:

```yaml
name: crap-comment
on:
  workflow_run:
    workflows: ["crap-threshold"]
    types:
      - completed

jobs:
  comment:
    runs-on: ubuntu-latest
    if: >
      github.event.workflow_run.event == 'pull_request' &&
      github.event.workflow_run.conclusion == 'success'
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: pr-comment
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
      - name: Post comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const comment = fs.readFileSync('pr-comment.md', 'utf8');
            const prNumber = fs.readFileSync('pr-number.txt', 'utf8').trim();
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: parseInt(prNumber),
              body: comment
            });
```

## Matrix build

Test multiple Python versions:

```yaml
jobs:
  threshold:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install py-crap
        run: pip install py-crap
      - name: Check CRAP
        run: py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
```
