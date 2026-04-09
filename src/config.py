from pydantic import BaseModel

class FarmaConfig(BaseModel):
    """Configuración centralizada para el motor FarmaRAG."""
    docs_dir: str = "documentos"
    chroma_path: str = "chroma_db"
    collection_name: str = "farmarag_collection"
    chunk_size: int = 800
    chunk_overlap: int = 150
    embedding_model: str = "models/gemini-embedding-001"
    generation_model: str = "models/gemini-3.1-flash-lite-preview"
    temperature: float = 0.0
    top_k: int = 4
    prompt: ""
    search_type: str = "similarity"
