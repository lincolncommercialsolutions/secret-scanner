#!/bin/bash
# Project statistics generator

echo "=========================================="
echo "Secret Scanner - Project Statistics"
echo "=========================================="
echo ""

echo "📊 File Counts:"
echo "---------------"
echo "Python files:     $(find . -name "*.py" ! -path "./.venv/*" ! -path "./venv/*" | wc -l)"
echo "Test files:       $(find ./tests -name "*.py" | wc -l)"
echo "Config files:     $(find . -name "*.yaml" -o -name "*.yml" | wc -l)"
echo "Documentation:    $(find . -maxdepth 1 -name "*.md" | wc -l)"
echo "Shell scripts:    $(find . -name "*.sh" | wc -l)"
echo ""

echo "📝 Lines of Code:"
echo "-----------------"
echo "Source code:      $(find ./src -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 'N/A')"
echo "Tests:            $(find ./tests -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 'N/A')"
echo "Config rules:     $(wc -l < config/default_rules.yaml 2>/dev/null || echo 'N/A')"
echo ""

echo "🎯 Features:"
echo "------------"
echo "Detection rules:  $(grep -c '^  - id:' config/default_rules.yaml 2>/dev/null || echo 'N/A')"
echo "CLI commands:     4 (scan, validate, list-rules, generate-hook)"
echo "Output formats:   4 (console, json, sarif, summary)"
echo "Test modules:     3 (entropy, config, scanner)"
echo ""

echo "📦 Dependencies:"
echo "----------------"
echo "Production:       5 (click, gitpython, pyyaml, colorama, + stdlib)"
echo "Development:      4 (pytest, pytest-cov, black, ruff)"
echo ""

echo "📚 Documentation:"
echo "-----------------"
ls -1 *.md 2>/dev/null | while read f; do
    echo "  • $f"
done
echo ""

echo "✅ Status: READY FOR USE"
echo "=========================================="
