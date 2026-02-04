#!/bin/bash
# Pre-commit hook for secret scanning
# Install: cp pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔍 Running secret scanner on staged files..."

# Check if secret-scanner is available
if ! command -v secret-scanner &> /dev/null; then
    echo "⚠️  secret-scanner not found. Install with: poetry install"
    echo "   Skipping secret scan..."
    exit 0
fi

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No staged files to scan"
    exit 0
fi

# Create temp directory for staged content
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy staged files to temp directory
for file in $STAGED_FILES; do
    mkdir -p "$TEMP_DIR/$(dirname "$file")"
    git show ":$file" > "$TEMP_DIR/$file" 2>/dev/null || true
done

# Run scanner on temp directory
if secret-scanner scan --format summary "$TEMP_DIR" 2>/dev/null; then
    echo "✅ No secrets detected"
    exit 0
else
    echo ""
    echo "❌ SECRETS DETECTED IN STAGED FILES!"
    echo "   Please remove secrets before committing."
    echo ""
    echo "   To see details, run: secret-scanner scan ."
    echo "   To bypass this check (NOT RECOMMENDED): git commit --no-verify"
    echo ""
    exit 1
fi
