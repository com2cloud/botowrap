.PHONY: install test lint format clean build docs

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build

docs:
	cd docs && make html

coverage:
	pytest --cov=botowrap --cov-report=html --cov-report=term-missing

typecheck:
	mypy .

check: lint test typecheck

precommit: format lint test typecheck

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make install    - Install package in development mode"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make build      - Build package"
	@echo "  make docs       - Build documentation"
	@echo "  make coverage   - Run tests with coverage"
	@echo "  make typecheck  - Run type checking"
	@echo "  make check      - Run all checks"
	@echo "  make precommit  - Run all checks before commit"
