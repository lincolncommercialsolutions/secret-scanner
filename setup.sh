#!/bin/bash
# Quick setup script for the Secret Scanner project

set -e

echo "🚀 Setting up Secret Scanner project..."
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo ""
fi

echo "✓ Poetry is available"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
poetry install
echo ""

# Run validation
echo "🔍 Validating configuration..."
poetry run secret-scanner validate
echo ""

# Run tests
echo "🧪 Running tests..."
poetry run pytest -v
echo ""

# Show available commands
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  make help          - Show all make targets"
echo "  make test          - Run tests with coverage"
echo "  make run           - Scan current directory"
echo "  make setup-hooks   - Install Git pre-commit hook"
echo ""
echo "Or use directly:"
echo "  poetry run secret-scanner scan ."
echo "  poetry run secret-scanner --help"
echo ""
echo "Try scanning the example files:"
echo "  poetry run secret-scanner scan examples/"
echo ""
