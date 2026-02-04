"""Command-line interface for the secret scanner."""

import sys
import click
from pathlib import Path
from typing import Optional

from . import __version__
from .config import load_rules, validate_config
from .scanner import Scanner
from .reporters.reporter import get_reporter


@click.group()
@click.version_option(version=__version__)
def main():
    """Secret Scanner - Detect secrets and sensitive information in code."""
    pass


@main.command()
@click.argument('targets', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--rules', '-r',
    type=click.Path(exists=True),
    help='Path to custom rules YAML file'
)
@click.option(
    '--git-history', '-g',
    is_flag=True,
    help='Scan Git commit history instead of current files'
)
@click.option(
    '--max-commits',
    type=int,
    default=None,
    help='Maximum number of commits to scan (default: all)'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['console', 'json', 'sarif', 'summary'], case_sensitive=False),
    default='console',
    help='Output format'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Verbose output (show entropy values, etc.)'
)
@click.option(
    '--exit-code/--no-exit-code',
    default=True,
    help='Exit with code 1 if secrets found (useful for CI/CD)'
)
def scan(
    targets: tuple,
    rules: Optional[str],
    git_history: bool,
    max_commits: Optional[int],
    format: str,
    verbose: bool,
    exit_code: bool
):
    """
    Scan files, directories, or Git repositories for secrets.
    
    Examples:
    
      # Scan current directory
      secret-scanner scan .
      
      # Scan specific files
      secret-scanner scan file1.py file2.js
      
      # Scan Git history
      secret-scanner scan --git-history /path/to/repo
      
      # Use custom rules
      secret-scanner scan --rules custom_rules.yaml .
      
      # Output as JSON
      secret-scanner scan --format json .
    """
    try:
        # Load configuration
        config = load_rules(rules)
        
        # Validate config and show warnings
        warnings = validate_config(config)
        if warnings and verbose:
            click.echo(click.style("⚠  Configuration warnings:", fg='yellow'))
            for warning in warnings:
                click.echo(click.style(f"   • {warning}", fg='yellow'))
            click.echo()
        
        # Create scanner
        scanner = Scanner(config)
        
        # Scan all targets
        all_findings = []
        for target in targets:
            target_path = Path(target)
            
            if verbose:
                mode = "Git history" if git_history else "files"
                click.echo(f"Scanning {mode} in: {target_path}")
            
            try:
                findings = scanner.scan(
                    target_path,
                    git_history=git_history,
                    max_commits=max_commits
                )
                all_findings.extend(findings)
            except Exception as e:
                click.echo(click.style(f"Error scanning {target}: {e}", fg='red'), err=True)
                if verbose:
                    import traceback
                    traceback.print_exc()
                continue
        
        # Report results
        reporter_kwargs = {}
        if format == 'console':
            reporter_kwargs['verbose'] = verbose
        elif format == 'json':
            reporter_kwargs['pretty'] = True
        
        reporter = get_reporter(format, **reporter_kwargs)
        reporter.report(all_findings)
        
        # Exit with appropriate code
        if exit_code and all_findings:
            sys.exit(1)
        
    except Exception as e:
        click.echo(click.style(f"Fatal error: {e}", fg='red', bold=True), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


@main.command()
@click.option(
    '--rules', '-r',
    type=click.Path(exists=True),
    help='Path to rules YAML file to validate'
)
def validate(rules: Optional[str]):
    """
    Validate a rules configuration file.
    
    Examples:
    
      # Validate default rules
      secret-scanner validate
      
      # Validate custom rules
      secret-scanner validate --rules my_rules.yaml
    """
    try:
        config = load_rules(rules)
        
        click.echo(click.style("✓ Configuration loaded successfully", fg='green'))
        click.echo(f"  Rules: {len(config.rules)}")
        click.echo(f"  Exclusions: {len(config.exclusions)}")
        click.echo()
        
        # Validate and show warnings
        warnings = validate_config(config)
        if warnings:
            click.echo(click.style("⚠  Warnings:", fg='yellow'))
            for warning in warnings:
                click.echo(click.style(f"   • {warning}", fg='yellow'))
        else:
            click.echo(click.style("✓ No validation warnings", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"✗ Validation failed: {e}", fg='red', bold=True), err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--rules', '-r',
    type=click.Path(exists=True),
    help='Path to rules YAML file'
)
def list_rules(rules: Optional[str]):
    """
    List all available detection rules.
    
    Examples:
    
      # List default rules
      secret-scanner list-rules
      
      # List custom rules
      secret-scanner list-rules --rules my_rules.yaml
    """
    try:
        config = load_rules(rules)
        
        click.echo(f"\nAvailable Rules ({len(config.rules)}):\n")
        
        for rule in config.rules:
            click.echo(click.style(f"• {rule['id']}", fg='cyan', bold=True))
            click.echo(f"  {rule.get('description', 'No description')}")
            
            if rule.get('entropy'):
                click.echo(f"  Entropy threshold: {rule['entropy']}")
            
            if rule.get('keywords'):
                click.echo(f"  Keywords: {', '.join(rule['keywords'])}")
            
            if rule.get('tags'):
                click.echo(f"  Tags: {', '.join(rule['tags'])}")
            
            click.echo()
        
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        sys.exit(1)


@main.command()
@click.argument('repo_url')
@click.option(
    '--token', '-t',
    envvar='GITHUB_TOKEN',
    required=True,
    help='GitHub personal access token (or set GITHUB_TOKEN env var)'
)
@click.option(
    '--git-history', '-g',
    is_flag=True,
    help='Scan Git commit history'
)
@click.option(
    '--max-commits',
    type=int,
    default=100,
    help='Maximum commits to scan if --git-history is used'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['console', 'json', 'sarif', 'summary'], case_sensitive=False),
    default='console',
    help='Output format'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Verbose output'
)
def scan_github(repo_url: str, token: str, git_history: bool, max_commits: int, format: str, verbose: bool):
    """
    Scan a GitHub public repository for secrets with authenticated access.
    
    Examples:
    
      # Scan a repository with token
      secret-scanner scan-github owner/repo --token YOUR_TOKEN
      
      # Scan Git history
      secret-scanner scan-github owner/repo -t YOUR_TOKEN --git-history
      
      # With environment variable
      export GITHUB_TOKEN=your_token
      secret-scanner scan-github owner/repo
      
    Create a Personal Access Token at: https://github.com/settings/tokens
    Select scope: 'public_repo' for read-only access to public repositories
    """
    try:
        from .github_scanner import GitHubScanner
        
        # Load config
        config = load_rules()
        
        # Create scanner with authentication
        gh_scanner = GitHubScanner(config, token)
        
        if verbose:
            click.echo(f"Scanning GitHub repository: {repo_url}")
            if token:
                rate_limit = gh_scanner.get_rate_limit()
                click.echo(f"API Rate Limit: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']}")
        
        # Scan repository
        result = gh_scanner.scan_repository(
            repo_url,
            scan_history=git_history,
            max_commits=max_commits
        )
        
        # Report results
        click.echo(f"\n📦 Repository: {result['repo_name']}")
        click.echo(f"⭐ Stars: {result['stars']}")
        click.echo(f"💻 Language: {result['language'] or 'N/A'}")
        click.echo(f"🔍 Findings: {result['total_findings']}\n")
        
        # Format output
        reporter_kwargs = {}
        if format == 'console':
            reporter_kwargs['verbose'] = verbose
        elif format == 'json':
            reporter_kwargs['pretty'] = True
        
        reporter = get_reporter(format, **reporter_kwargs)
        reporter.report(result['findings'])
        
        # Exit code
        if result['total_findings'] > 0:
            sys.exit(1)
        
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red', bold=True), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


@main.command()
def generate_hook():
    """
    Generate a Git pre-commit hook script.
    
    This will output a bash script that can be saved to .git/hooks/pre-commit
    """
    hook_script = """#!/bin/bash
# Git pre-commit hook for secret scanning
# Auto-generated by secret-scanner

set -e

echo "Running secret scanner..."

# Run scanner on staged files
if ! secret-scanner scan --format summary .; then
    echo ""
    echo "❌ Secrets detected in staged files!"
    echo "   Please remove secrets before committing."
    echo "   Use 'git commit --no-verify' to skip this check (not recommended)."
    exit 1
fi

echo "✅ No secrets detected"
exit 0
"""
    
    click.echo(hook_script)
    click.echo("\n" + "=" * 70)
    click.echo("To install this hook, run:")
    click.echo("  secret-scanner generate-hook > .git/hooks/pre-commit")
    click.echo("  chmod +x .git/hooks/pre-commit")
    click.echo("=" * 70)


@main.command()
def ui():
    """
    Launch the interactive web UI.
    
    This starts a Streamlit-based web interface for scanning and visualization.
    """
    try:
        import streamlit.web.cli as stcli
        import sys
        from pathlib import Path
        
        # Get path to ui.py
        ui_file = Path(__file__).parent / "ui.py"
        
        if not ui_file.exists():
            click.echo(click.style("Error: UI module not found", fg='red'), err=True)
            sys.exit(1)
        
        click.echo(click.style("🚀 Starting Secret Scanner Web UI...", fg='green', bold=True))
        click.echo(click.style("   The UI will open in your browser automatically.", fg='cyan'))
        click.echo(click.style("   Press Ctrl+C to stop the server.\n", fg='cyan'))
        
        # Run streamlit
        sys.argv = ["streamlit", "run", str(ui_file), "--server.headless", "false"]
        sys.exit(stcli.main())
        
    except ImportError:
        click.echo(click.style("Error: Streamlit not installed", fg='red'), err=True)
        click.echo("Install with: poetry install")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\n\n✓ Server stopped", fg='green'))
        sys.exit(0)


if __name__ == '__main__':
    main()
