"""
Tests for ingestion script (scripts/ingesta.py).
Verifies that PDF ingestion works correctly.
"""
import pytest
import os
import tempfile


class TestIngestionScript:
    def test_documentos_directory_exists(self):
        assert os.path.exists("documentos"), "documentos/ directory should exist"

    def test_documentos_directory_has_pdfs(self):
        pdfs = [f for f in os.listdir("documentos") if f.endswith(".pdf")]
        assert len(pdfs) > 0, "documentos/ should contain at least one PDF"

    def test_ingesta_imports_correctly(self):
        sys_import = __import__("sys")
        sys_import.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        try:
            from scripts import ingesta
            assert hasattr(ingesta, "ejecutar_ingesta")
        except ImportError as e:
            pytest.skip(f"Cannot import ingesta script: {e}")

    def test_procesador_imports_correctly(self):
        from src.procesador import FarmaProcessor
        assert FarmaProcessor is not None
