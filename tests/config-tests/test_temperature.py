"""
Config variation tests for temperature parameter.
Tests how different temperature values affect response determinism.
"""
import pytest
from src.config import FarmaConfig
from tests.conftest import PARAM_TEST_MATRICES
from tests.results_logger import ResultsLogger


class TestTemperature:
    logger = ResultsLogger()

    @pytest.mark.parametrize("temperature", PARAM_TEST_MATRICES["temperature"])
    def test_temperature_variation(self, rag_engine, test_queries, temperature):
        config = FarmaConfig.load()
        config.temperature = temperature
        rag_engine.config.temperature = temperature

        answers = []
        for query in test_queries:
            result = rag_engine.ask_with_fallback(query["question"])
            answers.append(result[0])

            self.logger.log_result(
                test_name="test_temperature",
                params={"temperature": temperature, "query_id": query["id"]},
                result={
                    "answer_length": len(result[0]),
                    "answer_preview": result[0][:200],
                    "provider_used": result[1]
                }
            )

            assert result[0], f"Empty answer for query {query['id']} with temperature={temperature}"

        if temperature == 0.0:
            for i in range(len(answers)):
                for j in range(i + 1, len(answers)):
                    if answers[i] == answers[j]:
                        print(f"Identical answers at temperature={temperature}: queries {i} and {j}")
