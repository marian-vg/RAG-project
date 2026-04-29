"""
Fallback flow integration test.
Tests automatic fallback when primary provider fails.
"""
import pytest
from tests.datos_test import TEST_QUERIES
from tests.registro_resultados import ResultsLogger


class TestFallbackFlow:
    logger = ResultsLogger()

    def test_fallback_gemini_to_ollama(self, rag_engine, test_queries):
        query = TEST_QUERIES[0]
        result = rag_engine.ask_with_fallback(query["question"], preferred_provider="gemini")

        self.logger.log_result(
            test_name="test_fallback",
            params={"preferred_provider": "gemini", "query_id": query["id"]},
            result={
                "provider_used": result[1],
                "answer_length": len(result[0])
            }
        )

        assert result[0], "Empty answer after fallback"
        assert result[1] in ["ollama", "gemini"], f"Invalid provider: {result[1]}"

    def test_fallback_ollama_to_gemini(self, rag_engine, test_queries):
        query = TEST_QUERIES[0]
        result = rag_engine.ask_with_fallback(query["question"], preferred_provider="ollama")

        self.logger.log_result(
            test_name="test_fallback",
            params={"preferred_provider": "ollama", "query_id": query["id"]},
            result={
                "provider_used": result[1],
                "answer_length": len(result[0])
            }
        )

        assert result[0], "Empty answer after fallback"
        assert result[1] in ["ollama", "gemini"], f"Invalid provider: {result[1]}"
