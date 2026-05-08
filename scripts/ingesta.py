from src.unificador import FarmaRAG, FarmaConfig

def ejecutar_ingesta():
    config = FarmaConfig.load("config.json")
    
    rag = FarmaRAG(config)
    
    print("=== INICIANDO PROCESO DE INGESTA REESTRUCTURADA ===")
    rag.ingest(clean_first=True)
    print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    ejecutar_ingesta()
