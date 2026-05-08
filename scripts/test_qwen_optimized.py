"""
Optimized Qwen integration test - loads embeddings once for all 3 FAQs.
"""
import sys
import time
sys.path.insert(0, '.')

from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import FarmaConfig


def run_all_faqs():
    config = FarmaConfig.load('config.json')

    print("=" * 60)
    print("QWEN INTEGRATION TEST (OPTIMIZED)")
    print("=" * 60)
    print(f"Config: top_k={config.top_k}, chunk_size={config.chunk_size}")
    print(f"Threshold: {config.score_threshold}")

    # Load embeddings ONCE
    print("\n[*] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=config.embedding_model,
        encode_kwargs={"normalize_embeddings": True}
    )

    # Create vectorstore ONCE
    print("[*] Loading vectorstore...")
    vs = Chroma(
        persist_directory=config.chroma_path,
        embedding_function=embeddings,
        collection_name=config.collection_name,
        collection_metadata={"hnsw:space": "cosine"}
    )

    # Create LLM ONCE
    print("[*] Loading Qwen (qwen2.5:0.5b)...")
    llm = ChatOllama(
        model="qwen2.5:0.5b",
        temperature=0.0,
        timeout=60
    )

    # Define FAQs
    faqs = [
        {
            "id": "faq_pami",
            "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
            "expected_keywords": ["PAMI", "cobertura", "medicamentos", "receta", "crónicos", "ambulatorio"],
        },
        {
            "id": "faq_oser",
            "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
            "expected_keywords": ["OSER", "2026", "receta", "electrónica", "obligatorio", "DNI"],
        },
        {
            "id": "faq_dim",
            "question": "¿Qué documentación necesito para gestionar una receta DIM?",
            "expected_keywords": ["DIM", "receta", "electrónica", "Circular", "medicamentos", "prescripción"],
        },
    ]

    passed = 0
    failed = 0

    for i, faq in enumerate(faqs):
        print(f"\n{'='*60}")
        print(f"FAQ {i+1}/3: {faq['id']}")
        print(f"Q: {faq['question']}")
        print(f"{'='*60}")

        try:
            # Retrieve
            start = time.time()
            docs_and_scores = vs.similarity_search_with_relevance_scores(
                faq["question"], k=config.top_k
            )
            retrieval_time = time.time() - start

            print(f"  Retrieved {len(docs_and_scores)} docs in {retrieval_time:.1f}s")
            if docs_and_scores:
                top_score = max(score for _, score in docs_and_scores)
                top_entity = docs_and_scores[0][0].metadata.get('entidad', '?')
                print(f"  Top score: {top_score:.4f} | Entity: {top_entity}")

            if not docs_and_scores:
                print("  FAIL: No docs retrieved")
                failed += 1
                continue

            # Format context
            context_parts = []
            for doc, score in docs_and_scores:
                src = doc.metadata.get('source', '?')
                ent = doc.metadata.get('entidad', '?')
                context_parts.append(f"--- {src} ({ent}) ---\n{doc.page_content}")

            context = "\n\n".join(context_parts)

            # Build prompt
            prompt = f"""Eres un asistente de auditoría farmacéutica.
Contexto: {context}
Pregunta: {faq['question']}
Responde con UNA o DOS oraciones. Si no hay info, dice 'No hay información suficiente'.
Respuesta:"""

            # Call Qwen
            print("  Calling Qwen...")
            start = time.time()
            result = llm.invoke(prompt)
            llm_time = time.time() - start

            result_text = result.content if hasattr(result, 'content') else str(result)
            print(f"  Response ({len(result_text)} chars, {llm_time:.1f}s):")
            print(f"  {result_text[:250]}...")

            # Verify
            result_lower = result_text.lower()

            # Check fallback
            if "no hay información suficiente" in result_lower:
                print("  FAIL: Model returned fallback")
                failed += 1
                continue

            # Check keywords
            matches = [kw for kw in faq["expected_keywords"] if kw.lower() in result_lower]
            print(f"  Keywords: {len(matches)}/{len(faq['expected_keywords'])} -> {matches}")

            if len(matches) < 3:
                print("  FAIL: Not enough keywords matched")
                failed += 1
                continue

            print("  PASS")
            passed += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Passed: {passed}/3")
    print(f"Failed: {failed}/3")

    if failed > 0:
        print("\n[WARNING] Some tests failed.")
        return False
    else:
        print("\n[OK] All tests passed!")
        return True


if __name__ == '__main__':
    ok = run_all_faqs()
    sys.exit(0 if ok else 1)