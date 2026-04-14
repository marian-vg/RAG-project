import json
import os
from pydantic import BaseModel

class FarmaConfig(BaseModel):
    """Configuración centralizada para el motor FarmaRAG."""
    docs_dir: str = "documentos"
    chroma_path: str = "chroma_db"
    collection_name: str = "farmarag_collection"
    chunk_size: int = 800
    chunk_overlap: int = 150
    embedding_model: str = "models/gemini-embedding-001"
    llm_provider: str = "ollama"  # "ollama" o "gemini"
    llm_model: str = "qwen2.5:0.5b"  # p.ej. "qwen2.5:0.5b" o "gemini-3.1-flash-lite-preview"
    generation_model: str = "models/gemini-3.1-flash-lite-preview"
    temperature: float = 0.0
    top_k: int = 4
    prompt: str = ""
    search_type: str = "similarity"

    def save(self, file_path="config.json"):
        """Guarda la configuración actual en un archivo JSON."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=4)
        print(f"[*] Configuración guardada en {file_path}")

    @classmethod
    def load(cls, file_path="config.json"):
        """Carga la configuración desde un archivo JSON o retorna valores por defecto."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = f.read()
                    print(f"[*] Configuración cargada desde {file_path}")
                    return cls.model_validate_json(data)
            except Exception as e:
                print(f"[!] Error cargando configuración: {e}. Usando valores por defecto.")
        return cls()
