"""Quick debug script to test retrieval scores."""
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

query = 'recetas OSER 2026'
results = vs.similarity_search_with_relevance_scores(query, k=5)

print(f'Query: {query}')
print(f'Results: {len(results)}')
for i, (doc, score) in enumerate(results):
    src = doc.metadata.get('source', '?')
    ent = doc.metadata.get('entidad', '?')
    content = doc.page_content[:150].replace('\n', ' ')
    print(f'{i+1}. Score={score:.4f} | {src} ({ent})')
    print(f'   Content: {content}...')
    print()