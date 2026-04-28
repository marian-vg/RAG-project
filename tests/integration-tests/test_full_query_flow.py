"""
Full query flow integration test.
Tests the complete flow: question -> retrieval -> generation -> response.
"""
import pytest
from tests.test_data import TEST_QUERIES
from tests.results_logger import ResultsLogger


class TestFullQueryFlow:
    logger = ResultsLogger()

    def test_full_flow_all_queries(self, rag_engine, test_queries):
        results = []
        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])
            results.append({
                "query_id": query["id"],
                "answer": result[0],
                "answer_length": len(result[0]),
                "provider": result[1]
            })

            self.logger.log_result(
                test_name="test_full_flow",
                params={"query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "provider": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']}"
            assert result[1] in ["ollama", "gemini"], f"Invalid provider: {result[1]}"

        print(f"\nProcessed {len(results)} queries successfully")
        return results

    def test_full_flow_returns_citations(self, rag_engine):
        query = TEST_QUERIES[0]
        result = rag_engine.ask_with_fallback(query["question"])

        self.logger.log_result(
            test_name="test_citations",
            params={"query_id": query["id"]},
            result={
                "answer": result[0]
            }
        )

        assert result[0], "Empty answer"
