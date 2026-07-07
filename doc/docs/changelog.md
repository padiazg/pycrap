# Changelog

## 0.1.0 (2025-07-06)

Initial release.

- `scan` command with 5 output formats (table, json, github, sarif, pr-comment)
- Cyclomatic complexity analysis via built-in AST walker
- Coverage auto-run via `coverage run -m pytest` + XML parser
- Merge engine joining complexity and coverage by (filepath, funcname)
- CRAP score formula with pessimistic/optimistic/skip missing coverage policy
- Mutation testing integration with mutmut JSON reports
- Filtering by `--top` and `--min`, `--fail-above` for CI
- Exclude patterns via `--exclude` flag (repeatable)
- Output redirection via `--output` / `-o`
