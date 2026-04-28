"""
Unit tests for FarmaConfig Pydantic model.
Tests config validation, save/load, and alias methods.
"""
import pytest
import tempfile
import os
from src.config import FarmaConfig


class TestFarmaConfig:
    def test_default_values(self):
        config = FarmaConfig()
        assert config.chunk_size == 800
        assert config.chunk_overlap == 150
        assert config.top_k == 4
        assert config.temperature == 0.0
        assert config.search_type == "similarity"

    def test_model_aliases_structure(self):
        config = FarmaConfig()
        assert isinstance(config.MODEL_ALIASES, dict)
        assert "Qwen 2.5" in config.MODEL_ALIASES
        assert "Gemini 3.1" in config.MODEL_ALIASES

    def test_get_friendly_name(self):
        config = FarmaConfig()
        config.llm_model = config.MODEL_ALIASES["Qwen 2.5"]
        assert config.get_friendly_name() == "Qwen 2.5"

        config.llm_model = config.MODEL_ALIASES["Gemini 3.1"]
        assert config.get_friendly_name() == "Gemini 3.1"

    def test_get_friendly_name_unknown_model(self):
        config = FarmaConfig()
        config.llm_model = "unknown_model"
        assert config.get_friendly_name() == "unknown_model"

    def test_get_technical_name(self):
        config = FarmaConfig()
        assert config.get_technical_name("Qwen 2.5") == "qwen2.5:0.5b"
        assert config.get_technical_name("Gemini 3.1") == "models/gemini-3.1-flash-lite-preview"

    def test_get_technical_name_unknown(self):
        config = FarmaConfig()
        result = config.get_technical_name("Unknown Model")
        assert result == "Unknown Model"

    def test_save_and_load(self, tmp_path):
        config = FarmaConfig()
        config.chunk_size = 1200
        config.top_k = 8

        config_path = tmp_path / "test_config.json"
        config.save(str(config_path))

        loaded = FarmaConfig.load(str(config_path))
        assert loaded.chunk_size == 1200
        assert loaded.top_k == 8

    def test_friendly_to_model_property(self):
        config = FarmaConfig()
        reverse = config.FRIENDLY_TO_MODEL
        assert isinstance(reverse, dict)
        assert reverse["qwen2.5:0.5b"] == "Qwen 2.5"
        assert reverse["models/gemini-3.1-flash-lite-preview"] == "Gemini 3.1"
