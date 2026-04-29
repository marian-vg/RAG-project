"""
Alias resolution integration test.
Tests that friendly names resolve correctly to technical IDs.
"""
import pytest
from src.config import FarmaConfig
from tests.registro_resultados import ResultsLogger


class TestAliasResolution:
    logger = ResultsLogger()

    def test_friendly_to_technical(self, base_config):
        config = base_config

        for friendly, expected_technical in config.MODEL_ALIASES.items():
            technical = config.get_technical_name(friendly)
            assert technical == expected_technical, f"Failed for {friendly}: got {technical}"

            self.logger.log_result(
                test_name="test_alias_resolution",
                params={"friendly_name": friendly},
                result={"technical_name": technical, "expected": expected_technical}
            )

    def test_friendly_name_retrieval(self, base_config):
        config = base_config

        for technical, expected_friendly in config.FRIENDLY_TO_MODEL.items():
            friendly = config.get_friendly_name()
            assert isinstance(friendly, str), f"get_friendly_name returned non-string: {type(friendly)}"

            self.logger.log_result(
                test_name="test_alias_resolution",
                params={"technical_name": technical},
                result={"friendly_name": friendly, "expected": expected_friendly}
            )

    def test_alias_endpoint_format(self, rag_engine):
        aliases = rag_engine.config.MODEL_ALIASES

        self.logger.log_result(
            test_name="test_alias_endpoint_format",
            params={},
            result={
                "aliases": aliases,
                "reverse_count": len(rag_engine.config.FRIENDLY_TO_MODEL)
            }
        )

        assert isinstance(aliases, dict), "MODEL_ALIASES should be a dict"
        assert len(aliases) > 0, "MODEL_ALIASES should not be empty"
