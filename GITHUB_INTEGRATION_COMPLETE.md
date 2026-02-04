# 🎉 Secret Scanner with GitHub Integration - Complete!

## ✅ What's Been Added

### 🐙 GitHub Repository Scanning
Your Secret Scanner now has powerful GitHub integration capabilities!

## 🚀 How to Access

### Web UI is Running!
```
Local URL:   http://localhost:8502
Network URL: http://192.168.1.143:8502
```

**Open in your browser to access the full UI with:**
- 📂 **Scan Local** - Files and directories
- 🐙 **Scan GitHub** - Public repositories  
- 📊 **Results** - Interactive visualizations
- ℹ️ **About** - Documentation

## 🐙 GitHub Features

### 1. Scan Single Repository
```bash
# CLI
secret-scanner scan-github torvalds/linux
secret-scanner scan-github owner/repo --token YOUR_TOKEN

# Web UI
Go to "Scan GitHub" tab → "Single Repository"
Enter: owner/repo or full URL
```

### 2. Scan User Repositories
```bash
# Web UI (easiest)
Mode: "User Repositories"
Username: octocat
Max Repos: 5
```

Scans multiple public repos from a GitHub user.

### 3. Scan Organization
```bash
# Web UI
Mode: "Organization Repositories"
Org Name: github
Max Repos: 5
```

### 4. Search & Scan
```bash
# Web UI
Mode: "Search Repositories"
Query: language:python stars:>1000
Max Repos: 3
```

**Search Query Examples:**
- `language:python stars:>1000`
- `topic:web language:javascript`
- `user:octocat language:python`
- `org:github topic:security`

## 📦 New Files Created

1. **src/secret_scanner/github_scanner.py** - GitHub integration module
2. **GITHUB_SCANNING.md** - Complete GitHub scanning guide
3. Updated **src/secret_scanner/ui.py** - New "Scan GitHub" tab
4. Updated **src/secret_scanner/cli.py** - New `scan-github` command
5. Updated **README.md** - GitHub features documented

## 🎯 Quick Examples

### Try These Safe Public Repos

```bash
# Example repositories you can scan right now:

# 1. Python's official CPython
secret-scanner scan-github python/cpython

# 2. Django web framework
secret-scanner scan-github django/django

# 3. Linux kernel
secret-scanner scan-github torvalds/linux

# 4. GitHub's own repos
# In Web UI: Organization mode → "github"
```

## ⚡ Features

### Automatic Handling
- ✅ Clones repo to temp directory
- ✅ Scans with all configured rules
- ✅ Optional Git history scanning
- ✅ Shows repo metadata (stars, language)
- ✅ Aggregates findings across repos
- ✅ Auto-cleanup of temp files
- ✅ Rate limiting protection

### Security
- 🔒 Read-only access
- 🔒 Temp files auto-deleted
- 🔒 Secrets truncated in output
- 🔒 Token stored in memory only
- 🔒 No data persisted

## 🔑 GitHub Token (Optional but Recommended)

### Why Use a Token?
- **Without**: 60 requests/hour
- **With**: 5,000 requests/hour

### How to Get One
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. **No scopes needed** for public repos!
4. Copy the token

### How to Use
```bash
# Command line
secret-scanner scan-github owner/repo --token YOUR_TOKEN

# Environment variable
export GITHUB_TOKEN=YOUR_TOKEN
secret-scanner scan-github owner/repo

# Web UI
Go to Settings → Enter token in "GitHub Personal Access Token" field
```

## 📊 Rate Limits Displayed in UI

The Web UI shows your current rate limit:
- **API Requests Remaining**
- **Search Requests Remaining**
- **Reset Time**

## 🎨 Web UI New Features

### "Scan GitHub" Tab Includes:

1. **Settings Panel**
   - Optional GitHub token input
   - Real-time rate limit display

2. **Scan Modes** (4 options)
   - Single Repository
   - User Repositories
   - Organization Repositories
   - Search Repositories

3. **Results Display**
   - Repository metadata (stars, language)
   - Total findings count
   - Aggregated results from multiple repos
   - All existing visualization features

## 💡 Usage Tips

### Start Small
```bash
# Good first scan (small repo)
secret-scanner scan-github octocat/hello-world

# Then try larger ones
secret-scanner scan-github django/django
```

### Use Filters
- Enable "Show Entropy Values" for analysis
- Filter by rule type or file
- Export results as JSON/CSV/Markdown

### Performance
- **Single repo**: ~10-30 seconds
- **Multiple repos**: ~1-2 min per repo
- **With history**: 2-5x longer
- Tool automatically adds delays for rate limiting

## 🚀 Commands Available

```bash
# Local scanning (existing)
secret-scanner scan .
secret-scanner scan --git-history .

# GitHub scanning (NEW!)
secret-scanner scan-github owner/repo
secret-scanner scan-github owner/repo --git-history
secret-scanner scan-github owner/repo --token TOKEN --format json

# Web UI (with GitHub tab)
secret-scanner ui
make ui

# Other commands
secret-scanner validate
secret-scanner list-rules
secret-scanner generate-hook
```

## 📚 Documentation

All guides available:
- **README.md** - Main documentation
- **GITHUB_SCANNING.md** - Complete GitHub guide (NEW!)
- **UI_GUIDE.md** - Web UI documentation
- **QUICKSTART.md** - Getting started
- **EXAMPLES.md** - Usage examples
- **DEVELOPMENT.md** - Developer guide

## ✨ Example Workflow

### 1. Start UI
```bash
# Already running at http://localhost:8502
# Or restart: python3 -m streamlit run src/secret_scanner/ui.py --server.port=8502
```

### 2. Try GitHub Scan
1. Open http://localhost:8502
2. Click "🐙 Scan GitHub" tab
3. Select "Single Repository"
4. Enter: `octocat/hello-world`
5. Click "🔍 Scan Repository"
6. View results in "📊 Results" tab

### 3. Try User Scan
1. Mode: "User Repositories"
2. Username: `torvalds`
3. Max Repos: 3
4. Click "🔍 Scan User Repos"

### 4. Export Results
1. Go to Results tab
2. Use filters if needed
3. Click "📥 Download JSON" or CSV or Markdown

## 🎓 Real-World Use Cases

### Security Audit
```bash
# Audit your organization's public repos
# Web UI → Organization mode → your-org-name
```

### Research
```bash
# Find common secrets in popular Python projects
# Web UI → Search mode → "language:python stars:>5000"
```

### Compliance
```bash
# Regular scans of dependencies
secret-scanner scan-github dependency-org/critical-lib --format sarif
```

## 🔒 Responsible Use

⚠️ **Important:**
- Only scan public repositories (or your own private ones)
- Report findings responsibly
- Respect rate limits
- Use for security improvement, not malicious purposes
- Credit repository owners when reporting

## 🆘 Troubleshooting

### "Repository not found"
- Ensure repo is public
- Check format: `owner/repo`

### "Rate limit exceeded"
- Add GitHub token
- Wait for reset (shown in UI)

### UI not loading
- Try http://localhost:8502
- Or restart: `pkill -f streamlit && make ui`

## 🎉 Summary

You now have a **complete secret scanner** with:
- ✅ Local file/directory scanning
- ✅ Git history scanning
- ✅ **GitHub repository scanning** (NEW!)
- ✅ Web UI with 4 tabs
- ✅ CLI commands
- ✅ Multiple output formats
- ✅ 30+ detection rules
- ✅ Comprehensive documentation

**The UI is running at: http://localhost:8502**

**Try it now!** 🚀
