"""Configuration loader for secret scanner rules."""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


class Config:
    """Configuration container for scanner rules and settings."""
    
    def __init__(self, rules: List[Dict[str, Any]], exclusions: List[str]):
        self.rules = rules
        self.exclusions = exclusions
    
    def __repr__(self):
        return f"Config(rules={len(self.rules)}, exclusions={len(self.exclusions)})"


def load_rules(rules_path: Optional[str] = None) -> Config:
    """
    Load scanning rules from a YAML file.
    
    Args:
        rules_path: Path to custom rules file. If None, uses default rules.
        
    Returns:
        Config object containing rules and exclusions
        
    Raises:
        FileNotFoundError: If rules file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if rules_path is None:
        # Use default rules from config directory
        rules_path = Path(__file__).parent.parent.parent / "config" / "default_rules.yaml"
    else:
        rules_path = Path(rules_path)
    
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    rules = data.get('rules', [])
    exclusions = data.get('exclusions', [])
    
    # Validate rules structure
    for idx, rule in enumerate(rules):
        if 'id' not in rule:
            raise ValueError(f"Rule at index {idx} missing required 'id' field")
        if 'regex' not in rule:
            raise ValueError(f"Rule '{rule.get('id')}' missing required 'regex' field")
        if 'description' not in rule:
            rule['description'] = rule['id']  # Default to ID if no description
    
    return Config(rules=rules, exclusions=exclusions)


def get_default_config() -> Config:
    """
    Get the default configuration.
    
    Returns:
        Config object with default rules
    """
    return load_rules()


def validate_config(config: Config) -> List[str]:
    """
    Validate configuration and return list of warnings.
    
    Args:
        config: Config object to validate
        
    Returns:
        List of warning messages (empty if valid)
    """
    warnings = []
    
    if not config.rules:
        warnings.append("No rules defined in configuration")
    
    # Check for duplicate rule IDs
    rule_ids = [r['id'] for r in config.rules]
    duplicates = set([x for x in rule_ids if rule_ids.count(x) > 1])
    if duplicates:
        warnings.append(f"Duplicate rule IDs found: {', '.join(duplicates)}")
    
    # Check for rules with both null entropy and no keywords
    for rule in config.rules:
        if rule.get('entropy') is None and not rule.get('keywords'):
            if 'generic' in rule['id'] or 'password' in rule['id']:
                warnings.append(
                    f"Rule '{rule['id']}' has no entropy threshold or keywords "
                    "(may produce many false positives)"
                )
    
    return warnings
