"""
Config variation tests for top_k parameter.
Tests how different top_k values affect retrieval relevance.
"""
import pytest
from src.config import FarmaConfig
from tests.conftest import PARAM_TEST_MATRICES
from tests.results_logger import ResultsLogger


class TestTopK:
    logger = ResultsLogger()

    @pytest.mark.parametrize("top_k", PARAM_TEST_MATRICES["top_k"])
    def test_top_k_variation(self, rag_engine, test_queries, top_k):
        config = FarmaConfig.load()
        config.top_k = top_k
        rag_engine.config.top_k = top_k

        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])

            self.logger.log_result(
                test_name="test_top_k",
                params={"top_k": top_k, "query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "answer_preview": result[0][:200],
                    "provider_used": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']} with top_k={top_k}"
