"""
Test de Integración Qwen para FAQs de Farmarag.

Verifica que Qwen2.5:0.5b puede responder correctamente a las 3 FAQs del sistema.
Si falla, se detiene y no hace cambios hasta planificar mejora de arquitectura.

FAQ expected content (from documents):
1. PAMI: Cobertura medicamentos esenciales, AMBA 100%, receta médica + DNI + credencial
2. OSER: Desde 2026 receta electrónica obligatoria, dos grupos (sin/con autorización)
3. DIM: Receta electrónica es el único medio válido según Circular 53
"""
import sys
import time
sys.path.insert(0, '.')

from src.unificador import FarmaRAG
from src.config import FarmaConfig


class QwenFAQTester:
    """Test suite for Qwen integration with FAQs."""

    # FAQs del sistema (de NavigationSidebar + OptionCards)
    FAQS = [
        {
            "id": "faq_pami",
            "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
            "expected_keywords": [
                "PAMI",
                "cobertura",
                "medicamentos",
                "receta",
                "crónicos",
                "ambulatorio",
            ],
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "source_doc": "Pami Ambulatorio_28_09_2022.pdf",
        },
        {
            "id": "faq_oser",
            "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
            "expected_keywords": [
                "OSER",
                "2026",
                "receta",
                "electrónica",
                "obligatorio",
                "DNI",
                "autORIZACIÓN",
            ],
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "source_doc": "OSER - Recetas electronicas 2026.pdf",
        },
        {
            "id": "faq_dim",
            "question": "¿Qué documentación necesito para gestionar una receta DIM?",
            "expected_keywords": [
                "DIM",
                "receta",
                "electrónica",
                "Circular",
                "medicamentos",
                "prescripción",
            ],
            "forbidden_phrases": [
                "no hay información suficiente",
                "no tengo información",
                "no puedo responder",
                "no tengo datos",
            ],
            "source_doc": "Circular 53 DIM - Implemetación receta digital-02ene26.pdf",
        },
    ]

    def __init__(self):
        self.config = FarmaConfig.load('config.json')
        self.rag = FarmaRAG(self.config)
        self.results = []

    def test_single_faq(self, faq, timeout=60):
        """Test a single FAQ and return detailed results."""
        print(f"\n{'='*60}")
        print(f"TEST: {faq['id']}")
        print(f"Q: {faq['question']}")
        print(f"{'='*60}")

        start_time = time.time()
        try:
            result, provider = self.rag.ask_with_fallback(faq["question"])
            elapsed = time.time() - start_time
        except Exception as e:
            return {
                "id": faq["id"],
                "success": False,
                "error": str(e),
                "elapsed": time.time() - start_time,
            }

        print(f"Provider: {provider}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Response ({len(result)} chars):")
        print(f"  {result[:300]}...")

        # Check 1: Non-empty response
        checks = {
            "not_empty": len(result.strip()) > 50,
            "no_fallback": all(fp.lower() not in result.lower() for fp in faq["forbidden_phrases"]),
        }

        # Check 2: Has expected keywords
        result_lower = result.lower()
        keyword_matches = [kw for kw in faq["expected_keywords"] if kw.lower() in result_lower]
        checks["has_keywords"] = len(keyword_matches) >= 3  # At least 3 of 6
        checks["keyword_detail"] = f"{len(keyword_matches)}/6: {keyword_matches}"

        # Check 3: Has entity mentioned
        checks["has_entity"] = faq["expected_keywords"][0].lower() in result_lower

        # Check 4: Response length reasonable
        checks["reasonable_length"] = 50 < len(result) < 2000

        all_passed = all(v if isinstance(v, bool) else True for v in checks.values())

        return {
            "id": faq["id"],
            "success": all_passed,
            "provider": provider,
            "elapsed": elapsed,
            "result": result,
            "checks": checks,
        }

    def run_all_tests(self):
        """Run all FAQ tests."""
        print("\n" + "=" * 60)
        print("QWEN INTEGRATION TESTS - FARMARAG FAQS")
        print("=" * 60)
        print(f"\nConfig: top_k={self.config.top_k}, chunk_size={self.config.chunk_size}")
        print(f"Provider: {self.config.llm_provider}, Model: {self.config.llm_model}")
        print(f"Embedding: {self.config.embedding_model}")

        passed = 0
        failed = 0

        for faq in self.FAQS:
            result = self.test_single_faq(faq)
            self.results.append(result)

            if result["success"]:
                print(f"\n  RESULT: PASS")
                for check, value in result["checks"].items():
                    if check != "keyword_detail":
                        status = "OK" if value else "FAIL"
                        print(f"    - {check}: {status}")
                print(f"    - keywords: {result['checks'].get('keyword_detail', 'N/A')}")
                passed += 1
            else:
                print(f"\n  RESULT: FAIL")
                if "error" in result:
                    print(f"    - Error: {result['error']}")
                else:
                    for check, value in result["checks"].items():
                        if check != "keyword_detail" and not value:
                            print(f"    - {check}: FAIL")
                failed += 1

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Passed: {passed}/3")
        print(f"Failed: {failed}/3")

        if failed > 0:
            print("\n[IMPORTANT] Some tests failed. DO NOT make architecture changes.")
            print("Run analysis to understand why Qwen fails before proceeding.")
            return False
        else:
            print("\n[OK] All tests passed. System is working correctly.")
            return True


if __name__ == '__main__':
    tester = QwenFAQTester()
    success = tester.run_all_tests()

    if not success:
        print("\n\nTests failed. Waiting for analysis before proceeding.")
        sys.exit(1)
    else:
        print("\n\nAll tests passed successfully!")
        sys.exit(0)