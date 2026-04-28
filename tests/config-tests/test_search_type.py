"""
Config variation tests for search_type parameter.
Tests similarity vs mmr (maximal marginal relevance) search strategies.
"""
import pytest
from src.config import FarmaConfig
from tests.conftest import PARAM_TEST_MATRICES
from tests.results_logger import ResultsLogger


class TestSearchType:
    logger = ResultsLogger()

    @pytest.mark.parametrize("search_type", PARAM_TEST_MATRICES["search_type"])
    def test_search_type_variation(self, rag_engine, test_queries, search_type):
        config = FarmaConfig.load()
        config.search_type = search_type
        rag_engine.config.search_type = search_type

        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])

            self.logger.log_result(
                test_name="test_search_type",
                params={"search_type": search_type, "query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "answer_preview": result[0][:200],
                    "provider_used": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']} with search_type={search_type}"
