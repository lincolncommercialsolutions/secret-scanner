# Development Guide

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd git-fih
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Activate virtual environment:
```bash
poetry shell
```

## Running Tests

Run all tests:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov=secret_scanner --cov-report=html
```

Run specific test file:
```bash
poetry run pytest tests/test_scanner.py
```

## Code Quality

Format code with Black:
```bash
poetry run black src/ tests/
```

Lint with Ruff:
```bash
poetry run ruff check src/ tests/
```

Fix auto-fixable issues:
```bash
poetry run ruff check --fix src/ tests/
```

## Running the Tool

After installation, you can run:

```bash
# Using poetry
poetry run secret-scanner scan .

# Or if installed globally
secret-scanner scan .
```

## Project Structure

```
git-fih/
├── src/
│   └── secret_scanner/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── config.py           # Configuration loader
│       ├── scanner.py          # Core scanning logic
│       ├── detectors/
│       │   ├── __init__.py
│       │   └── entropy.py      # Entropy calculations
│       └── reporters/
│           ├── __init__.py
│           └── reporter.py     # Output formatters
├── config/
│   └── default_rules.yaml      # Detection rules
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_entropy.py
│   └── test_scanner.py
├── pyproject.toml              # Project configuration
└── README.md
```

## Adding New Rules

Edit `config/default_rules.yaml`:

```yaml
rules:
  - id: my-custom-rule
    description: My Custom Secret Pattern
    regex: pattern-here
    entropy: 3.5  # optional
    keywords: [key, token]  # optional
    tags: [custom]  # optional
```

## Git Hooks

Install pre-commit hook:
```bash
cp hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## CI/CD Integration

### GitHub Actions

The repository includes a CI workflow at `.github/workflows/ci.yml` that:
- Runs tests on multiple Python versions
- Checks code formatting and linting
- Scans for secrets and uploads results

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
secret-scan:
  stage: test
  image: python:3.11
  before_script:
    - pip install poetry
    - poetry install
  script:
    - poetry run secret-scanner scan --format json .
  allow_failure: false
```

## Release Process

1. Update version in `pyproject.toml` and `src/secret_scanner/__init__.py`
2. Run tests: `poetry run pytest`
3. Build: `poetry build`
4. Publish: `poetry publish` (requires PyPI credentials)

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and linters
4. Submit pull request

## Performance Tips

- Use `--max-commits` to limit Git history scanning
- Add exclusions for large generated files
- Use `--format summary` for faster output
- Optimize regex patterns for performance

## Debugging

Enable verbose mode:
```bash
secret-scanner scan --verbose .
```

Test specific rules:
```bash
secret-scanner list-rules
secret-scanner validate --rules config/default_rules.yaml
```
