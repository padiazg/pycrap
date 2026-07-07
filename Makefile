PACKAGE := py-crap
MODULE  := py_crap

.PHONY: build test lint typecheck clean fmt help install preflight

build:
	uv pip install -e ".[dev]"

test:
	pytest -v --tb=short

lint:
	ruff check src/ tests/

typecheck:
	mypy src/py_crap/ --ignore-missing-imports

clean:
	rm -rf build/ dist/ *.egg-info/ .coverage coverage.xml .mypy_cache/ .ruff_cache/ .pytest_cache/

fmt:
	ruff format src/ tests/

preflight: lint typecheck test

install: build

help:
	@echo "build      - install package in editable mode"
	@echo "test       - run tests with verbose output"
	@echo "lint       - run ruff linter"
	@echo "typecheck  - run mypy type checker"
	@echo "clean      - remove build artifacts"
	@echo "fmt        - format source code with ruff"
	@echo "preflight  - run lint, typecheck, and tests"
	@echo "help       - show this help"
