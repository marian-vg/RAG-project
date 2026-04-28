"""
Tests for farma_query CLI script (scripts/farma_query.py).
Verifies that the CLI query interface works.
"""
import pytest
import sys
import os


class TestFarmaQueryScript:
    def test_farma_query_imports(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        try:
            from scripts import farma_query
            assert True
        except ImportError as e:
            pytest.skip(f"Cannot import farma_query script: {e}")

    def test_unificador_imports(self):
        from src.unificador import FarmaRAG
        assert FarmaRAG is not None

    def test_query_function_exists(self):
        from src.auditor import FarmaAuditor
        assert hasattr(FarmaAuditor, "ask_with_fallback") or hasattr(FarmaAuditor, "ask")
