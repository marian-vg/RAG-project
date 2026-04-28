import os
from farma_query import consultar

def run_suite_de_pruebas():
    """Ejecuta una serie de preguntas de prueba para validar el sistema FarmaRAG."""
    
    preguntas = [
        # Prueba sobre DIM
        "¿Qué dice la Circular 53 sobre la implementación de la receta digital en DIM?",
        
        # Prueba sobre COFAER (Colegio Farmacéutico de Entre Ríos)
        "¿Cuál es el contenido de la Circular 4 - 11 de COFAER?",
        
        # Prueba sobre PAMI
        "¿Cuáles son las pautas para el PAMI Ambulatorio según el documento de 2022?",
        
        # Prueba de fuera de contexto
        "¿Cómo se cocina una tortilla de papas?"
    ]
    
    print("="*60)
    print("INICIANDO SUITE DE PRUEBAS DEL AUDITOR FARMARAG")
    print("="*60)
    
    for i, p in enumerate(preguntas, 1):
        print(f"\n--- PRUEBA {i} ---")
        ask(p)
        
    print("="*60)
    print("SUITE DE PRUEBAS FINALIZADA")
    print("="*60)

if __name__ == "__main__":
    run_suite_de_pruebas()
