# Contributing to py-crap

Thanks for your interest in contributing.

## Reporting bugs

Open an issue using the bug report template. Include:
- py-crap version (`py-crap version`)
- Python version (`python --version`)
- OS and architecture
- Steps to reproduce
- Expected vs actual behavior

## Proposing features

Open an issue using the feature request template.
Describe the use case before proposing a solution.

## Development setup

> If `pip` is not found, try `pip3` or `python3 -m pip` instead.
> Inside an active virtual environment `pip` always works.

```shell
git clone https://github.com/padiazg/py-crap.git
cd py-crap
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
ruff check src/ tests/
```

Requirements: Python 3.10+, pytest, ruff.

## Pull request process

1. Fork the repo and create a feature branch from `main`.
2. Make your changes. Keep commits atomic.
3. Run `pytest tests/` and `ruff check src/ tests/` — both must pass.
4. Open a PR against `main`. Fill in the PR template.
5. One approval required before merge.

## Code style

- Tests: table-driven with pytest. Prefer pytest over unittest.
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- No `sys.exit` outside CLI handlers.
- Use `click` for CLI, `rich` for table output.

## License

By contributing you agree your contributions are licensed under the MIT License.
