"""Unit tests for the scanner module."""

import pytest
import tempfile
from pathlib import Path
from secret_scanner.scanner import (
    Finding,
    should_skip_path,
    is_binary_file,
    scan_content,
    scan_file
)
from secret_scanner.config import Config


class TestFinding:
    """Tests for Finding dataclass."""
    
    def test_finding_creation(self):
        """Creating a Finding should work."""
        finding = Finding(
            rule_id="test-rule",
            description="Test Description",
            secret="test-secret",
            file_path="/path/to/file.py",
            line_number=42
        )
        assert finding.rule_id == "test-rule"
        assert finding.line_number == 42
    
    def test_finding_to_dict(self):
        """Converting Finding to dict should work."""
        finding = Finding(
            rule_id="test-rule",
            description="Test",
            secret="verylongsecret" * 10,
            file_path="file.py"
        )
        d = finding.to_dict()
        assert d["rule_id"] == "test-rule"
        assert "secret_preview" in d
        assert len(d["secret_preview"]) <= 23  # 20 + "..."


class TestShouldSkipPath:
    """Tests for path exclusion logic."""
    
    def test_skip_node_modules(self):
        """node_modules should be skipped."""
        assert should_skip_path("node_modules/package/file.js", [r"node_modules/"])
    
    def test_skip_venv(self):
        """.venv should be skipped."""
        assert should_skip_path(".venv/lib/python3.10/site.py", [r"\.venv/"])
    
    def test_dont_skip_normal_path(self):
        """Normal paths should not be skipped."""
        assert not should_skip_path("src/main.py", [r"node_modules/", r"\.venv/"])


class TestIsBinaryFile:
    """Tests for binary file detection."""
    
    def test_image_extension(self):
        """Image files should be detected as binary."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            assert is_binary_file(temp_path)
        finally:
            temp_path.unlink()
    
    def test_text_file(self):
        """Text files should not be detected as binary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')")
            temp_path = Path(f.name)
        
        try:
            assert not is_binary_file(temp_path)
        finally:
            temp_path.unlink()


class TestScanContent:
    """Tests for content scanning."""
    
    def test_find_aws_key(self):
        """AWS access key should be detected."""
        content = "aws_access_key_id = AKIAIOSFODNN7EXAMPLE"
        rules = [
            {
                "id": "aws-access-key",
                "description": "AWS Key",
                "regex": r"AKIA[0-9A-Z]{16}",
                "entropy": None
            }
        ]
        
        findings = scan_content(content, rules, "test.py")
        assert len(findings) > 0
        assert findings[0].rule_id == "aws-access-key"
    
    def test_entropy_filtering(self):
        """Low entropy matches should be filtered out."""
        content = "key = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        rules = [
            {
                "id": "test-key",
                "description": "Test",
                "regex": r"[a-z]{40}",
                "entropy": 3.0  # This will filter out the low-entropy string
            }
        ]
        
        findings = scan_content(content, rules, "test.py")
        assert len(findings) == 0  # Should be filtered by entropy
    
    def test_keyword_optimization(self):
        """Content without keywords should skip regex."""
        content = "This is just normal text"
        rules = [
            {
                "id": "api-key",
                "description": "API Key",
                "regex": r"api[_-]key",
                "keywords": ["api", "key"]
            }
        ]
        
        findings = scan_content(content, rules, "test.py")
        assert len(findings) == 0


class TestScanFile:
    """Tests for file scanning."""
    
    def test_scan_file_with_secret(self):
        """File containing secret should be detected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("api_key = 'AKIAIOSFODNN7EXAMPLE'\n")
            temp_path = Path(f.name)
        
        try:
            config = Config(
                rules=[
                    {
                        "id": "aws-key",
                        "description": "AWS",
                        "regex": r"AKIA[0-9A-Z]{16}"
                    }
                ],
                exclusions=[]
            )
            
            findings = scan_file(temp_path, config)
            assert len(findings) > 0
        finally:
            temp_path.unlink()
    
    def test_scan_excluded_file(self):
        """Excluded file should not be scanned."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("api_key = 'AKIAIOSFODNN7EXAMPLE'\n")
            temp_path = Path(f.name)
        
        try:
            config = Config(
                rules=[{"id": "aws-key", "regex": r"AKIA[0-9A-Z]{16}"}],
                exclusions=[temp_path.name]  # Exclude this specific file
            )
            
            findings = scan_file(temp_path, config)
            assert len(findings) == 0
        finally:
            temp_path.unlink()
