# Secret Scanner - Project Index

Welcome to the Secret Scanner project! This index will help you navigate the codebase.

## 📖 Start Here

New to the project? Read these in order:

1. **[README.md](README.md)** - Project overview and basic usage
2. **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
3. **[EXAMPLES.md](EXAMPLES.md)** - Real-world usage examples
4. **[BUILD_REPORT.md](BUILD_REPORT.md)** - What was built and why

## 🗂️ Documentation

| File | Description |
|------|-------------|
| [README.md](README.md) | Main documentation and overview |
| [QUICKSTART.md](QUICKSTART.md) | Quick setup and installation guide |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development workflow and contributing guide |
| [EXAMPLES.md](EXAMPLES.md) | Usage examples and CI/CD integration |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Comprehensive project overview |
| [BUILD_REPORT.md](BUILD_REPORT.md) | Complete build report and features |
| [LICENSE](LICENSE) | MIT License |

## 💻 Source Code

### Main Application (`src/secret_scanner/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `__init__.py` | Package initialization | Version info |
| `cli.py` | Command-line interface | `main()`, `scan()`, `validate()` |
| `config.py` | Configuration loader | `load_rules()`, `validate_config()` |
| `scanner.py` | Core scanning engine | `scan_file()`, `scan_directory()`, `scan_git_history()` |

### Detectors (`src/secret_scanner/detectors/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `entropy.py` | Shannon entropy calculation | `shannon_entropy()`, `is_base64()`, `is_hex()` |

### Reporters (`src/secret_scanner/reporters/`)

| File | Purpose | Output Formats |
|------|---------|----------------|
| `reporter.py` | Output formatting | Console, JSON, SARIF, Summary |

## 🧪 Tests (`tests/`)

| File | Tests For | Coverage |
|------|-----------|----------|
| `test_entropy.py` | Entropy calculations | Shannon entropy, base64, hex detection |
| `test_config.py` | Configuration loading | YAML parsing, validation |
| `test_scanner.py` | Scanner logic | File scanning, path filtering |
| `conftest.py` | Test configuration | Pytest setup |

## ⚙️ Configuration

| File | Purpose |
|------|---------|
| `config/default_rules.yaml` | 30+ detection rules for secrets |
| `pyproject.toml` | Poetry package configuration |
| `.gitignore` | Git ignore patterns |

## 🛠️ Automation & CI/CD

| File | Purpose |
|------|---------|
| `Makefile` | Convenience commands (test, lint, format, run) |
| `setup.sh` | Automated project setup script |
| `.github/workflows/ci.yml` | GitHub Actions CI/CD pipeline |
| `hooks/pre-commit.sh` | Git pre-commit hook for secret scanning |

## 📝 Examples

| File | Purpose |
|------|---------|
| `examples/test_secrets.py` | File with intentional test secrets |
| `examples/safe_config.py` | Best practices example (no secrets) |

## 🚀 Quick Commands

```bash
# Setup
./setup.sh                          # Automated setup
make install                        # Install dependencies

# Usage
make run                            # Scan current directory
poetry run secret-scanner scan .   # Direct command
make run-verbose                    # Verbose output

# Testing
make test                           # Run tests with coverage
make lint                           # Lint code
make format                         # Format code

# Configuration
make validate                       # Validate rules
make list-rules                     # List all rules
make setup-hooks                    # Install Git hook

# Development
make help                           # Show all commands
poetry shell                        # Activate environment
```

## 🎯 Common Tasks

### Adding a New Detection Rule

1. Edit `config/default_rules.yaml`
2. Add rule with id, description, regex, and optional entropy
3. Run `make validate` to check syntax
4. Test with `make run`

### Running Tests

```bash
make test                    # All tests with coverage
poetry run pytest -v         # Verbose test output
poetry run pytest tests/test_scanner.py  # Specific test file
```

### Customizing Output

See `src/secret_scanner/reporters/reporter.py` for output formatters:
- `ConsoleReporter` - Colorized terminal output
- `JSONReporter` - Machine-readable JSON
- `SARIFReporter` - GitHub Security compatible
- `SummaryReporter` - Brief overview

### Integrating with CI/CD

Examples in [EXAMPLES.md](EXAMPLES.md):
- GitHub Actions
- GitLab CI
- Jenkins

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                    CLI (cli.py)                 │
│         scan | validate | list-rules            │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Config Loader (config.py)          │
│          Loads rules from YAML files            │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Scanner (scanner.py)               │
│    scan_file | scan_directory | scan_git       │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Entropy    │ │  Regex   │ │   Finding    │
│  Detector    │ │ Matching │ │   Dataclass  │
└──────────────┘ └──────────┘ └──────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            Reporter (reporter.py)               │
│   Console | JSON | SARIF | Summary             │
└─────────────────────────────────────────────────┘
```

## 📊 Key Metrics

- **Lines of Code**: ~2,000
- **Test Coverage**: Targeting >80%
- **Detection Rules**: 30+
- **Output Formats**: 4
- **CLI Commands**: 4
- **Dependencies**: 5 core + dev tools

## 🔗 Related Files

### Original Requirements
- `info.txt` - Detailed specification
- `instructions.txt` - Step-by-step instructions
- `overview.txt` - Development plan

### Generated Documentation
- All markdown files in root directory

## 📚 Learning Resources

To understand the codebase:

1. **Entropy Detection**: Read `src/secret_scanner/detectors/entropy.py`
2. **Pattern Matching**: Study `config/default_rules.yaml`
3. **Git Integration**: Check `scanner.py` → `scan_git_history()`
4. **CLI Framework**: Explore `cli.py` using Click
5. **Output Formats**: Review `reporters/reporter.py`

## 🎓 Code Conventions

- **Formatting**: Black (100 char line length)
- **Linting**: Ruff
- **Type Hints**: Used throughout
- **Docstrings**: Google style
- **Testing**: Pytest with fixtures

## 🔍 Finding Things

### Search by Feature
- **Entropy calculation**: `src/secret_scanner/detectors/entropy.py`
- **Rule validation**: `src/secret_scanner/config.py`
- **Git scanning**: `src/secret_scanner/scanner.py` → `scan_git_history()`
- **Console output**: `src/secret_scanner/reporters/reporter.py` → `ConsoleReporter`
- **CLI commands**: `src/secret_scanner/cli.py`

### Search by Test
- **Entropy tests**: `tests/test_entropy.py`
- **Config tests**: `tests/test_config.py`
- **Scanner tests**: `tests/test_scanner.py`

## 💡 Tips

- Use `make help` to see all available commands
- Run `poetry run secret-scanner --help` for CLI help
- Check `examples/` for test files
- Use `--verbose` flag for debugging
- Validate rules with `make validate`

---

**Last Updated**: February 3, 2026  
**Version**: 0.1.0  
**Status**: Production Ready ✅
