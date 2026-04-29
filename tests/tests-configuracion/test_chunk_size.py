"""
Config variation tests for chunk_size parameter.
Tests how different chunk_size values affect answer completeness.
"""
import pytest
from src.config import FarmaConfig
from tests.test_configuracion import PARAM_TEST_MATRICES
from tests.registro_resultados import ResultsLogger


class TestChunkSize:
    logger = ResultsLogger()

    @pytest.mark.parametrize("chunk_size", PARAM_TEST_MATRICES["chunk_size"])
    def test_chunk_size_variation(self, rag_engine, test_queries, chunk_size):
        config = FarmaConfig.load()
        config.chunk_size = chunk_size
        rag_engine.config.chunk_size = chunk_size

        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])

            self.logger.log_result(
                test_name="test_chunk_size",
                params={"chunk_size": chunk_size, "query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "answer_preview": result[0][:200],
                    "provider_used": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']} with chunk_size={chunk_size}"
