"""
Tests estadisticos - Preguntas de borde/límite con set_1
Parámetros: chunk_size=1400, chunk_overlap=400, top_k=6
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from src.config import FarmaConfig
from src.unificador import FarmaRAG
from tests.tests_estadisticos.preguntas_borde import PREGUNTAS_BORDE
from tests.registro_resultados import ResultsLogger


class TestBordeSet1:
    logger = ResultsLogger()
    SET_PARAMS = {"set": 1, "chunk_size": 1400, "chunk_overlap": 400, "top_k": 6}

    @pytest.fixture(scope="class")
    def config_mod(self):
        config = FarmaConfig.load()
        config.chunk_size = 1400
        config.chunk_overlap = 400
        config.top_k = 6
        return config

    @pytest.fixture(scope="class")
    def rag_engine_set1(self, config_mod):
        try:
            rag = FarmaRAG(config_mod)
            rag.auditor.vectorstore
            return rag
        except Exception as e:
            pytest.skip(f"No se pudo cargar RAG: {e}")

    @pytest.mark.parametrize("pregunta_data", PREGUNTAS_BORDE)
    def test_pregunta_borde(self, rag_engine_set1, pregunta_data):
        pregunta = pregunta_data["pregunta"]
        pregunta_id = pregunta_data["id"]

        result, provider, sources = rag_engine_set1.ask_with_sources(pregunta)

        self.logger.log_result(
            test_name="test_borde_set_1",
            params={**self.SET_PARAMS, "pregunta_id": pregunta_id, "pregunta": pregunta},
            result={
                "respuesta": result,
                "answer_length": len(result),
                "provider": provider,
                "source_documents": sources
            }
        )

        assert result and len(result.strip()) > 0, f"Respuesta vacia para {pregunta_id}"