"""Reporter module for formatting and displaying scan results."""

import json
from typing import List
from colorama import Fore, Style, init

from .scanner import Finding

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class Reporter:
    """Base reporter class."""
    
    def report(self, findings: List[Finding]) -> None:
        """Generate and output report."""
        raise NotImplementedError


class ConsoleReporter(Reporter):
    """Console reporter with colored output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def report(self, findings: List[Finding]) -> None:
        """
        Print findings to console with colors.
        
        Args:
            findings: List of Finding objects to report
        """
        if not findings:
            print(f"{Fore.GREEN}✓ No secrets detected!{Style.RESET_ALL}")
            return
        
        # Group by severity/type
        print(f"\n{Fore.RED}{'=' * 70}")
        print(f"  SECRETS DETECTED: {len(findings)} finding(s)")
        print(f"{'=' * 70}{Style.RESET_ALL}\n")
        
        # Group findings by file for better readability
        findings_by_file = {}
        for finding in findings:
            key = finding.file_path
            if key not in findings_by_file:
                findings_by_file[key] = []
            findings_by_file[key].append(finding)
        
        for file_path, file_findings in findings_by_file.items():
            print(f"{Fore.CYAN}📁 {file_path}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   {len(file_findings)} finding(s){Style.RESET_ALL}\n")
            
            for finding in file_findings:
                self._print_finding(finding)
                print()  # Blank line between findings
        
        # Summary
        print(f"{Fore.RED}{'=' * 70}")
        print(f"  TOTAL: {len(findings)} secret(s) found across {len(findings_by_file)} file(s)")
        print(f"{'=' * 70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚠  Action required: Review and remove these secrets!{Style.RESET_ALL}\n")
    
    def _print_finding(self, finding: Finding) -> None:
        """Print a single finding with formatting."""
        # Rule ID and description
        print(f"  {Fore.RED}🔑 [{finding.rule_id}]{Style.RESET_ALL} {finding.description}")
        
        # Line number
        if finding.line_number:
            print(f"     Line: {Fore.YELLOW}{finding.line_number}{Style.RESET_ALL}")
        
        # Commit hash
        if finding.commit_hash:
            print(f"     Commit: {Fore.MAGENTA}{finding.commit_hash[:8]}{Style.RESET_ALL}")
        
        # Entropy
        if finding.entropy and self.verbose:
            color = Fore.RED if finding.entropy > 4.0 else Fore.YELLOW
            print(f"     Entropy: {color}{finding.entropy:.2f}{Style.RESET_ALL}")
        
        # Secret preview (truncated)
        display_secret = finding.secret[:60] + "..." if len(finding.secret) > 60 else finding.secret
        print(f"     {Fore.WHITE}{Style.DIM}Secret: {display_secret}{Style.RESET_ALL}")


class JSONReporter(Reporter):
    """JSON reporter for machine-readable output."""
    
    def __init__(self, pretty: bool = True):
        self.pretty = pretty
    
    def report(self, findings: List[Finding]) -> None:
        """
        Output findings as JSON.
        
        Args:
            findings: List of Finding objects to report
        """
        output = {
            "total_findings": len(findings),
            "findings": [f.to_dict() for f in findings]
        }
        
        if self.pretty:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output))


class SARIFReporter(Reporter):
    """SARIF reporter for CI/CD integration."""
    
    def report(self, findings: List[Finding]) -> None:
        """
        Output findings in SARIF format.
        
        Args:
            findings: List of Finding objects to report
        """
        # Build SARIF results
        results = []
        for finding in findings:
            result = {
                "ruleId": finding.rule_id,
                "level": "error",
                "message": {
                    "text": finding.description
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.file_path
                        },
                        "region": {
                            "startLine": finding.line_number or 1
                        }
                    }
                }]
            }
            
            if finding.commit_hash:
                result["versionControlProvenance"] = [{
                    "revisionId": finding.commit_hash
                }]
            
            results.append(result)
        
        # Build SARIF document
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "secret-scanner",
                        "version": "0.1.0",
                        "informationUri": "https://github.com/yourusername/secret-scanner"
                    }
                },
                "results": results
            }]
        }
        
        print(json.dumps(sarif, indent=2))


class SummaryReporter(Reporter):
    """Brief summary reporter."""
    
    def report(self, findings: List[Finding]) -> None:
        """
        Print brief summary of findings.
        
        Args:
            findings: List of Finding objects to report
        """
        if not findings:
            print("✓ No secrets detected")
            return
        
        # Count by rule type
        rule_counts = {}
        for finding in findings:
            rule_id = finding.rule_id
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        
        print(f"\n⚠  {len(findings)} secret(s) detected:\n")
        for rule_id, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rule_id}: {count}")
        print()


def get_reporter(format_type: str = "console", **kwargs) -> Reporter:
    """
    Factory function to get appropriate reporter.
    
    Args:
        format_type: Type of reporter (console, json, sarif, summary)
        **kwargs: Additional arguments for reporter
        
    Returns:
        Reporter instance
    """
    reporters = {
        "console": ConsoleReporter,
        "json": JSONReporter,
        "sarif": SARIFReporter,
        "summary": SummaryReporter
    }
    
    reporter_class = reporters.get(format_type.lower())
    if not reporter_class:
        raise ValueError(f"Unknown reporter type: {format_type}")
    
    return reporter_class(**kwargs)
