"""
Test data for FarmaRAG testing.
Modify these queries to adjust test behavior.
"""

TEST_QUERIES = [
    {
        "id": "faq_pami",
        "question": "¿Cuáles son las normativas vigentes de PAMI?",
        "label": "Normativas PAMI",
        "category": "normativas",
        "icon": "file",
        "expected_entity": "PAMI"
    },
    {
        "id": "faq_oser",
        "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
        "label": "Decreto OSER",
        "category": "recetas",
        "icon": "alert",
        "expected_entity": "OSER"
    },
    {
        "id": "faq_dim",
        "question": "¿Qué requisitos tienen las recetas veterinarias en DIM?",
        "label": "Recetas DIM",
        "category": "recetas",
        "icon": "help",
        "expected_entity": "DIM"
    }
]

SYNTHETIC_QUERIES = [
    {
        "id": "synth_drug_interaction",
        "question": "¿Interacciona el ibuprofeno con el alcohol?",
        "category": "interacciones",
        "expected_keywords": ["ibuprofeno", "alcohol"]
    },
    {
        "id": "synth_prescription_validation",
        "question": "¿Cómo valido una receta de obras social?",
        "category": "validacion",
        "expected_keywords": ["receta", "obra social", "validar"]
    }
]

ALL_QUERIES = TEST_QUERIES + SYNTHETIC_QUERIES
