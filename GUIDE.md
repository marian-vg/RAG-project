# Guía Técnica del Sistema FarmaRAG

Este documento explica el funcionamiento interno del sistema RAG, detallando el flujo de datos, las funciones clave y el razonamiento detrás de cada elección tecnológica.

---

## 1. El Proceso de Ingesta (`ingest.py`)

La ingesta es el corazón del sistema, donde convertimos documentos estáticos en datos recuperables.

### Carga de Documentos: `UnstructuredPDFLoader`
Cuando llamamos a `loader = UnstructuredPDFLoader(pdf_path)`, el sistema no solo lee el texto plano. 
*   **¿Qué retorna?**: Una lista de objetos `Document` de LangChain. Cada objeto contiene `page_content` (el texto extraído) y `metadata` (un diccionario con información del archivo).
*   **¿Por qué Unstructured?**: A diferencia de cargadores básicos como `PyPDF`, Unstructured utiliza modelos de inferencia para reconocer párrafos, tablas y listas. Esto es crucial para que las reglas de auditoría se mantengan legibles tras ser fragmentadas.

### Identificación de Entidad: `get_entidad(text)`
*   **Funcionamiento**: Toma los primeros 4000 caracteres del texto extraído y los envía a `gemini-3.1-flash-lite-preview` con un prompt estructurado.
*   **Razonamiento**: Los nombres de archivos suelen ser poco descriptivos o erróneos. Analizando el contenido (encabezados, firmas, sellos mencionados en el texto), el LLM puede clasificar el documento con alta precisión como **DIM**, **COFAER** o **PAMI**.

### Fragmentación Semántica: `RecursiveCharacterTextSplitter`
*   **Método**: `split_documents(docs)`.
*   **Parámetros**: `chunk_size=800` y `chunk_overlap=150`.
*   **El "Por Qué"**: 800 caracteres es el tamaño ideal para capturar una regla de auditoría completa sin exceder la ventana de contexto. El "overlap" (solapamiento) de 150 caracteres asegura que si una idea se corta, el siguiente fragmento tenga suficiente contexto previo para que el modelo entienda de qué se está hablando.

---

## 2. Vectorización y Embeddings

### El Modelo: `gemini-embedding-001`
*   **¿Qué hace?**: Convierte cada fragmento de texto en una lista de 768 números (un vector). Fragmentos con significados similares tendrán vectores con "distancias" matemáticas cortas entre sí.
*   **Idioma**: Este modelo está entrenado para entender el contexto semántico en Español, reconociendo sinónimos y jerga farmacéutica argentina.

### El Almacén: `ChromaDB`
*   **Método**: `Chroma.from_documents(...)`.
*   **Función**: Almacena los vectores y sus metadatos (`source`, `entidad`, `fecha_ingesta`) de forma persistente en el disco. Esto evita tener que re-procesar los PDFs cada vez que queremos hacer una pregunta.

---

## 3. El Motor de Consulta (`farma_query.py`)

### Recuperación (Retrieval): `vectorstore.as_retriever(k=4)`
*   **Acción**: Cuando haces una pregunta, el sistema la convierte en un vector, busca los 4 fragmentos más parecidos en la base de datos y los retorna.
*   **Filtrado**: Los fragmentos retornados mantienen sus metadatos, lo que permite al sistema saber exactamente de qué archivo y de qué entidad provienen.

### Generación y Orquestación (LCEL)
Utilizamos **LangChain Expression Language (LCEL)** para unir las piezas:
1.  **Input**: Tu pregunta.
2.  **Contexto**: El `retriever` busca los fragmentos y la función `format_docs` los limpia y etiqueta.
3.  **Prompt**: Se ensambla la pregunta con el contexto y las instrucciones de "Auditor Estricto".
4.  **LLM**: Gemini genera la respuesta final basada únicamente en el contexto provisto.

---

## 4. Ejecución Iterativa (Modo Bucle)

Para optimizar el uso, el sistema incluye una función `modo_interactivo()`. 
*   **¿Por qué?**: Cargar los embeddings y conectar con la base de datos vectorial toma unos segundos. Al ejecutar en bucle, solo realizamos esta carga una vez, permitiendo respuestas casi instantáneas en las preguntas subsiguientes.
*   **Control**: El bucle utiliza `input()` para capturar la pregunta y solo rompe la ejecución si el usuario escribe comandos de salida específicos, garantizando una sesión de auditoría fluida.
