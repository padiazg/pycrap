# Changelog

All notable changes to py-crap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 - 2025-07-06

### Added

- Initial release of py-crap
- `scan` command — analyze Python projects and calculate CRAP scores
- AST-based cyclomatic complexity via `py_crap/complexity` (adapted from go-crap's gocyclo)
- Coverage profiling via `py_crap/coverage` — auto-runs `coverage run -m pytest`, falls back to existing `coverage.xml`
- Double-index merge — joins coverage and complexity by `(filepath, funcname)` without path resolution issues
- CRAP formula — `CC² × (1 - coverage/100)³ + CC`
- Missing coverage policy — `pessimistic` (default), `optimistic`, `skip`
- Output formatters:
  - `table` — human-readable with status symbols and coverage bars (rich)
  - `json` — structured output with schema URL
  - `github` — GitHub Actions workflow annotation format
  - `sarif` — SARIF 2.1.0 compliant JSON for static analysis tools
  - `pr-comment` — markdown table formatted for pull request comments
- Mutation testing integration — parses mutmut JSON reports and annotates CRAP entries
- Filtering — `--top N`, `--min score`, `--exclude regex`
- CI integration — `--fail-above` exits with code 1
- Coverage unavailable warnings propagated through merge → score → formatters
- Doc site at `doc/` with full documentation
