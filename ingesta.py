from src.unificador import FarmaRAG, FarmaConfig

def ejecutar_ingesta():
    config = FarmaConfig(
        chunk_size=400,
        chunk_overlap=60,
        top_k=3,
        temperature=0.4
    )
    
    rag = FarmaRAG(config)
    
    print("=== INICIANDO PROCESO DE INGESTA REESTRUCTURADA ===")
    rag.ingest(clean_first=True)
    print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    ejecutar_ingesta()
