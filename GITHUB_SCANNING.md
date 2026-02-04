# GitHub Scanning Guide

## Overview

The Secret Scanner now includes powerful GitHub integration to scan public repositories for exposed secrets. This feature allows you to:

- Scan individual GitHub repositories
- Scan all repositories from a user
- Scan all repositories from an organization  
- Search and scan repositories by criteria

## Quick Start

### Web UI (Easiest)

1. Start the UI:
```bash
make ui
# or
python3 -m streamlit run src/secret_scanner/ui.py --server.port=8502
```

2. Go to the "🐙 Scan GitHub" tab
3. Choose your scan mode
4. Enter repository/user/org name
5. Click "🔍 Scan"

### Command Line

```bash
# Scan a single repository
secret-scanner scan-github owner/repo

# With GitHub token for higher rate limits
secret-scanner scan-github owner/repo --token YOUR_TOKEN

# Or use environment variable
export GITHUB_TOKEN=your_token
secret-scanner scan-github owner/repo

# Scan Git history
secret-scanner scan-github owner/repo --git-history

# Output as JSON
secret-scanner scan-github owner/repo --format json > results.json
```

## GitHub API Rate Limits

### Without Token (Anonymous)
- 60 requests per hour
- Search: 10 requests per minute

### With Personal Access Token
- 5,000 requests per hour
- Search: 30 requests per minute

### Creating a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "Secret Scanner")
4. Select scopes: **No scopes needed for public repos!**
5. Click "Generate token"
6. Copy and save the token

## Scan Modes

### 1. Single Repository

Scan one specific repository:

**Web UI:**
- Tab: "Scan GitHub"
- Mode: "Single Repository"
- Enter: `owner/repo` or full URL
- Optional: Enable "Scan Git History"

**CLI:**
```bash
secret-scanner scan-github torvalds/linux
secret-scanner scan-github https://github.com/python/cpython
```

### 2. User Repositories

Scan multiple repositories from a GitHub user:

**Web UI:**
- Tab: "Scan GitHub"
- Mode: "User Repositories"  
- Enter username
- Set max repositories (1-20)

**Example Users to Try:**
- `octocat` - GitHub's mascot account
- `torvalds` - Linus Torvalds
- `gvanrossum` - Python creator

### 3. Organization Repositories

Scan repositories from an organization:

**Web UI:**
- Tab: "Scan GitHub"
- Mode: "Organization Repositories"
- Enter organization name
- Set max repositories

**Example Organizations:**
- `github` - GitHub's own repos
- `microsoft` - Microsoft
- `google` - Google
- `netflix` - Netflix

### 4. Search Repositories

Search GitHub and scan matching repositories:

**Web UI:**
- Tab: "Scan GitHub"
- Mode: "Search Repositories"
- Enter search query
- Set max repositories

**Example Search Queries:**
```
language:python stars:>1000
topic:web language:javascript
user:octocat language:python
org:github topic:security
created:>2024-01-01 language:go
```

## Features

### Automatic Features
- ✅ Clones repository to temporary directory
- ✅ Scans all files with configured rules
- ✅ Optionally scans Git history
- ✅ Aggregates findings across multiple repos
- ✅ Shows repository metadata (stars, language)
- ✅ Respects rate limits with delays
- ✅ Cleans up temporary files automatically

### Security
- 🔒 Repositories cloned to temp directory
- 🔒 Temp files deleted after scan
- 🔒 Secrets truncated in output
- 🔒 GitHub token stored in memory only
- 🔒 No data persisted

## Usage Examples

### Scan Popular Python Projects

```bash
# Django
secret-scanner scan-github django/django

# Flask
secret-scanner scan-github pallets/flask

# FastAPI
secret-scanner scan-github tiangolo/fastapi
```

### Scan Security Tools

```bash
# TruffleHog
secret-scanner scan-github trufflesecurity/trufflehog

# GitLeaks
secret-scanner scan-github gitleaks/gitleaks

# Semgrep
secret-scanner scan-github returntocorp/semgrep
```

### Scan Your Own Repos

```bash
# Replace 'yourusername' with your GitHub username
secret-scanner scan-github yourusername/your-repo

# Scan all your public repos (via Web UI)
# Mode: "User Repositories"
# Username: yourusername
```

## Best Practices

### Rate Limiting
1. Use a GitHub token for higher limits
2. Start with small batches (3-5 repos)
3. The tool automatically adds delays between requests
4. Monitor rate limit in Web UI settings

### Performance
1. **Single Repo**: ~10-30 seconds
2. **Multiple Repos**: ~1-2 minutes per repo
3. **With Git History**: 2-5x longer
4. **Large Repos**: May timeout (>500MB)

### Optimization Tips
- Disable Git history for faster scans
- Limit number of repos (especially for orgs)
- Use specific search queries
- Scan smaller/focused repositories first

## Troubleshooting

### "Repository not found"
- Check repository name format: `owner/repo`
- Ensure repository is public
- Verify repository exists

### "Rate limit exceeded"
- Add GitHub token
- Wait for rate limit reset
- Check current limits in Web UI

### "Git clone error"
- Repository may be too large
- Network connectivity issues
- Try again later

### "Permission denied"
- Repository is private (token has no access)
- Organization blocks anonymous access
- Use personal access token

## Output Formats

### Console (Default)
Colorized output with findings grouped by file

### JSON
```bash
secret-scanner scan-github owner/repo --format json > results.json
```

### SARIF (for CI/CD)
```bash
secret-scanner scan-github owner/repo --format sarif > results.sarif
```

### Summary
```bash
secret-scanner scan-github owner/repo --format summary
```

## Integration Examples

### CI/CD - GitHub Actions

```yaml
name: Scan Dependencies for Secrets

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  scan-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Secret Scanner
        run: pip install -e .
      
      - name: Scan Dependencies
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          secret-scanner scan-github dependency-org/dependency-repo --format sarif > results.sarif
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

### Scheduled Audits

Create a script to regularly scan important repos:

```bash
#!/bin/bash
# scan_audit.sh

REPOS=(
  "org1/repo1"
  "org2/repo2"
  "org3/repo3"
)

for repo in "${REPOS[@]}"; do
  echo "Scanning $repo..."
  secret-scanner scan-github "$repo" --format json > "results_${repo//\//_}.json"
  sleep 5  # Rate limiting
done

echo "Audit complete!"
```

## Advanced Features

### Environment Variables

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Disable Streamlit browser auto-open
export STREAMLIT_SERVER_HEADLESS=true

# Custom config
export SECRET_SCANNER_CONFIG=custom_rules.yaml
```

### Programmatic Use

```python
from secret_scanner.config import load_rules
from secret_scanner.github_scanner import GitHubScanner

# Load config
config = load_rules()

# Create scanner
gh_scanner = GitHubScanner(config, github_token="your_token")

# Scan single repo
result = gh_scanner.scan_repository("owner/repo")
print(f"Found {result['total_findings']} secrets")

# Scan user repos
results = gh_scanner.scan_user_repositories("username", max_repos=5)

# Search and scan
results = gh_scanner.search_and_scan("language:python stars:>100", max_repos=3)
```

## Privacy & Ethics

⚠️ **Important Guidelines:**

1. **Public Repositories Only**: This tool only scans public repositories
2. **Responsible Disclosure**: If you find secrets, report them responsibly
3. **Respect Rate Limits**: Don't abuse GitHub's API
4. **No Malicious Use**: Use for security research and prevention only
5. **Attribution**: Credit repository owners when reporting findings

## FAQ

**Q: Can I scan private repositories?**  
A: Yes, but you need a GitHub token with appropriate permissions. The repository must be accessible to the token owner.

**Q: How long does scanning take?**  
A: Typically 10-30 seconds per repository, longer for large repos or with Git history enabled.

**Q: Is this legal?**  
A: Yes! Scanning public repositories for security research is legal and encouraged. However, always use findings responsibly.

**Q: What happens to cloned repositories?**  
A: They're automatically deleted after scanning. Nothing is persisted.

**Q: Can I scan my own private repos?**  
A: Yes, provide a GitHub token with repo access permissions.

**Q: Does this notify repository owners?**  
A: No, scanning is read-only and doesn't trigger notifications.

## Next Steps

1. **Try Examples**: Start with the example repos above
2. **Get a Token**: Create a GitHub token for higher rate limits
3. **Scan Your Repos**: Audit your own public repositories
4. **Report Findings**: Responsibly disclose any secrets found
5. **Integrate**: Add to your security workflow

For more help, see:
- [Main Documentation](README.md)
- [Web UI Guide](UI_GUIDE.md)
- [Examples](EXAMPLES.md)
