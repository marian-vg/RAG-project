# RESUMEN TÉCNICO FARMARAG

Este documento detalla el flujo de trabajo actual del sistema de Auditoría de Farmacia, optimizado para modelos de bajo costo.

## 1. Flujo de Ingesta (Preparación de Datos)
El proceso comienza en `ingesta.py` y sigue este orden:

1.  **Inicio (`ingesta.py`)**: Llama a `rag.ingest()`, configurando el tamaño de fragmentos (*chunks*) de 800 caracteres.
2.  **Carga de PDF (`src/procesador.py`)**: 
    - Usa `UnstructuredPDFLoader` para extraer elementos del PDF.
    - Se aplica `_clean_text` para eliminar ruido visual y caracteres repetitivos.
3.  **Detección de Entidad (`src/procesador.py`)**:
    - **Paso A (Heurística)**: `_extract_entity_from_filename` busca palabras clave (PAMI, OSER, etc.) en el nombre del archivo.
    - **Paso B (Fallback)**: Si falla la heurística, `_detect_entity` consulta a un LLM (Gemini) para clasificar el documento por contenido.
4.  **Fragmentación y Metadatos**: El texto se divide y se le inyectan metadatos clave: `source`, `entidad` y `fecha_ingesta`.
5.  **Vectorización e Indexación**: Los fragmentos se convierten en vectores usando `GoogleGenerativeAIEmbeddings` y se guardan en la base de datos `Chroma`.

## 2. Flujo de Consulta (RAG)
El proceso de pregunta-respuesta se gestiona en `src/auditor.py`:

1.  **Configuración del Modelo**: El sistema selecciona el proveedor (Ollama o Gemini) según la configuración activa mediante `_get_llm()`.
2.  **Recuperación (Retrieval)**: 
    - Se buscan los `top_k` (4 por defecto) fragmentos más similares a la pregunta del usuario en la DB Chroma.
    - `_format_docs` estructura estos fragmentos con sus fuentes y entidades.
3.  **Generación de Respuesta**:
    - Se inyecta el contexto en un **Prompt Estructurado** optimizado para modelos pequeños (Qwen).
    - El LLM genera la respuesta basándose estrictamente en el texto delimitado por etiquetas `<contexto>`.
    - Si no hay información, el modelo responde con una frase predefinida de error.

## 3. Interfaces de Usuario
- **Modo CLI (`farma_query.py`)**: Permite elegir el modelo al inicio (Qwen Local o Gemini Cloud) y mantiene un bucle de preguntas.
- **Modo Servidor (`server.py`)**: 
    - `POST /ask`: Recibe preguntas y devuelve respuestas del auditor.
    - `POST /config`: Permite cambiar el modelo del motor RAG dinámicamente.
    - `GET /`: Informa el estado del motor y qué modelo está activo.

## 4. Notas para Depuración
- **Modelos Locales**: Requieren que **Ollama** esté corriendo y el modelo (`qwen2.5:0.5b`) descargado.
- **Embeddings**: Actualmente el sistema usa Gemini para los embeddings por su alta precisión incluso cuando el LLM de respuesta es local.
- **Limpieza**: Si los resultados son extraños, revisar `src/procesador.py -> _clean_text` para ajustar el filtrado de caracteres especiales.
