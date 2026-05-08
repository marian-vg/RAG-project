"""Debug retrieval with multiple queries to find OSER content."""
import sys
sys.path.insert(0, '.')

from src.config import FarmaConfig
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

config = FarmaConfig.load('config.json')
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
    encode_kwargs={'normalize_embeddings': True}
)
vs = Chroma(
    persist_directory=config.chroma_path,
    embedding_function=embeddings,
    collection_name=config.collection_name,
    collection_metadata={'hnsw:space': 'cosine'}
)

queries = [
    'recetas fisicas OSER 2026',
    'receta electronica obligatoria OSER',
    'requisitos cobertura medicamentos OSER',
]

for query in queries:
    print(f'\n=== Query: {query} ===')
    try:
        results = vs.similarity_search_with_relevance_scores(query, k=3)
        print(f'Results: {len(results)}')
        for doc, score in results:
            src = doc.metadata.get('source', '?')
            ent = doc.metadata.get('entidad', '?')
            content = doc.page_content[:80].replace('\n', ' ')
            print(f'  Score={score:.4f} | {src} ({ent}) | {content}')
    except Exception as e:
        print(f'Error: {e}')