"""
Diagnostic script - muestra exactamente qué chunks se recuperan para cada FAQ.
Incluye score, entidad, fuente, y contenido (primeros 300 chars).
"""
import sys
sys.path.insert(0, '.')

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import FarmaConfig


def diagnose_faq(question, faq_id, top_k=5):
    """Diagnostic retrieval for a single FAQ."""
    config = FarmaConfig.load('config.json')

    print(f"\n{'='*70}")
    print(f"FAQ: {faq_id}")
    print(f"Q:  {question}")
    print(f"{'='*70}")

    # Load embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=config.embedding_model,
        encode_kwargs={"normalize_embeddings": True}
    )

    # Load vectorstore
    vs = Chroma(
        persist_directory=config.chroma_path,
        embedding_function=embeddings,
        collection_name=config.collection_name,
        collection_metadata={"hnsw:space": "cosine"}
    )

    # Retrieve with high top_k to see more options
    docs_and_scores = vs.similarity_search_with_relevance_scores(question, k=top_k)

    print(f"\n  Retrieved {len(docs_and_scores)} chunks:")
    print(f"  {'N':<3} {'Score':>7} {'Entidad':<10} {'Fuente':<45}")
    print(f"  {'-'*3} {'-'*7} {'-'*10} {'-'*45}")

    for i, (doc, score) in enumerate(docs_and_scores):
        src = doc.metadata.get('source', '?')[:43]
        ent = doc.metadata.get('entidad', '?')
        content_preview = doc.page_content[:100].replace('\n', '|')
        print(f"\n  {i+1}. Score: {score:.4f} | Entidad: {ent:<10} | Fuente: {src}")
        print(f"     Content: {content_preview}...")

    return docs_and_scores


def main():
    config = FarmaConfig.load('config.json')

    print("=" * 70)
    print("RETRIEVAL DIAGNOSTIC FOR FAQS")
    print("=" * 70)
    print(f"Config: chunk_size={config.chunk_size}, top_k={config.top_k}, threshold={config.score_threshold}")

    faqs = [
        {
            "id": "faq_pami",
            "question": "¿Cuáles son los requisitos para la cobertura de medicamentos de PAMI?",
        },
        {
            "id": "faq_oser",
            "question": "¿Qué sucede con las recetas físicas de OSER desde 2026?",
        },
        {
            "id": "faq_dim",
            "question": "¿Qué documentación necesito para gestionar una receta DIM?",
        },
    ]

    all_results = {}
    for faq in faqs:
        results = diagnose_faq(faq["question"], faq["id"])
        all_results[faq["id"]] = results

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY - CHUNKS BY ENTITY")
    print("=" * 70)

    for faq_id, results in all_results.items():
        print(f"\n  {faq_id}:")
        entity_counts = {}
        for doc, score in results:
            ent = doc.metadata.get('entidad', '?')
            entity_counts[ent] = entity_counts.get(ent, 0) + 1

        for ent, count in sorted(entity_counts.items(), key=lambda x: -x[1]):
            print(f"    - {ent}: {count} chunks")

        # Show top chunk content for this FAQ
        top_doc, top_score = results[0]
        print(f"    Top chunk: score={top_score:.4f}")
        print(f"    Content preview: {top_doc.page_content[:200]}...")


if __name__ == '__main__':
    main()