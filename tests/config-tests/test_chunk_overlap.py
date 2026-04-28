"""
Config variation tests for chunk_overlap parameter.
Tests how different chunk_overlap values affect answer continuity.
"""
import pytest
from src.config import FarmaConfig
from tests.conftest import PARAM_TEST_MATRICES
from tests.results_logger import ResultsLogger


class TestChunkOverlap:
    logger = ResultsLogger()

    @pytest.mark.parametrize("chunk_overlap", PARAM_TEST_MATRICES["chunk_overlap"])
    def test_chunk_overlap_variation(self, rag_engine, test_queries, chunk_overlap):
        config = FarmaConfig.load()
        config.chunk_overlap = chunk_overlap
        rag_engine.config.chunk_overlap = chunk_overlap

        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])

            self.logger.log_result(
                test_name="test_chunk_overlap",
                params={"chunk_overlap": chunk_overlap, "query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "answer_preview": result[0][:200],
                    "provider_used": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']} with chunk_overlap={chunk_overlap}"
