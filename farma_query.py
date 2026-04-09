import os
from src.unificador import FarmaRAG, FarmaConfig

def modo_interactivo():
    """Ejecuta el sistema RAG profesional en modo interactivo."""
    
    config = FarmaConfig(
        temperature=0.0,
        top_k=4
    )
    
    rag = FarmaRAG(config)
    
    print("\n" + "="*60)
    print("SISTEMA DE AUDITORÍA FARMARAG PROFESIONAL - MODO INTERACTIVO")
    print("Escribe 'salir' o 'exit' para finalizar.")
    print("="*60)
    
    while True:
        pregunta = input("\n[?] Ingrese su consulta: ").strip()
        
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("[*] Cerrando auditoría...")
            break
            
        if not pregunta: continue
            
        print("[*] Auditor analizando documentos...")
        try:
            respuesta = rag.ask(pregunta)
            print("\n" + "-"*30)
            print("RESPUESTA DEL AUDITOR:")
            print("-"*30)
            print(respuesta)
            print("-"*30)
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    modo_interactivo()
