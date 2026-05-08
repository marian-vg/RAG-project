"""
FAQ Retrieval Verification Tests - Fast version.
Tests retrieval scores without calling the LLM.

Verifies:
1. PAMI query returns chunks above threshold with correct entity
2. OSER query returns chunks above threshold with correct entity
3. DIM query returns chunks above threshold with correct entity
"""
import sys
sys.path.insert(0, '.')

from src.config import FarmaConfig
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class TestFAQRetrievalFast:
    """Test suite for FAQ query verification using retrieval scores only."""

    FAQ_QUERIES = [
        {
            "id": "faq_pami",
            "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
            "expected_entity": "PAMI",
        },
        {
            "id": "faq_oser",
            "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
            "expected_entity": "OSER",
        },
        {
            "id": "faq_dim",
            "question": "¿Qué documentación necesito para gestionar una receta DIM?",
            "expected_entity": "DIM",
        },
    ]

    @classmethod
    def setup_class(cls):
        """Setup vectorstore once for all tests."""
        config = FarmaConfig.load('config.json')
        cls.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
            encode_kwargs={'normalize_embeddings': True}
        )
        cls.vectorstore = Chroma(
            persist_directory=config.chroma_path,
            embedding_function=cls.embeddings,
            collection_name=config.collection_name,
            collection_metadata={'hnsw:space': 'cosine'}
        )
        cls.threshold = config.score_threshold

    def test_retrieval_pami(self):
        """Test PAMI query returns above-threshold chunks with PAMI entity."""
        faq = self.FAQ_QUERIES[0]
        results = self.vectorstore.similarity_search_with_relevance_scores(faq["question"], k=3)

        assert len(results) > 0, f"No results for {faq['id']}"

        scores = [score for _, score in results]
        top_score = max(scores)
        top_doc = results[0][0]

        print(f"\nPAMI query results:")
        print(f"  Top score: {top_score:.4f} (threshold: {self.threshold})")
        print(f"  Top entity: {top_doc.metadata.get('entidad', '?')}")

        assert top_score >= self.threshold, f"Top score {top_score:.4f} below threshold {self.threshold}"
        assert top_doc.metadata.get('entidad') == faq['expected_entity'], (
            f"Expected entity {faq['expected_entity']}, got {top_doc.metadata.get('entidad')}"
        )

    def test_retrieval_oser(self):
        """Test OSER query returns above-threshold chunks with OSER entity."""
        faq = self.FAQ_QUERIES[1]
        results = self.vectorstore.similarity_search_with_relevance_scores(faq["question"], k=3)

        assert len(results) > 0, f"No results for {faq['id']}"

        scores = [score for _, score in results]
        top_score = max(scores)
        oser_docs = [doc for doc, score in results if doc.metadata.get('entidad') == 'OSER']
        has_oser = len(oser_docs) > 0

        print(f"\nOSER query results:")
        print(f"  Top score: {top_score:.4f} (threshold: {self.threshold})")
        print(f"  OSER docs found: {len(oser_docs)}")
        print(f"  Top entity: {results[0][0].metadata.get('entidad', '?')}")

        assert top_score >= self.threshold, f"Top score {top_score:.4f} below threshold {self.threshold}"
        assert has_oser, f"No OSER documents retrieved (threshold: {self.threshold}, top: {top_score:.4f})"

    def test_retrieval_dim(self):
        """Test DIM query returns above-threshold chunks with DIM entity."""
        faq = self.FAQ_QUERIES[2]
        results = self.vectorstore.similarity_search_with_relevance_scores(faq["question"], k=3)

        assert len(results) > 0, f"No results for {faq['id']}"

        scores = [score for _, score in results]
        top_score = max(scores)
        top_doc = results[0][0]

        print(f"\nDIM query results:")
        print(f"  Top score: {top_score:.4f} (threshold: {self.threshold})")
        print(f"  Top entity: {top_doc.metadata.get('entidad', '?')}")

        assert top_score >= self.threshold, f"Top score {top_score:.4f} below threshold {self.threshold}"
        assert top_doc.metadata.get('entidad') == faq['expected_entity'], (
            f"Expected entity {faq['expected_entity']}, got {top_doc.metadata.get('entidad')}"
        )

    def test_all_faqs_retrievable(self):
        """Comprehensive test that all 3 FAQs can be retrieved above threshold."""
        print(f"\n=== All FAQs retrieval test (threshold: {self.threshold}) ===")
        results_summary = {}

        for faq in self.FAQ_QUERIES:
            results = self.vectorstore.similarity_search_with_relevance_scores(faq["question"], k=3)

            above_threshold = [(doc, score) for doc, score in results if score >= self.threshold]
            entities_found = set(doc.metadata.get('entidad') for doc, _ in results)

            results_summary[faq['id']] = {
                'top_score': max(score for _, score in results) if results else 0,
                'above_threshold_count': len(above_threshold),
                'entities': entities_found,
            }

            print(f"\n  {faq['id']}: top_score={results_summary[faq['id']]['top_score']:.4f}, "
                  f"above_thresh={len(above_threshold)}, entities={entities_found}")

        all_pass = all(
            results_summary[faq['id']]['top_score'] >= self.threshold
            for faq in self.FAQ_QUERIES
        )
        assert all_pass, f"Some FAQs below threshold: {results_summary}"


if __name__ == '__main__':
    TestFAQRetrievalFast.setup_class()

    print("=" * 60)
    print("FAQ RETRIEVAL TESTS (Fast - No LLM calls)")
    print("=" * 60)

    tester = TestFAQRetrievalFast()

    tests = [
        ('PAMI retrieval', tester.test_retrieval_pami),
        ('OSER retrieval', tester.test_retrieval_oser),
        ('DIM retrieval', tester.test_retrieval_dim),
        ('All FAQs pass', tester.test_all_faqs_retrievable),
    ]

    for name, test_fn in tests:
        try:
            test_fn()
            print(f"\n  PASS: {name}")
        except AssertionError as e:
            print(f"\n  FAIL: {name} - {e}")
        except Exception as e:
            print(f"\n  ERROR: {name} - {e}")