# Example Usage

## Basic Scanning

### Scan current directory
```bash
secret-scanner scan .
```

### Scan specific files
```bash
secret-scanner scan app.py config.json
```

### Scan with custom rules
```bash
secret-scanner scan --rules my_rules.yaml /path/to/project
```

## Git History Scanning

### Scan all commits
```bash
secret-scanner scan --git-history .
```

### Scan last 100 commits
```bash
secret-scanner scan --git-history --max-commits 100 .
```

## Output Formats

### Console output (default, colorized)
```bash
secret-scanner scan .
```

### JSON output
```bash
secret-scanner scan --format json . > results.json
```

### SARIF output (for CI/CD)
```bash
secret-scanner scan --format sarif . > results.sarif
```

### Summary output (brief)
```bash
secret-scanner scan --format summary .
```

## Validation and Configuration

### Validate rules file
```bash
secret-scanner validate
secret-scanner validate --rules custom_rules.yaml
```

### List all rules
```bash
secret-scanner list-rules
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Scan for secrets
  run: |
    pip install poetry
    poetry install
    poetry run secret-scanner scan --format sarif . > results.sarif

- name: Upload results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### GitLab CI
```yaml
secret-scan:
  script:
    - pip install secret-scanner
    - secret-scanner scan --format json .
  allow_failure: false
```

### Jenkins
```groovy
stage('Secret Scan') {
    steps {
        sh 'secret-scanner scan --format json . > results.json'
        archiveArtifacts artifacts: 'results.json'
    }
}
```

## Git Hooks

### Generate pre-commit hook
```bash
secret-scanner generate-hook > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Manual hook installation
```bash
cp hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Advanced Options

### Verbose output
```bash
secret-scanner scan --verbose .
```

### Don't exit with error code
```bash
secret-scanner scan --no-exit-code .
```

### Multiple targets
```bash
secret-scanner scan src/ tests/ docs/
```

## Example Findings

When secrets are found, output looks like:

```
======================================================================
  SECRETS DETECTED: 3 finding(s)
======================================================================

📁 src/config.py
   2 finding(s)

  🔑 [aws-access-key-id] AWS Access Key ID
     Line: 45
     Entropy: 3.42
     Secret: AKIAIOSFODNN7EXAMPLE

  🔑 [generic-password] Generic password / secret assignment
     Line: 67
     Entropy: 4.15
     Secret: password = "super_secret_123"

📁 .env
   1 finding(s)

  🔑 [database-url] Database Connection String
     Line: 12
     Entropy: 3.78
     Secret: postgres://user:pass@localhost/db

======================================================================
  TOTAL: 3 secret(s) found across 2 file(s)
======================================================================

⚠  Action required: Review and remove these secrets!
```

## Custom Rules Example

Create `custom_rules.yaml`:

```yaml
rules:
  - id: internal-api-key
    description: Internal API Key Pattern
    regex: "INTERNAL_KEY_[A-Za-z0-9]{32}"
    entropy: 4.0
    tags: [internal, api]

  - id: employee-id
    description: Employee ID Pattern
    regex: "EMP[0-9]{6}"
    entropy: null
    keywords: [employee, emp]

exclusions:
  - "test/"
  - "mock/"
  - "\\.lock$"
```

Use it:
```bash
secret-scanner scan --rules custom_rules.yaml .
```
