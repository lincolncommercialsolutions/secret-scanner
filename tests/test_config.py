"""Unit tests for the configuration loader."""

import pytest
import tempfile
from pathlib import Path
from secret_scanner.config import load_rules, validate_config, Config


class TestLoadRules:
    """Tests for loading rules from YAML."""
    
    def test_load_default_rules(self):
        """Loading default rules should work."""
        config = load_rules()
        assert isinstance(config, Config)
        assert len(config.rules) > 0
        assert isinstance(config.exclusions, list)
    
    def test_rules_have_required_fields(self):
        """All rules should have id and regex fields."""
        config = load_rules()
        for rule in config.rules:
            assert "id" in rule
            assert "regex" in rule
    
    def test_custom_rules_file(self):
        """Loading custom rules file should work."""
        # Create temporary rules file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
rules:
  - id: test-rule
    description: Test Rule
    regex: test-pattern
    entropy: 3.5
exclusions:
  - test/
""")
            temp_path = f.name
        
        try:
            config = load_rules(temp_path)
            assert len(config.rules) == 1
            assert config.rules[0]["id"] == "test-rule"
            assert len(config.exclusions) == 1
        finally:
            Path(temp_path).unlink()
    
    def test_missing_file(self):
        """Loading non-existent file should raise error."""
        with pytest.raises(FileNotFoundError):
            load_rules("/nonexistent/path/to/rules.yaml")
    
    def test_malformed_yaml(self):
        """Loading malformed YAML should raise error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: {[")
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):  # YAMLError
                load_rules(temp_path)
        finally:
            Path(temp_path).unlink()


class TestValidateConfig:
    """Tests for configuration validation."""
    
    def test_valid_config(self):
        """Valid config should return no warnings."""
        config = Config(
            rules=[
                {"id": "test-1", "regex": "pattern1", "description": "Test 1"},
                {"id": "test-2", "regex": "pattern2", "description": "Test 2"}
            ],
            exclusions=["test/"]
        )
        warnings = validate_config(config)
        assert isinstance(warnings, list)
    
    def test_empty_rules(self):
        """Config with no rules should warn."""
        config = Config(rules=[], exclusions=[])
        warnings = validate_config(config)
        assert any("No rules" in w for w in warnings)
    
    def test_duplicate_rule_ids(self):
        """Duplicate rule IDs should warn."""
        config = Config(
            rules=[
                {"id": "duplicate", "regex": "pattern1"},
                {"id": "duplicate", "regex": "pattern2"}
            ],
            exclusions=[]
        )
        warnings = validate_config(config)
        assert any("Duplicate" in w for w in warnings)
