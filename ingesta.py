from src.engine import FarmaRAG, FarmaConfig

def ejecutar_ingesta():
    config = FarmaConfig(
        chunk_size=800,
        chunk_overlap=150,
    )
    
    rag = FarmaRAG(config)
    
    print("=== INICIANDO PROCESO DE INGESTA REESTRUCTURADA ===")
    rag.ingest(clean_first=True)
    print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    ejecutar_ingesta()
