"""GitHub repository scanner for detecting secrets in public repositories."""

import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import git
from github import Github, Repository, GithubException
import requests
import time

from .scanner import Scanner, Finding
from .config import Config


class GitHubScanner:
    """Scanner for GitHub public repositories."""
    
    def __init__(self, config: Config, github_token: str):
        """
        Initialize GitHub scanner with authenticated access.
        
        Args:
            config: Scanner configuration
            github_token: GitHub personal access token (PAT)
        """
        self.config = config
        self.scanner = Scanner(config)
        self.github_token = github_token
        self.github = Github(github_token)
        
        # Verify authentication
        try:
            user = self.github.get_user()
            self.authenticated_user = user.login
        except Exception as e:
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            raise ValueError(f"Authentication failed: {error_msg}. Please check your token.")
    
    def scan_repository(
        self,
        repo_url: str,
        scan_history: bool = False,
        max_commits: Optional[int] = 100
    ) -> Dict:
        """
        Scan a GitHub repository for secrets.
        
        Args:
            repo_url: GitHub repository URL or owner/repo format
            scan_history: Whether to scan Git history
            max_commits: Maximum commits to scan if scan_history=True
            
        Returns:
            Dictionary with findings and metadata
        """
        # Parse repository URL
        repo_name = self._parse_repo_url(repo_url)
        
        try:
            # Get repository info
            repo = self.github.get_repo(repo_name)
            
            # Clone repository to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                print(f"Cloning repository: {repo.full_name}...")
                git.Repo.clone_from(repo.clone_url, temp_path, depth=max_commits if scan_history else 1)
                
                # Scan the repository
                print(f"Scanning repository...")
                findings = self.scanner.scan(
                    temp_path,
                    git_history=scan_history,
                    max_commits=max_commits
                )
                
                return {
                    "repo_name": repo.full_name,
                    "repo_url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "language": repo.language,
                    "is_fork": repo.fork,
                    "findings": findings,
                    "total_findings": len(findings)
                }
        
        except GithubException as e:
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except git.exc.GitCommandError as e:
            raise ValueError(f"Git clone error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error scanning repository: {str(e)}")
    
    def scan_user_repositories(
        self,
        username: str,
        max_repos: int = 10,
        scan_history: bool = False
    ) -> List[Dict]:
        """
        Scan multiple repositories from a GitHub user.
        
        Args:
            username: GitHub username
            max_repos: Maximum number of repositories to scan
            scan_history: Whether to scan Git history
            
        Returns:
            List of scan results for each repository
        """
        try:
            user = self.github.get_user(username)
            repos = user.get_repos(sort='updated', direction='desc')
            
            results = []
            scanned = 0
            
            for repo in repos:
                if scanned >= max_repos:
                    break
                
                # Skip private repos and forks (optional)
                if repo.private:
                    continue
                
                try:
                    print(f"\nScanning {repo.full_name}...")
                    result = self.scan_repository(
                        repo.full_name,
                        scan_history=scan_history,
                        max_commits=50
                    )
                    results.append(result)
                    scanned += 1
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error scanning {repo.full_name}: {e}")
                    continue
            
            return results
            
        except GithubException as e:
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def scan_organization_repositories(
        self,
        org_name: str,
        max_repos: int = 10,
        scan_history: bool = False
    ) -> List[Dict]:
        """
        Scan repositories from a GitHub organization.
        
        Args:
            org_name: GitHub organization name
            max_repos: Maximum number of repositories to scan
            scan_history: Whether to scan Git history
            
        Returns:
            List of scan results for each repository
        """
        try:
            org = self.github.get_organization(org_name)
            repos = org.get_repos(sort='updated', direction='desc')
            
            results = []
            scanned = 0
            
            for repo in repos:
                if scanned >= max_repos:
                    break
                
                if repo.private:
                    continue
                
                try:
                    print(f"\nScanning {repo.full_name}...")
                    result = self.scan_repository(
                        repo.full_name,
                        scan_history=scan_history,
                        max_commits=50
                    )
                    results.append(result)
                    scanned += 1
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error scanning {repo.full_name}: {e}")
                    continue
            
            return results
            
        except GithubException as e:
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def search_and_scan(
        self,
        query: str,
        max_repos: int = 5,
        scan_history: bool = False
    ) -> List[Dict]:
        """
        Search GitHub and scan matching repositories.
        
        Args:
            query: Search query (e.g., "language:python stars:>100")
            max_repos: Maximum repositories to scan
            scan_history: Whether to scan Git history
            
        Returns:
            List of scan results
        """
        try:
            repos = self.github.search_repositories(query=query, sort='stars', order='desc')
            
            results = []
            scanned = 0
            
            for repo in repos:
                if scanned >= max_repos:
                    break
                
                if repo.private:
                    continue
                
                try:
                    print(f"\nScanning {repo.full_name}...")
                    result = self.scan_repository(
                        repo.full_name,
                        scan_history=scan_history,
                        max_commits=50
                    )
                    results.append(result)
                    scanned += 1
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error scanning {repo.full_name}: {e}")
                    continue
            
            return results
            
        except GithubException as e:
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def get_rate_limit(self) -> Dict:
        """Get current GitHub API rate limit status."""
        try:
            rate_limit = self.github.get_rate_limit()
            # Access the rate limit data via resources
            resources = rate_limit.resources
            return {
                "core": {
                    "limit": resources.core.limit,
                    "remaining": resources.core.remaining,
                    "reset": resources.core.reset
                },
                "search": {
                    "limit": resources.search.limit,
                    "remaining": resources.search.remaining,
                    "reset": resources.search.reset
                }
            }
        except (AttributeError, Exception) as e:
            # Fallback if rate limit structure is different
            return {
                "core": {
                    "limit": 5000,
                    "remaining": 5000,
                    "reset": None
                },
                "search": {
                    "limit": 30,
                    "remaining": 30,
                    "reset": None
                }
            }
    
    @staticmethod
    def _parse_repo_url(repo_url: str) -> str:
        """
        Parse GitHub repository URL to owner/repo format.
        
        Args:
            repo_url: URL or owner/repo format
            
        Returns:
            owner/repo format
        """
        # Already in owner/repo format
        if '/' in repo_url and not repo_url.startswith('http'):
            return repo_url
        
        # Parse from URL
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1].replace('.git', '')}"
        
        raise ValueError(f"Invalid repository URL or format: {repo_url}")
