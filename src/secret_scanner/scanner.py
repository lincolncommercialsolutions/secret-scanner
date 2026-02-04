"""Core scanner module for detecting secrets in files and Git repositories."""

import re
from pathlib import Path
from typing import List, Dict, Optional, Iterator
from dataclasses import dataclass
import git

from .detectors.entropy import shannon_entropy
from .config import Config


@dataclass
class Finding:
    """Represents a detected secret or sensitive information."""
    
    rule_id: str
    description: str
    secret: str
    file_path: str
    line_number: Optional[int] = None
    commit_hash: Optional[str] = None
    entropy: Optional[float] = None
    
    def __str__(self):
        parts = [f"[{self.rule_id}] {self.description}"]
        parts.append(f"\n  File: {self.file_path}")
        
        if self.line_number:
            parts.append(f":{self.line_number}")
        
        if self.commit_hash:
            parts.append(f"\n  Commit: {self.commit_hash[:8]}")
        
        if self.entropy:
            parts.append(f"\n  Entropy: {self.entropy:.2f}")
        
        # Truncate secret for display (security)
        display_secret = self.secret[:60] + "..." if len(self.secret) > 60 else self.secret
        parts.append(f"\n  Secret: {display_secret}")
        
        return "".join(parts)
    
    def to_dict(self) -> dict:
        """Convert finding to dictionary for JSON/structured output."""
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "commit_hash": self.commit_hash,
            "entropy": round(self.entropy, 2) if self.entropy else None,
            "secret_preview": self.secret[:20] + "..." if len(self.secret) > 20 else self.secret
        }


def should_skip_path(path: str, exclusions: List[str]) -> bool:
    """
    Check if a file path should be skipped based on exclusion patterns.
    
    Args:
        path: File path to check
        exclusions: List of regex patterns to match against
        
    Returns:
        True if path should be skipped
    """
    return any(re.search(pattern, path) for pattern in exclusions)


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary (heuristic check).
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file appears to be binary
    """
    # Common binary extensions
    binary_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.pdf', '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z',
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.pyc', '.pyo', '.class', '.o', '.a'
    }
    
    if file_path.suffix.lower() in binary_extensions:
        return True
    
    # Check file content for null bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True


def scan_content(
    content: str,
    rules: List[Dict],
    file_path: str = "",
    commit_hash: Optional[str] = None,
    exclusions: Optional[List[str]] = None
) -> List[Finding]:
    """
    Scan text content for secrets based on rules.
    
    Args:
        content: Text content to scan
        rules: List of rule dictionaries
        file_path: Path to file being scanned (for reporting)
        commit_hash: Git commit hash if scanning history
        exclusions: List of path exclusion patterns
        
    Returns:
        List of Finding objects
    """
    if exclusions and should_skip_path(file_path, exclusions):
        return []
    
    findings = []
    
    for rule in rules:
        try:
            pattern = re.compile(rule['regex'], re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            print(f"Warning: Invalid regex in rule '{rule['id']}': {e}")
            continue
        
        # Pre-filter by keywords if specified (performance optimization)
        keywords = rule.get('keywords', [])
        if keywords:
            has_keyword = any(kw.lower() in content.lower() for kw in keywords)
            if not has_keyword:
                continue
        
        for match in pattern.finditer(content):
            secret = match.group(0)
            
            # Calculate entropy
            ent = shannon_entropy(secret)
            min_entropy = rule.get('entropy')
            
            # Filter by entropy threshold if specified
            if min_entropy is not None and ent < min_entropy:
                continue
            
            # Find line number
            line_number = content[:match.start()].count('\n') + 1
            
            finding = Finding(
                rule_id=rule['id'],
                description=rule.get('description', rule['id']),
                secret=secret,
                file_path=file_path,
                line_number=line_number,
                commit_hash=commit_hash,
                entropy=ent
            )
            
            findings.append(finding)
    
    return findings


def scan_file(file_path: Path, config: Config) -> List[Finding]:
    """
    Scan a single file for secrets.
    
    Args:
        file_path: Path to file to scan
        config: Configuration object with rules and exclusions
        
    Returns:
        List of Finding objects
    """
    if not file_path.is_file():
        return []
    
    # Check exclusions
    if should_skip_path(str(file_path), config.exclusions):
        return []
    
    # Skip binary files
    if is_binary_file(file_path):
        return []
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []
    
    return scan_content(
        content,
        config.rules,
        file_path=str(file_path),
        exclusions=config.exclusions
    )


def scan_directory(directory: Path, config: Config) -> List[Finding]:
    """
    Recursively scan a directory for secrets.
    
    Args:
        directory: Path to directory to scan
        config: Configuration object with rules and exclusions
        
    Returns:
        List of Finding objects
    """
    all_findings = []
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            findings = scan_file(file_path, config)
            all_findings.extend(findings)
    
    return all_findings


def scan_git_history(
    repo_path: Path,
    config: Config,
    max_commits: Optional[int] = None,
    branch: str = "HEAD"
) -> List[Finding]:
    """
    Scan Git commit history for secrets.
    
    Args:
        repo_path: Path to Git repository
        config: Configuration object with rules and exclusions
        max_commits: Maximum number of commits to scan (None for all)
        branch: Branch to scan (default: HEAD)
        
    Returns:
        List of Finding objects
    """
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError(f"Not a valid Git repository: {repo_path}")
    
    all_findings = []
    
    # Get commits
    commits = list(repo.iter_commits(branch, max_count=max_commits))
    
    for commit in commits:
        # Get parent (for diff)
        parent = commit.parents[0] if commit.parents else git.NULL_TREE
        
        # Get diff
        diffs = commit.diff(parent, create_patch=True)
        
        for diff in diffs:
            # Skip binary files
            if diff.diff is None:
                continue
            
            file_path = diff.b_path if diff.b_path else diff.a_path
            
            # Check exclusions
            if should_skip_path(file_path, config.exclusions):
                continue
            
            try:
                # Decode diff content
                diff_text = diff.diff.decode('utf-8', errors='ignore')
                
                # Scan added lines (lines starting with +)
                added_lines = []
                for line in diff_text.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        added_lines.append(line[1:])  # Remove + prefix
                
                if added_lines:
                    content = '\n'.join(added_lines)
                    findings = scan_content(
                        content,
                        config.rules,
                        file_path=file_path,
                        commit_hash=commit.hexsha,
                        exclusions=config.exclusions
                    )
                    all_findings.extend(findings)
                    
            except Exception as e:
                print(f"Warning: Error processing commit {commit.hexsha[:8]}: {e}")
                continue
    
    return all_findings


class Scanner:
    """Main scanner class for orchestrating secret detection."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def scan(
        self,
        target: Path,
        git_history: bool = False,
        max_commits: Optional[int] = None
    ) -> List[Finding]:
        """
        Scan a target path for secrets.
        
        Args:
            target: Path to file, directory, or Git repository
            git_history: Whether to scan Git history
            max_commits: Maximum commits to scan (if git_history=True)
            
        Returns:
            List of Finding objects
        """
        target = Path(target)
        
        if not target.exists():
            raise FileNotFoundError(f"Target not found: {target}")
        
        if git_history:
            return scan_git_history(target, self.config, max_commits)
        elif target.is_file():
            return scan_file(target, self.config)
        elif target.is_dir():
            return scan_directory(target, self.config)
        else:
            raise ValueError(f"Invalid target: {target}")
