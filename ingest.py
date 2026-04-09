import os
from farma_engine import FarmaRAG, FarmaConfig

def ejecutar_ingesta():
    # Aquí puedes personalizar parámetros para pruebas
    config = FarmaConfig(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    rag = FarmaRAG(config)
    
    print("=== INICIANDO PROCESO DE INGESTA PROFESIONAL ===")
    rag.ingest(clean_first=True)
    print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    ejecutar_ingesta()
