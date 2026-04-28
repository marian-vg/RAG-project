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
    llm_provider: str = "ollama"
    llm_model: str = "Qwen 2.5"
    generation_model: str = "models/gemini-3.1-flash-lite-preview"
    temperature: float = 0.0
    top_k: int = 4
    prompt: str = ""
    search_type: str = "similarity"

    MODEL_ALIASES: dict = {
        "Qwen 2.5": "qwen2.5:0.5b",
        "Gemini 3.1": "models/gemini-3.1-flash-lite-preview",
    }

    @property
    def FRIENDLY_TO_MODEL(self) -> dict:
        """Retorna mapeo reverse: nombre amigable -> ID técnico."""
        return {v: k for k, v in self.MODEL_ALIASES.items()}

    def get_friendly_name(self) -> str:
        for friendly, technical in self.MODEL_ALIASES.items():
            if self.llm_model == technical:
                return friendly
        return self.llm_model

    def get_technical_name(self, friendly_name: str) -> str:
        """Convierte nombre amigable a ID técnico."""
        return self.MODEL_ALIASES.get(friendly_name, friendly_name)

    def save(self, file_path="config.json"):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=4)
        print(f"[*] Configuración guardada en {file_path}")

    @classmethod
    def load(cls, file_path="config.json"):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = f.read()
                    print(f"[*] Configuración cargada desde {file_path}")
                    return cls.model_validate_json(data)
            except Exception as e:
                print(f"[!] Error cargando configuración: {e}. Usando valores por defecto.")
        return cls()
