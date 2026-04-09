from pydantic import BaseModel

class FarmaConfig(BaseModel):
    """Configuración centralizada para el motor FarmaRAG."""
    docs_dir: str = "documentos"
    chroma_path: str = "chroma_db"
    collection_name: str = "farmarag_collection"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "models/gemini-embedding-001"
    generation_model: str = "models/gemini-3.1-flash-lite-preview"
    temperature: float = 0.0
    top_k: int = 4
    search_type: str = "similarity" # similarity o mmr
