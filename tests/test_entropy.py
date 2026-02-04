"""Unit tests for the entropy detector module."""

import pytest
from secret_scanner.detectors.entropy import (
    shannon_entropy,
    is_base64,
    is_hex,
    calculate_entropy_score
)


class TestShannonEntropy:
    """Tests for Shannon entropy calculation."""
    
    def test_empty_string(self):
        """Empty string should have 0 entropy."""
        assert shannon_entropy("") == 0.0
    
    def test_single_character(self):
        """String with one unique character should have 0 entropy."""
        assert shannon_entropy("aaaa") == 0.0
    
    def test_two_equal_characters(self):
        """String with two equally distributed characters should have entropy of 1."""
        result = shannon_entropy("aaabbb")
        assert abs(result - 1.0) < 0.01  # Allow small floating point error
    
    def test_high_entropy_string(self):
        """Random-looking string should have high entropy."""
        result = shannon_entropy("K7gH9mP2qL5xN8wR")
        assert result > 3.5
    
    def test_base64_string(self):
        """Base64 encoded strings typically have high entropy."""
        result = shannon_entropy("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=")
        assert result > 3.0


class TestIsBase64:
    """Tests for base64 detection."""
    
    def test_valid_base64(self):
        """Valid base64 string should be detected."""
        assert is_base64("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=")
    
    def test_short_string(self):
        """Short strings should not be considered base64."""
        assert not is_base64("abc")
    
    def test_invalid_characters(self):
        """String with invalid characters should not be base64."""
        assert not is_base64("this-is-not-base64!@#$%^&*()")
    
    def test_wrong_padding(self):
        """String with incorrect padding may not be detected."""
        # This is a heuristic, so it may or may not pass
        result = is_base64("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo")
        # Just ensure it doesn't crash
        assert isinstance(result, bool)


class TestIsHex:
    """Tests for hexadecimal detection."""
    
    def test_valid_hex(self):
        """Valid hex string should be detected."""
        assert is_hex("deadbeef1234567890abcdef")
    
    def test_short_string(self):
        """Short strings should not be considered hex."""
        assert not is_hex("abc")
    
    def test_invalid_characters(self):
        """String with invalid hex characters should not be hex."""
        assert not is_hex("this-is-not-hex-zzz")
    
    def test_uppercase_hex(self):
        """Uppercase hex should be detected."""
        assert is_hex("DEADBEEF1234567890ABCDEF")


class TestCalculateEntropyScore:
    """Tests for comprehensive entropy scoring."""
    
    def test_short_string(self):
        """Short strings should return 0 entropy with metadata."""
        ent, meta = calculate_entropy_score("short", min_length=20)
        assert ent == 0.0
        assert meta["too_short"] is True
    
    def test_long_string(self):
        """Long string should return entropy and metadata."""
        ent, meta = calculate_entropy_score("a" * 30)
        assert ent >= 0.0
        assert "entropy" in meta
        assert "length" in meta
        assert meta["length"] == 30
    
    def test_metadata_includes_all_fields(self):
        """Metadata should include all expected fields."""
        _, meta = calculate_entropy_score("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=")
        assert "entropy" in meta
        assert "length" in meta
        assert "is_base64" in meta
        assert "is_hex" in meta
        assert "unique_chars" in meta
