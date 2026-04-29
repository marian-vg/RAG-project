"""
Unit tests for model alias mappings.
Tests forward and reverse alias resolution.
"""
import pytest
from src.config import FarmaConfig


class TestModelAliases:
    def test_forward_mapping_count(self):
        config = FarmaConfig()
        assert len(config.MODEL_ALIASES) >= 2

    def test_forward_mapping_values_are_strings(self):
        config = FarmaConfig()
        for friendly, technical in config.MODEL_ALIASES.items():
            assert isinstance(friendly, str)
            assert isinstance(technical, str)
            assert len(technical) > 0

    def test_reverse_mapping_is_complete(self):
        config = FarmaConfig()
        reverse = config.FRIENDLY_TO_MODEL
        for technical, friendly in reverse.items():
            assert config.MODEL_ALIASES.get(friendly) == technical

    def test_qwen_alias(self):
        config = FarmaConfig()
        assert config.MODEL_ALIASES.get("Qwen 2.5") == "qwen2.5:0.5b"
        assert config.FRIENDLY_TO_MODEL.get("qwen2.5:0.5b") == "Qwen 2.5"

    def test_gemini_alias(self):
        config = FarmaConfig()
        assert config.MODEL_ALIASES.get("Gemini 3.1") == "models/gemini-3.1-flash-lite-preview"
