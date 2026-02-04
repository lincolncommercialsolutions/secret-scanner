# Secret Scanner

A production-grade CLI tool for detecting secrets and sensitive information in Git repositories and files.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Key Features

- 🔍 **30+ Detection Rules** - AWS keys, GitHub tokens, API keys, database credentials, private keys, and more
- 🎲 **Shannon Entropy Analysis** - Detect high-entropy strings that look like secrets
- 📜 **Git History Scanning** - Find secrets introduced in past commits
- 🐙 **GitHub Integration** - Scan public repositories, users, organizations, or search results
- 🎨 **Multiple Output Formats** - Console (colorized), JSON, SARIF, Summary
- 🖥️ **Web UI** - Beautiful Streamlit interface for interactive scanning
- ⚙️ **Configurable Rules** - YAML-based configuration for easy customization
- 🚫 **Smart Filtering** - False positive reduction with entropy thresholds and path exclusions
- 🔌 **CI/CD Ready** - Git hooks, GitHub Actions, GitLab CI integration examples

## Installation

```bash
# Install dependencies using Poetry
poetry install

# Or using pip
pip install -e .
```

## Usage

### Web UI (Recommended)
```bash
# Launch interactive web interface
secret-scanner ui

# Or using make
make ui
```

### Command Line

#### Scan a directory
```bash
secret-scanner scan /path/to/project
```

#### Scan Git history
```bash
secret-scanner scan --git-history /path/to/repo
```

#### Scan GitHub repository
```bash
secret-scanner scan-github owner/repo
secret-scanner scan-github owner/repo --token YOUR_GITHUB_TOKEN
```

#### Scan specific files
```bash
secret-scanner scan file1.py file2.js
```

#### Custom rules file
```bash
secret-scanner scan --rules custom_rules.yaml /path/to/project
```

## 🐙 GitHub Scanning

Scan public GitHub repositories directly:

```bash
# Single repository
secret-scanner scan-github torvalds/linux

# With GitHub token (higher rate limits)
export GITHUB_TOKEN=your_token
secret-scanner scan-github django/django --git-history

# Via Web UI
secret-scanner ui
# Then go to "Scan GitHub" tab
```

Features:
- Scan individual repositories
- Scan all repos from a user/organization
- Search and scan by criteria
- View repository metadata (stars, language)
- Aggregate findings across multiple repos

See [GitHub Scanning Guide](GITHUB_SCANNING.md) for details.

## Configuration

Rules are defined in YAML format. See `config/default_rules.yaml` for examples.

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black src/

# Lint
poetry run ruff check src/
```

## License

MIT
