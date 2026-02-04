# Quick Start Guide

## Installation

### Option 1: Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd git-fih

# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manually:
poetry install
```

### Option 2: Using pip

```bash
# From source
pip install -e .

# Or after building
poetry build
pip install dist/secret_scanner-*.whl
```

## Quick Test

Scan the example files to see the tool in action:

```bash
# This will find secrets
poetry run secret-scanner scan examples/test_secrets.py

# This should be clean
poetry run secret-scanner scan examples/safe_config.py
```

## Basic Usage

```bash
# Scan current directory
poetry run secret-scanner scan .

# Scan with verbose output
poetry run secret-scanner scan --verbose .

# Scan Git history
poetry run secret-scanner scan --git-history .

# Output as JSON
poetry run secret-scanner scan --format json . > results.json
```

## Using Make Commands

The project includes a Makefile for convenience:

```bash
# See all available commands
make help

# Install dependencies
make install

# Run tests
make test

# Scan current directory
make run

# Validate rules
make validate

# Install Git hook
make setup-hooks
```

## Verify Installation

```bash
# Check version
poetry run secret-scanner --version

# Validate rules
poetry run secret-scanner validate

# List available rules
poetry run secret-scanner list-rules
```

## Next Steps

1. **Customize Rules**: Edit `config/default_rules.yaml` to add your own patterns
2. **Set up Git Hook**: Run `make setup-hooks` to prevent committing secrets
3. **Integrate with CI/CD**: See `EXAMPLES.md` for CI/CD integration examples
4. **Read Documentation**: Check `DEVELOPMENT.md` for development guidelines

## Troubleshooting

### Poetry not found
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Python version too old
The tool requires Python 3.10 or later. Update your Python installation.

### GitPython issues
```bash
poetry run pip install --upgrade gitpython
```

### Permission denied for setup.sh
```bash
chmod +x setup.sh
```

## Testing the Scanner

Try scanning the example files:

```bash
# Should find multiple secrets
poetry run secret-scanner scan examples/test_secrets.py

# Should be clean (uses environment variables)
poetry run secret-scanner scan examples/safe_config.py
```

Expected output for test_secrets.py:
- AWS Access Key ID
- AWS Secret Access Key
- GitHub Token
- Database Connection String
- API Keys (Stripe, Google)
- JWT Token
- Password assignments
- Private Key

## Common Commands

```bash
# Development
poetry shell              # Activate virtual environment
make test                # Run all tests
make lint                # Check code style
make format              # Auto-format code

# Scanning
make run                 # Scan current directory
make run-verbose         # Verbose output
make run-git             # Scan Git history

# Configuration
make validate            # Validate rules
make list-rules          # Show all rules
```

## Getting Help

```bash
# CLI help
poetry run secret-scanner --help
poetry run secret-scanner scan --help

# Or
make help
```
