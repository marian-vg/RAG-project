"""
Unit tests for input sanitization.
Tests prompt injection prevention.
"""
import pytest
from server import sanitize_input


class TestSanitizeInput:
    def test_removes_script_tags(self):
        malicious = "<script>alert('xss')</script>Hello"
        result = sanitize_input(malicious)
        assert "<script>" not in result
        assert "alert" not in result

    def test_removes_javascript_protocol(self):
        malicious = "javascript:alert('xss')"
        result = sanitize_input(malicious)
        assert "javascript:" not in result.lower()

    def test_removes_event_handlers(self):
        malicious = '<img src=x onerror="alert(1)">'
        result = sanitize_input(malicious)
        assert "onerror" not in result.lower()

    def test_removes_control_characters(self):
        malicious = "Hello\x00\x08\x1fWorld"
        result = sanitize_input(malicious)
        assert "\x00" not in result
        assert "\x08" not in result

    def test_preserves_normal_text(self):
        normal = "¿Cuáles son las normativas de PAMI?"
        result = sanitize_input(normal)
        assert result == normal

    def test_trims_whitespace(self):
        text = "  ¿Hola?  "
        result = sanitize_input(text)
        assert result == "¿Hola?"

    def test_truncates_long_input(self):
        long_text = "A" * 2000
        result = sanitize_input(long_text)
        assert len(result) == 1000

    def test_empty_string(self):
        result = sanitize_input("")
        assert result == ""

    def test_none_input(self):
        result = sanitize_input(None)
        assert result == ""
