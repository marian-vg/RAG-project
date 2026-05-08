"""
FAQ Retrieval Verification Tests.

Tests that the 3 main FAQ queries return relevant, non-empty responses
without falling back to "No hay información suficiente".

Verifies:
1. PAMI query returns coverage/medication related information
2. OSER query returns 2026 electronic prescription information
3. DIM query returns veterinary prescription requirements
"""
import pytest
from tests.datos_test import TEST_QUERIES


class TestFAQRetrieval:
    """Test suite for FAQ query verification."""

    FAQ_TESTS = [
        {
            "id": "faq_pami",
            "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
            "expected_entity": "PAMI",
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "expected_keywords": ["PAMI", "cobertura", "medicamentos", "vademécum"],
        },
        {
            "id": "faq_oser",
            "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
            "expected_entity": "OSER",
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "expected_keywords": ["OSER", "2026", "receta", "electrónica", "papel"],
        },
        {
            "id": "faq_dim",
            "question": "¿Qué documentación necesito para gestionar una receta DIM?",
            "expected_entity": "DIM",
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "expected_keywords": ["DIM", "receta", "documentación", "requisitos"],
        },
    ]

    def test_faq_responses_not_empty(self, rag_engine):
        """Verify that all FAQ queries return non-empty responses."""
        for faq in self.FAQ_TESTS:
            result, provider = rag_engine.ask_with_fallback(faq["question"])
            assert result and len(result.strip()) > 0, (
                f"Empty response for FAQ {faq['id']}: {faq['question']}"
            )

    def test_faq_responses_no_no_info_fallback(self, rag_engine):
        """Verify that no FAQ query returns 'No hay información suficiente'."""
        for faq in self.FAQ_TESTS:
            result, provider = rag_engine.ask_with_fallback(faq["question"])
            result_lower = result.lower()
            for forbidden in faq["forbidden_phrases"]:
                assert forbidden.lower() not in result_lower, (
                    f"FAQ {faq['id']} returned forbidden phrase '{forbidden}'. "
                    f"Full response: {result[:200]}..."
                )

    def test_faq_pami_returns_relevant_info(self, rag_engine):
        """Test PAMI query returns coverage/medication information."""
        faq = self.FAQ_TESTS[0]
        result, provider = rag_engine.ask_with_fallback(faq["question"])

        result_lower = result.lower()
        has_keyword = any(kw.lower() in result_lower for kw in faq["expected_keywords"])
        assert has_keyword, (
            f"PAMI query missing keywords {faq['expected_keywords']}. "
            f"Response: {result[:300]}..."
        )

    def test_faq_oser_returns_relevant_info(self, rag_engine):
        """Test OSER query returns 2026 electronic prescription information."""
        faq = self.FAQ_TESTS[1]
        result, provider = rag_engine.ask_with_fallback(faq["question"])

        result_lower = result.lower()
        has_keyword = any(kw.lower() in result_lower for kw in faq["expected_keywords"])
        assert has_keyword, (
            f"OSER query missing keywords {faq['expected_keywords']}. "
            f"Response: {result[:300]}..."
        )

    def test_faq_dim_returns_relevant_info(self, rag_engine):
        """Test DIM query returns documentation/requirements information."""
        faq = self.FAQ_TESTS[2]
        result, provider = rag_engine.ask_with_fallback(faq["question"])

        result_lower = result.lower()
        has_keyword = any(kw.lower() in result_lower for kw in faq["expected_keywords"])
        assert has_keyword, (
            f"DIM query missing keywords {faq['expected_keywords']}. "
            f"Response: {result[:300]}..."
        )

    def test_all_faqs_pass_together(self, rag_engine):
        """Comprehensive test that all 3 FAQs pass all checks."""
        results = {}
        for faq in self.FAQ_TESTS:
            result, provider = rag_engine.ask_with_fallback(faq["question"])
            result_lower = result.lower()

            checks = {
                "not_empty": len(result.strip()) > 0,
                "no_fallback": all(fp.lower() not in result_lower for fp in faq["forbidden_phrases"]),
                "has_entity": faq["expected_entity"].lower() in result_lower,
                "has_keywords": any(kw.lower() in result_lower for kw in faq["expected_keywords"]),
            }
            results[faq["id"]] = {"result": result, "provider": provider, "checks": checks}

        failed = []
        for faq_id, data in results.items():
            for check_name, passed in data["checks"].items():
                if not passed:
                    failed.append(f"{faq_id}.{check_name}")

        assert len(failed) == 0, f"Failed checks: {failed}"

        print(f"\n✓ All 3 FAQ tests passed")
        for faq_id, data in results.items():
            print(f"  - {faq_id}: {data['provider']} | {len(data['result'])} chars")