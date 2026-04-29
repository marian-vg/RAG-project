import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import FarmaConfig
from src.unificador import FarmaRAG

TEST_QUERIES = [
    {
        "id": "faq_pami",
        "question": "¿Cuáles son las normativas vigentes de PAMI?",
        "category": "normativas",
        "expected_entity": "PAMI"
    },
    {
        "id": "faq_oser",
        "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
        "category": "recetas",
        "expected_entity": "OSER"
    },
    {
        "id": "faq_dim",
        "question": "¿Qué requisitos tienen las recetas veterinarias en DIM?",
        "category": "recetas",
        "expected_entity": "DIM"
    }
]

PARAM_TEST_MATRICES = {
    "top_k": [1, 2, 4, 8],
    "temperature": [0.0, 0.3, 0.7],
    "chunk_size": [400, 800, 1200],
    "chunk_overlap": [50, 150, 300],
    "search_type": ["similarity", "mmr"]
}


@pytest.fixture(scope="session")
def base_config():
    return FarmaConfig.load()


@pytest.fixture(scope="session")
def rag_engine(base_config):
    try:
        engine = FarmaRAG(base_config)
        return engine
    except Exception as e:
        pytest.skip(f"RAG engine could not be loaded: {e}")


@pytest.fixture(scope="function")
def temp_config(tmp_path):
    temp_config_file = tmp_path / "test_config.json"
    config = FarmaConfig()
    config.chroma_path = str(tmp_path / "chroma_test")
    yield config
    if temp_config_file.exists():
        temp_config_file.unlink()


@pytest.fixture
def test_queries():
    return TEST_QUERIES


@pytest.fixture
def param_matrices():
    return PARAM_TEST_MATRICES