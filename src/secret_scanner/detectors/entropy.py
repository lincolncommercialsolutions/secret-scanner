"""Entropy detection module for identifying high-entropy strings."""

import math
from collections import Counter


def shannon_entropy(data: str) -> float:
    """
    Calculate Shannon entropy in bits per character.
    
    Args:
        data: The string to analyze
        
    Returns:
        Float representing entropy (higher = more random/complex)
        
    Example:
        >>> shannon_entropy("aaaa")
        0.0
        >>> shannon_entropy("abcd")
        2.0
    """
    if not data:
        return 0.0
    
    entropy = 0.0
    length = len(data)
    freq = Counter(data)
    
    for count in freq.values():
        p_x = count / length
        entropy += -p_x * math.log2(p_x)
    
    return entropy


def is_base64(text: str) -> bool:
    """
    Check if a string looks like base64 encoding.
    
    Args:
        text: String to check
        
    Returns:
        True if string appears to be base64 encoded
    """
    if len(text) < 16:
        return False
    
    # Base64 uses A-Za-z0-9+/= characters
    base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    char_set = set(text)
    
    # Check if at least 95% of characters are valid base64
    valid_chars = sum(1 for c in text if c in base64_chars)
    ratio = valid_chars / len(text)
    
    # Base64 strings are typically divisible by 4 (with padding)
    length_check = len(text) % 4 == 0
    
    return ratio >= 0.95 and length_check


def is_hex(text: str) -> bool:
    """
    Check if a string is hexadecimal.
    
    Args:
        text: String to check
        
    Returns:
        True if string is valid hex
    """
    if len(text) < 16:
        return False
    
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


def calculate_entropy_score(text: str, min_length: int = 20) -> tuple[float, dict]:
    """
    Calculate comprehensive entropy metrics for a string.
    
    Args:
        text: String to analyze
        min_length: Minimum length to consider for analysis
        
    Returns:
        Tuple of (entropy_value, metadata_dict)
    """
    if len(text) < min_length:
        return 0.0, {"too_short": True}
    
    ent = shannon_entropy(text)
    
    metadata = {
        "entropy": round(ent, 2),
        "length": len(text),
        "is_base64": is_base64(text),
        "is_hex": is_hex(text),
        "unique_chars": len(set(text))
    }
    
    return ent, metadata
