"""Streamlit-based web UI for Secret Scanner."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import tempfile
import json
from typing import List, Dict
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from secret_scanner.config import load_rules, validate_config
from secret_scanner.scanner import Scanner, Finding
from secret_scanner.github_scanner import GitHubScanner


# Page configuration
st.set_page_config(
    page_title="Secret Scanner",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'github_token' not in st.session_state:
        st.session_state.github_token = None


def load_default_config():
    """Load default configuration."""
    try:
        config = load_rules()
        st.session_state.config = config
        return config
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return None


def render_sidebar():
    """Render sidebar with configuration options."""
    st.sidebar.title("Configuration")
    
    # Load config
    if st.session_state.config is None:
        load_default_config()
    
    config = st.session_state.config
    
    if config:
        st.sidebar.success(f"{len(config.rules)} rules loaded")
        
        # Show rule categories
        with st.sidebar.expander("Detection Rules", expanded=False):
            rule_tags = {}
            for rule in config.rules:
                tags = rule.get('tags', ['other'])
                for tag in tags:
                    if tag not in rule_tags:
                        rule_tags[tag] = 0
                    rule_tags[tag] += 1
            
            for tag, count in sorted(rule_tags.items()):
                st.write(f"• {tag}: {count} rules")
        
        # Configuration warnings
        warnings = validate_config(config)
        if warnings:
            with st.sidebar.expander("Warnings", expanded=False):
                for warning in warnings:
                    st.warning(warning)
    
    st.sidebar.divider()
    
    # Scan options
    st.sidebar.subheader("Scan Options")
    
    scan_mode = st.sidebar.radio(
        "Scan Mode",
        ["Files/Directory", "Git History"],
        help="Choose what to scan"
    )
    
    if scan_mode == "Git History":
        max_commits = st.sidebar.number_input(
            "Max Commits",
            min_value=1,
            max_value=10000,
            value=100,
            help="Maximum number of commits to scan"
        )
    else:
        max_commits = None
    
    show_entropy = st.sidebar.checkbox(
        "Show Entropy Values",
        value=True,
        help="Display entropy calculations"
    )
    
    return scan_mode, max_commits, show_entropy


def scan_path(path: str, git_history: bool = False, max_commits: int = None) -> List[Finding]:
    """Perform scan on given path."""
    try:
        config = st.session_state.config
        scanner = Scanner(config)
        
        path_obj = Path(path)
        if not path_obj.exists():
            st.error(f"Path does not exist: {path}")
            return []
        
        with st.spinner(f"Scanning {'Git history' if git_history else 'files'}..."):
            findings = scanner.scan(
                path_obj,
                git_history=git_history,
                max_commits=max_commits
            )
        
        return findings
    except Exception as e:
        st.error(f"Error during scan: {e}")
        return []


def render_findings_summary(findings: List[Finding]):
    """Render summary statistics of findings."""
    if not findings:
        st.success("No secrets detected!")
        return
    
    st.error(f"WARNING: {len(findings)} secret(s) detected!")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Findings", len(findings))
    
    with col2:
        unique_files = len(set(f.file_path for f in findings))
        st.metric("Affected Files", unique_files)
    
    with col3:
        unique_rules = len(set(f.rule_id for f in findings))
        st.metric("Rule Types", unique_rules)
    
    with col4:
        avg_entropy = sum(f.entropy for f in findings if f.entropy) / len([f for f in findings if f.entropy])
        st.metric("Avg Entropy", f"{avg_entropy:.2f}" if avg_entropy else "N/A")


def render_findings_charts(findings: List[Finding]):
    """Render visualization charts for findings."""
    if not findings:
        return
    
    col1, col2 = st.columns(2)
    
    # Findings by rule type
    with col1:
        rule_counts = {}
        for finding in findings:
            rule_counts[finding.rule_id] = rule_counts.get(finding.rule_id, 0) + 1
        
        fig = px.bar(
            x=list(rule_counts.keys()),
            y=list(rule_counts.values()),
            labels={'x': 'Rule Type', 'y': 'Count'},
            title='Findings by Rule Type',
            color=list(rule_counts.values()),
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Findings by file
    with col2:
        file_counts = {}
        for finding in findings:
            # Truncate long file paths
            file_name = Path(finding.file_path).name
            file_counts[file_name] = file_counts.get(file_name, 0) + 1
        
        # Show top 10 files
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig = px.bar(
            x=[f[1] for f in sorted_files],
            y=[f[0] for f in sorted_files],
            orientation='h',
            labels={'x': 'Count', 'y': 'File'},
            title='Top 10 Files with Findings',
            color=[f[1] for f in sorted_files],
            color_continuous_scale='Oranges'
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Entropy distribution (if available)
    entropy_values = [f.entropy for f in findings if f.entropy is not None]
    if entropy_values:
        fig = px.histogram(
            x=entropy_values,
            nbins=20,
            labels={'x': 'Entropy Value', 'y': 'Count'},
            title='Entropy Distribution',
            color_discrete_sequence=['#FF6B6B']
        )
        st.plotly_chart(fig, use_container_width=True)


def render_findings_table(findings: List[Finding], show_entropy: bool = True):
    """Render detailed findings table."""
    if not findings:
        return
    
    st.subheader("Detailed Findings")
    
    # Convert findings to DataFrame
    data = []
    for i, finding in enumerate(findings, 1):
        row = {
            "#": i,
            "Rule ID": finding.rule_id,
            "Description": finding.description,
            "File": Path(finding.file_path).name,
            "Full Path": finding.file_path,
            "Line": finding.line_number or "N/A",
            "Secret Preview": finding.secret[:40] + "..." if len(finding.secret) > 40 else finding.secret,
        }
        
        if show_entropy and finding.entropy:
            row["Entropy"] = f"{finding.entropy:.2f}"
        
        if finding.commit_hash:
            row["Commit"] = finding.commit_hash[:8]
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Add filters
    col1, col2 = st.columns(2)
    
    with col1:
        rule_filter = st.multiselect(
            "Filter by Rule Type",
            options=sorted(df["Rule ID"].unique()),
            default=[]
        )
    
    with col2:
        file_filter = st.multiselect(
            "Filter by File",
            options=sorted(df["File"].unique()),
            default=[]
        )
    
    # Apply filters
    filtered_df = df.copy()
    if rule_filter:
        filtered_df = filtered_df[filtered_df["Rule ID"].isin(rule_filter)]
    if file_filter:
        filtered_df = filtered_df[filtered_df["File"].isin(file_filter)]
    
    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Secret Preview": st.column_config.TextColumn(
                "Secret Preview",
                help="First 40 characters of detected secret",
                width="large"
            ),
            "Entropy": st.column_config.NumberColumn(
                "Entropy",
                help="Shannon entropy value",
                format="%.2f"
            )
        }
    )
    
    # Export options
    st.subheader("Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export as JSON
        json_data = json.dumps(
            {
                "total_findings": len(findings),
                "findings": [f.to_dict() for f in findings]
            },
            indent=2
        )
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="scan_results.json",
            mime="application/json"
        )
    
    with col2:
        # Export as CSV
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="scan_results.csv",
            mime="text/csv"
        )
    
    with col3:
        # Export full report
        report = f"""# Secret Scanner Report

## Summary
- Total Findings: {len(findings)}
- Unique Files: {len(set(f.file_path for f in findings))}
- Rule Types: {len(set(f.rule_id for f in findings))}

## Findings
"""
        for i, finding in enumerate(findings, 1):
            report += f"\n### Finding {i}: {finding.rule_id}\n"
            report += f"- **Description**: {finding.description}\n"
            report += f"- **File**: {finding.file_path}\n"
            report += f"- **Line**: {finding.line_number or 'N/A'}\n"
            if finding.entropy:
                report += f"- **Entropy**: {finding.entropy:.2f}\n"
            report += f"- **Secret Preview**: {finding.secret[:60]}...\n"
        
        st.download_button(
            label="📥 Download Report (MD)",
            data=report,
            file_name="scan_report.md",
            mime="text/markdown"
        )


def main():
    """Main UI function."""
    init_session_state()
    
    # Header with logo
    logo_path = Path(__file__).parent.parent.parent / "media" / "gitfih.png"
    if logo_path.exists():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(str(logo_path), width=150)
        with col2:
            st.title("Secret Scanner")
            st.markdown("**Production-grade secret detection for Git repositories and files**")
    else:
        st.title("Secret Scanner")
        st.markdown("**Production-grade secret detection for Git repositories and files**")
    
    # Sidebar
    scan_mode, max_commits, show_entropy = render_sidebar()
    tab1, tab2, tab3, tab4 = st.tabs(["Scan Local", "Scan GitHub", "Results", "About"])
    
    with tab1:
        st.header("Scan Local Files")
        
        # Input method
        input_method = st.radio(
            "Input Method",
            ["Local Path", "Upload Files"],
            horizontal=True
        )
        
        if input_method == "Local Path":
            path = st.text_input(
                "Enter path to scan",
                value=os.getcwd(),
                help="Absolute or relative path to file or directory"
            )
            
            if st.button("🚀 Start Scan", type="primary", use_container_width=True, key="local_scan"):
                if path:
                    findings = scan_path(
                        path,
                        git_history=(scan_mode == "Git History"),
                        max_commits=max_commits
                    )
                    st.session_state.scan_results = findings
                    st.rerun()
                else:
                    st.error("Please enter a path")
        
        else:  # Upload Files
            uploaded_files = st.file_uploader(
                "Upload files to scan",
                accept_multiple_files=True,
                help="Upload source code files to scan for secrets"
            )
            
            if uploaded_files and st.button("🚀 Start Scan", type="primary", use_container_width=True, key="upload_scan"):
                # Create temp directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Save uploaded files
                    for uploaded_file in uploaded_files:
                        file_path = temp_path / uploaded_file.name
                        file_path.write_bytes(uploaded_file.getvalue())
                    
                    # Scan temp directory
                    findings = scan_path(str(temp_path))
                    st.session_state.scan_results = findings
                    st.rerun()
    
    with tab2:
        st.header("Scan GitHub Repositories")
        
        # GitHub authentication (required)
        with st.expander("🔐 GitHub Authentication (Required)", expanded=True):
            st.markdown("""
            **Required:** Authenticate with your GitHub Personal Access Token to scan public repositories.
            
            **How to create a PAT:**
            1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
            2. Click "Generate new token (classic)"
            3. Give it a name (e.g., "Secret Scanner")
            4. Select scope: **`public_repo`** (read-only access to public repositories)
            5. Click "Generate token" and copy it
            """)
            
            github_token = st.text_input(
                "GitHub Personal Access Token (PAT)",
                type="password",
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
                value=st.session_state.get('github_token', ''),
                help="Your GitHub PAT with 'public_repo' scope"
            )
            
            # Store token in session state
            if github_token:
                st.session_state.github_token = github_token
            
            # Validate and show authenticated user info
            if github_token:
                try:
                    gh_scanner = GitHubScanner(st.session_state.config, github_token)
                    auth_user = gh_scanner.github.get_user()
                    st.success(f"Authenticated as: **{auth_user.login}** ({auth_user.name or 'No name'})")
                    
                    # Show rate limit
                    rate_limit = gh_scanner.get_rate_limit()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("API Requests Remaining", rate_limit['core']['remaining'])
                    with col2:
                        st.metric("Search Requests Remaining", rate_limit['search']['remaining'])
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
                    st.info("Please verify your token is valid and has the correct scopes.")
            else:
                st.warning("Please enter your Personal Access Token to proceed.")
        
        # Scan mode
        github_scan_mode = st.radio(
            "Scan Mode",
            ["Single Repository", "User Repositories", "Organization Repositories", "Search Repositories"],
            horizontal=False
        )
        
        if github_scan_mode == "Single Repository":
            repo_input = st.text_input(
                "Repository URL or owner/repo",
                placeholder="https://github.com/owner/repo or owner/repo",
                help="Enter GitHub repository URL or owner/repo format"
            )
            
            scan_git_history = st.checkbox(
                "Scan Git History",
                value=False,
                help="Scan commit history for secrets (slower)"
            )
            
            if st.button("Scan Repository", type="primary", use_container_width=True):
                if not github_token:
                    st.error("Please authenticate with your GitHub token first (see settings above)")
                elif repo_input:
                    try:
                        gh_scanner = GitHubScanner(st.session_state.config, github_token)
                        with st.spinner(f"Scanning repository..."):
                            result = gh_scanner.scan_repository(
                                repo_input,
                                scan_history=scan_git_history,
                                max_commits=max_commits
                            )
                        
                        st.success(f"Scanned {result['repo_name']}")
                        st.session_state.scan_results = result['findings']
                        
                        # Show repo info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Stars", result['stars'])
                        with col2:
                            st.metric("Language", result['language'] or "N/A")
                        with col3:
                            st.metric("Findings", result['total_findings'])
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter a repository URL or owner/repo")
        
        elif github_scan_mode == "User Repositories":
            st.info("💡 Scan public repositories from any GitHub user (including yourself)")
            
            # Option to quickly use authenticated user
            if github_token:
                try:
                    gh_scanner = GitHubScanner(st.session_state.config, github_token)
                    auth_username = gh_scanner.authenticated_user
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        username = st.text_input(
                            "GitHub Username",
                            placeholder="octocat",
                            help="Enter any GitHub username to scan their public repositories",
                            value=""
                        )
                    with col2:
                        st.write("")  # Spacing
                        st.write("")  # Spacing
                        if st.button("Use My Account", help=f"Scan {auth_username}'s repos"):
                            username = auth_username
                            st.session_state.scan_username = auth_username
                    
                    # Use session state value if set
                    if 'scan_username' in st.session_state and st.session_state.scan_username:
                        username = st.session_state.scan_username
                        st.caption(f"Scanning: **{username}**")
                except:
                    username = st.text_input(
                        "GitHub Username",
                        placeholder="octocat",
                        help="Enter GitHub username to scan their public repositories"
                    )
            else:
                username = st.text_input(
                    "GitHub Username",
                    placeholder="octocat",
                    help="Enter GitHub username to scan their public repositories"
                )
            
            max_repos = st.slider(
                "Maximum Repositories to Scan",
                min_value=1,
                max_value=20,
                value=5,
                help="Limit number of repositories to scan"
            )
            
            if st.button("Scan User Repos", type="primary", use_container_width=True):
                if not github_token:
                    st.error("Please authenticate with your GitHub token first (see settings above)")
                elif username:
                    try:
                        gh_scanner = GitHubScanner(st.session_state.config, github_token)
                        with st.spinner(f"Scanning repositories for {username}..."):
                            results = gh_scanner.scan_user_repositories(
                                username,
                                max_repos=max_repos,
                                scan_history=False
                            )
                        
                        # Store both individual results and aggregated findings
                        all_findings = []
                        for result in results:
                            all_findings.extend(result['findings'])
                        
                        st.session_state.scan_results = all_findings
                        st.session_state.repo_results = results  # Store individual repo results
                        
                        st.success(f"Scanned {len(results)} repositories")
                        
                        # Show individual repository results
                        st.subheader("Repository Scan Results")
                        total_secrets = 0
                        for idx, result in enumerate(results, 1):
                            with st.expander(f"{idx}. {result['repo_name']} - {result['total_findings']} findings", expanded=result['total_findings'] > 0):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Stars", result['stars'])
                                with col2:
                                    st.metric("Language", result['language'] or "N/A")
                                with col3:
                                    st.metric("Findings", result['total_findings'])
                                
                                if result['findings']:
                                    st.warning(f"Found {result['total_findings']} potential secrets in this repository")
                                    for finding in result['findings'][:5]:  # Show first 5
                                        st.code(f"{finding.file}:{finding.line} - {finding.rule_id}", language="text")
                                    if len(result['findings']) > 5:
                                        st.caption(f"... and {len(result['findings']) - 5} more findings")
                                else:
                                    st.success("No secrets detected")
                            total_secrets += result['total_findings']
                        
                        st.divider()
                        st.metric("Total Secrets Found Across All Repos", total_secrets)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter a GitHub username or click 'Use My Account' button above")
        
        elif github_scan_mode == "Organization Repositories":
            org_name = st.text_input(
                "Organization Name",
                placeholder="github",
                help="Enter GitHub organization name"
            )
            
            max_repos = st.slider(
                "Maximum Repositories to Scan",
                min_value=1,
                max_value=20,
                value=5,
                help="Limit number of repositories to scan",
                key="org_max_repos"
            )
            
            if st.button("Scan Org Repos", type="primary", use_container_width=True):
                if not github_token:
                    st.error("Please authenticate with your GitHub token first (see settings above)")
                elif org_name:
                    try:
                        gh_scanner = GitHubScanner(st.session_state.config, github_token)
                        with st.spinner(f"Scanning repositories for {org_name}..."):
                            results = gh_scanner.scan_organization_repositories(
                                org_name,
                                max_repos=max_repos,
                                scan_history=False
                            )
                        
                        # Store both individual results and aggregated findings
                        all_findings = []
                        for result in results:
                            all_findings.extend(result['findings'])
                        
                        st.session_state.scan_results = all_findings
                        st.session_state.repo_results = results  # Store individual repo results
                        
                        st.success(f"Scanned {len(results)} repositories")
                        
                        # Show individual repository results
                        st.subheader("Repository Scan Results")
                        total_secrets = 0
                        for idx, result in enumerate(results, 1):
                            with st.expander(f"{idx}. {result['repo_name']} - {result['total_findings']} findings", expanded=result['total_findings'] > 0):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Stars", result['stars'])
                                with col2:
                                    st.metric("Language", result['language'] or "N/A")
                                with col3:
                                    st.metric("Findings", result['total_findings'])
                                
                                if result['findings']:
                                    st.warning(f"Found {result['total_findings']} potential secrets in this repository")
                                    for finding in result['findings'][:5]:  # Show first 5
                                        st.code(f"{finding.file}:{finding.line} - {finding.rule_id}", language="text")
                                    if len(result['findings']) > 5:
                                        st.caption(f"... and {len(result['findings']) - 5} more findings")
                                else:
                                    st.success("No secrets detected")
                            total_secrets += result['total_findings']
                        
                        st.divider()
                        st.metric("Total Secrets Found Across All Repos", total_secrets)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter an organization name")
        
        else:  # Search Repositories
            search_query = st.text_input(
                "Search Query",
                placeholder="language:python stars:>100",
                help="GitHub search query (e.g., 'language:python stars:>100 topic:web')"
            )
            
            max_repos = st.slider(
                "Maximum Repositories to Scan",
                min_value=1,
                max_value=10,
                value=3,
                help="Limit number of repositories to scan",
                key="search_max_repos"
            )
            
            if st.button("Search & Scan", type="primary", use_container_width=True):
                if not github_token:
                    st.error("Please authenticate with your GitHub token first (see settings above)")
                elif search_query:
                    try:
                        gh_scanner = GitHubScanner(st.session_state.config, github_token)
                        with st.spinner(f"Searching and scanning repositories..."):
                            results = gh_scanner.search_and_scan(
                                search_query,
                                max_repos=max_repos,
                                scan_history=False
                            )
                        
                        # Store both individual results and aggregated findings
                        all_findings = []
                        for result in results:
                            all_findings.extend(result['findings'])
                        
                        st.session_state.scan_results = all_findings
                        st.session_state.repo_results = results  # Store individual repo results
                        
                        st.success(f"Scanned {len(results)} repositories")
                        
                        # Show individual repository results
                        st.subheader("Repository Scan Results")
                        total_secrets = 0
                        for idx, result in enumerate(results, 1):
                            with st.expander(f"{idx}. {result['repo_name']} - {result['total_findings']} findings", expanded=result['total_findings'] > 0):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Stars", result['stars'])
                                with col2:
                                    st.metric("Language", result['language'] or "N/A")
                                with col3:
                                    st.metric("Findings", result['total_findings'])
                                
                                if result['findings']:
                                    st.warning(f"Found {result['total_findings']} potential secrets in this repository")
                                    for finding in result['findings'][:5]:  # Show first 5
                                        st.code(f"{finding.file}:{finding.line} - {finding.rule_id}", language="text")
                                    if len(result['findings']) > 5:
                                        st.caption(f"... and {len(result['findings']) - 5} more findings")
                                else:
                                    st.success("No secrets detected")
                            total_secrets += result['total_findings']
                        
                        st.divider()
                        st.metric("Total Secrets Found Across All Repos", total_secrets)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter a search query")
    
    with tab3:
        st.header("Scan Results")
        
        if st.session_state.scan_results is not None:
            findings = st.session_state.scan_results
            
            # Summary
            render_findings_summary(findings)
            
            if findings:
                st.divider()
                
                # Charts
                st.subheader("Visualization")
                render_findings_charts(findings)
                
                st.divider()
                
                # Detailed table
                render_findings_table(findings, show_entropy)
        else:
            st.info("No scan results yet. Go to the 'Scan Local' or 'Scan GitHub' tab to start scanning.")
    
    with tab4:
        st.header("About Secret Scanner")
        
        st.markdown("""
        ### Features
        - **30+ Detection Rules** - AWS, GitHub, Stripe, API keys, and more
        - **Shannon Entropy Analysis** - Detect high-randomness secrets
        - **Git History Scanning** - Find secrets in commit history
        - **GitHub Integration** - Scan public repositories directly
        - **Interactive UI** - Easy-to-use web interface
        - **Visualizations** - Charts and graphs for analysis
        - **Export Options** - JSON, CSV, Markdown reports
        
        ### Detection Categories
        - Cloud Credentials (AWS, Google Cloud, Azure)
        - Version Control Tokens (GitHub, GitLab)
        - API Keys (Stripe, Slack, SendGrid, Twilio)
        - Database Connection Strings
        - Private Keys (RSA, EC, OpenSSH)
        - JWT Tokens
        - Generic High-Entropy Strings
        
        ### How It Works
        1. **Pattern Matching**: Regex-based detection for known secret formats
        2. **Entropy Analysis**: Shannon entropy calculation to find random-looking strings
        3. **Smart Filtering**: Keyword optimization and path exclusions
        4. **Reporting**: Detailed findings with line numbers and file paths
        
        ### Usage Tips
        - Use **Git History** mode to find secrets introduced in past commits
        - Enable **Show Entropy Values** to see randomness scores
        - Filter results by **Rule Type** or **File** for focused analysis
        - Export results for documentation or compliance reporting
        
        ### Version
        - **Version**: 0.1.0
        - **License**: MIT
        - **Python**: 3.10+
        
        ### Resources
        - [Documentation](README.md)
        - [GitHub Repository](#)
        - [Report Issues](#)
        """)
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Detection Rules", len(st.session_state.config.rules) if st.session_state.config else "N/A")
        
        with col2:
            st.metric("Exclusions", len(st.session_state.config.exclusions) if st.session_state.config else "N/A")
        
        with col3:
            st.metric("Status", "Ready")


if __name__ == "__main__":
    main()
