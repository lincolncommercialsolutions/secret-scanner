.PHONY: install test lint format clean run help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with Poetry
	poetry install

test:  ## Run tests with coverage
	poetry run pytest --cov=secret_scanner --cov-report=html --cov-report=term

test-quick:  ## Run tests without coverage
	poetry run pytest -v

lint:  ## Run linters (ruff)
	poetry run ruff check src/ tests/

lint-fix:  ## Fix auto-fixable linting issues
	poetry run ruff check --fix src/ tests/

format:  ## Format code with Black
	poetry run black src/ tests/

format-check:  ## Check formatting without modifying files
	poetry run black --check src/ tests/

clean:  ## Clean up generated files
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run:  ## Run scanner on current directory
	poetry run secret-scanner scan .

run-verbose:  ## Run scanner with verbose output
	poetry run secret-scanner scan --verbose .

run-git:  ## Run scanner on Git history
	poetry run secret-scanner scan --git-history .

ui:  ## Launch web UI
	poetry run secret-scanner ui

validate:  ## Validate rules configuration
	poetry run secret-scanner validate

list-rules:  ## List all detection rules
	poetry run secret-scanner list-rules

build:  ## Build distribution packages
	poetry build

publish:  ## Publish to PyPI (requires credentials)
	poetry publish

dev:  ## Enter Poetry shell
	poetry shell

setup-hooks:  ## Install Git pre-commit hook
	cp hooks/pre-commit.sh .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✓ Pre-commit hook installed"

check-all: format-check lint test  ## Run all checks (format, lint, test)

ci: clean install check-all  ## Run full CI pipeline locally
