"""
Quick Qwen test - single FAQ direct call with Ollama.
"""
import sys
import time
sys.path.insert(0, '.')

from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import FarmaConfig


def test_faq_with_ollama(question, expected_keywords, threshold=0.40):
    """Test a single FAQ using Ollama directly."""
    config = FarmaConfig.load('config.json')

    print(f"\n  Query: {question}")

    # Setup vectorstore
    embeddings = HuggingFaceEmbeddings(
        model_name=config.embedding_model,
        encode_kwargs={"normalize_embeddings": True}
    )
    vs = Chroma(
        persist_directory=config.chroma_path,
        embedding_function=embeddings,
        collection_name=config.collection_name,
        collection_metadata={"hnsw:space": "cosine"}
    )

    # Retrieval
    print(f"  Retrieving (top_k={config.top_k}, threshold={threshold})...")
    docs_and_scores = vs.similarity_search_with_relevance_scores(question, k=config.top_k)
    print(f"  Retrieved {len(docs_and_scores)} docs")

    if not docs_and_scores:
        print("  FAIL: No docs retrieved")
        return False

    top_score = max(score for _, score in docs_and_scores)
    print(f"  Top score: {top_score:.4f}")

    # Format context
    context_parts = []
    for doc, score in docs_and_scores:
        src = doc.metadata.get('source', '?')
        ent = doc.metadata.get('entidad', '?')
        context_parts.append(f"--- {src} ({ent}) ---\n{doc.page_content}")

    context = "\n\n".join(context_parts)

    # Call Qwen directly
    print(f"  Calling Ollama (qwen2.5:0.5b)...")
    llm = ChatOllama(
        model="qwen2.5:0.5b",
        temperature=0.0,
        timeout=60
    )

    prompt = f"""Eres un asistente de auditoría farmacéutica.
Contexto: {context}
Pregunta: {question}
Responde con UNA o DOS oraciones. Si no hay info, dice 'No hay información suficiente'.
Respuesta:"""

    start = time.time()
    result = llm.invoke(prompt)
    elapsed = time.time() - start

    result_text = result.content if hasattr(result, 'content') else str(result)
    print(f"  Response ({len(result_text)} chars, {elapsed:.1f}s):")
    print(f"  {result_text[:300]}")

    # Verify
    result_lower = result_text.lower()

    # Check no fallback
    if "no hay información suficiente" in result_lower:
        print("  FAIL: Model returned fallback")
        return False

    # Check expected keywords
    matches = [kw for kw in expected_keywords if kw.lower() in result_lower]
    print(f"  Keywords matched: {len(matches)}/6: {matches}")

    if len(matches) < 3:
        print("  FAIL: Not enough keywords matched")
        return False

    print("  PASS")
    return True


# Test all 3 FAQs
FAQS = [
    {
        "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
        "keywords": ["PAMI", "cobertura", "medicamentos", "receta", "crónicos", "ambulatorio"],
    },
    {
        "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
        "keywords": ["OSER", "2026", "receta", "electrónica", "obligatorio", "DNI"],
    },
    {
        "question": "¿Qué documentación necesito para gestionar una receta DIM?",
        "keywords": ["DIM", "receta", "electrónica", "Circular", "medicamentos", "prescripción"],
    },
]

print("=" * 60)
print("QWEN DIRECT INTEGRATION TEST")
print("=" * 60)

passed = 0
failed = 0

for i, faq in enumerate(FAQS):
    print(f"\n{'='*60}")
    print(f"FAQ {i+1}/3")
    print(f"{'='*60}")

    try:
        ok = test_faq_with_ollama(faq["question"], faq["keywords"])
        if ok:
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'='*60}")

if failed > 0:
    print("\nTests failed. Analysis required before proceeding.")
    sys.exit(1)
else:
    print("\nAll tests passed!")
    sys.exit(0)