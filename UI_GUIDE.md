# Web UI Guide

## Starting the Web UI

Launch the interactive web interface:

```bash
# Using CLI command
poetry run secret-scanner ui

# Or using make
make ui

# Or directly with streamlit
poetry run streamlit run src/secret_scanner/ui.py
```

The UI will automatically open in your default web browser at `http://localhost:8501`.

## Features

### 📂 Scan Tab

**Input Methods:**
- **Local Path**: Enter a file or directory path on your system
- **Upload Files**: Drag and drop files to scan

**Scan Modes:**
- **Files/Directory**: Scan current files
- **Git History**: Scan commit history (with configurable commit limit)

**Options:**
- Show entropy values in results
- Configure maximum commits for Git scanning

### 📊 Results Tab

**Summary Metrics:**
- Total findings count
- Number of affected files
- Unique rule types triggered
- Average entropy score

**Visualizations:**
- Bar chart: Findings by rule type
- Horizontal bar: Top 10 files with findings
- Histogram: Entropy distribution

**Detailed Table:**
- Interactive data table with all findings
- Filter by rule type or file
- Sort by any column
- Secret preview (truncated for security)

**Export Options:**
- **JSON**: Machine-readable format
- **CSV**: Spreadsheet compatible
- **Markdown**: Human-readable report

### ℹ️ About Tab

- Feature overview
- Detection categories
- Usage tips
- Version information
- Configuration statistics

## UI Configuration

### Sidebar Options

The left sidebar contains:
- **Configuration Status**: Number of rules loaded
- **Detection Rules**: Expandable list of rule categories
- **Warnings**: Configuration validation warnings
- **Scan Options**: Mode selection and settings

### Keyboard Shortcuts

- `Ctrl/Cmd + R`: Refresh page
- `Ctrl/Cmd + K`: Focus search (if available)
- `Ctrl/Cmd + C`: Stop the server

## Tips & Tricks

### Best Practices

1. **Start with Local Path**: Easier for testing
2. **Use Filters**: When dealing with many findings
3. **Export Results**: Save for documentation or compliance
4. **Git History**: Scan last 100-500 commits first, then expand

### Performance Tips

- For large repositories, use Git History with limited commits
- Upload only relevant files when using file upload
- Filter results to focus on specific rule types
- Use the summary view for quick overview

### Troubleshooting

**UI won't start:**
```bash
# Reinstall dependencies
poetry install

# Check if Streamlit is installed
poetry run streamlit --version
```

**Port already in use:**
```bash
# Streamlit uses port 8501 by default
# Kill existing process or change port:
poetry run streamlit run src/secret_scanner/ui.py --server.port 8502
```

**Browser doesn't open:**
- Manually navigate to: http://localhost:8501
- Check firewall settings
- Try incognito/private mode

## Screenshots & Demo

### Main Interface
The UI provides a clean, modern interface with three main tabs:
- Scan: Configure and execute scans
- Results: View findings with charts and tables
- About: Documentation and info

### Scan Configuration
- Choose between file/directory or Git history scanning
- Upload multiple files or specify local paths
- Configure scan depth and options

### Results Visualization
- Interactive charts showing findings by type and file
- Entropy distribution histogram
- Filterable data table
- One-click export in multiple formats

## Advanced Usage

### Custom Themes

Streamlit supports custom themes. Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

### Running in Production

For production deployment:

```bash
# Run with specific port and host
streamlit run src/secret_scanner/ui.py \
  --server.port 8080 \
  --server.address 0.0.0.0 \
  --server.headless true

# Or use Docker (create Dockerfile first)
docker build -t secret-scanner-ui .
docker run -p 8501:8501 secret-scanner-ui
```

### Environment Variables

```bash
# Disable usage stats
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Custom cache directory
export STREAMLIT_CACHE_DIR=/tmp/streamlit_cache
```

## Security Considerations

1. **Secrets Display**: Secret values are truncated in the UI
2. **Local Only**: By default, UI runs on localhost
3. **No Storage**: Scan results are not persisted
4. **Temp Files**: Uploaded files are stored in temp directory and deleted after scan
5. **Export Control**: Be careful when exporting results with sensitive data

## Comparison: UI vs CLI

| Feature | Web UI | CLI |
|---------|--------|-----|
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Visualizations | ⭐⭐⭐⭐⭐ | ⭐ |
| Export Options | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Automation | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| CI/CD Integration | ❌ | ✅ |
| File Upload | ✅ | ❌ |
| Interactive Filtering | ✅ | ❌ |
| Best For | Manual analysis | Automation, CI/CD |

## Next Steps

After scanning:
1. Review findings in the Results tab
2. Use filters to focus on specific issues
3. Export results for reporting
4. Fix identified secrets
5. Re-scan to verify

For automated scanning, use the CLI commands in your CI/CD pipeline.
