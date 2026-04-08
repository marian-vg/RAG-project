# Walkthrough de Implementación - FarmaRAG

Este documento detalla el proceso de desarrollo y los resultados obtenidos en la implementación del sistema RAG para auditoría de farmacia.

## 🚀 Fases Completadas

### Fase 1: Ingestión de Datos
- **Tecnología:** `UnstructuredPDFLoader`.
- **Refactorización:** Implementación de `get_entidad()` utilizando `gemini-3.1-flash-lite-preview`.
- **Logro:** Identificación automática de entidades (DIM, COFAER, PAMI) analizando el contenido del documento, eliminando la dependencia del nombre del archivo.

### Fase 2: Fragmentación (Chunking)
- **Configuración:** `chunk_size=800`, `chunk_overlap=150`.
- **Separadores:** Prioridad en párrafos y puntos para mantener coherencia normativa.

### Fase 3: Vectorización
- **Embeddings:** `models/gemini-embedding-001`.
- **Base de Datos:** `ChromaDB` (persistente en local).

### Fase 4: Estrategia de Recuperación (Retrieval)
- **Configuración:** `Top-K = 4`.
- **Metadatos:** Inclusión de `source` y `entidad` en los fragmentos recuperados para trazabilidad.

### Fase 5: Generación y Orquestación
- **Modelo:** `gemini-3.1-flash-lite-preview`.
- **Engine:** LCEL (LangChain Expression Language).
- **Prompt:** Configurado como "Auditor de Farmacia Estricto" en Español.

---

## 📊 Resultados de las Pruebas

Se ejecutó una suite de pruebas (`test_rag.py`) con los siguientes resultados:

1.  **DIM (Receta Digital):** Respuesta precisa sobre la obligatoriedad desde el 01/01/2026 y el tratamiento de recetas oficiales en papel.
2.  **COFAER (Circulares):** Desglose correcto de circulares 04/2026 y 11/2026, listando obras sociales cortadas.
3.  **PAMI (Ambulatorio):** Detalle de pautas de validación, prescripción genérica y uso racional de medicamentos.
4.  **Seguridad (Fuera de Contexto):** Ante la pregunta "¿Cómo se cocina una tortilla de papas?", el modelo respondió correctamente: *"No hay información suficiente en los documentos cargados para responder esta pregunta."*

---

## 🛠️ Archivos Principales
- `ingest.py`: Script de procesamiento y carga inicial.
- `farma_query.py`: Motor de consulta RAG y lógica de auditoría.
- `test_rag.py`: Suite de validación automática.
- `chroma_db/`: Directorio de persistencia vectorial.

---
**Estado Final:** Sistema 100% funcional y verificado.
