Fase 1: Ingestión y Estructuración de Datos (Data Ingestion)
El objetivo de esta fase no es solo "leer texto", sino preservar la estructura lógica de los manuales y circulares de OSER y PAMI.

Tecnología: UnstructuredPDFLoader (de LangChain).

Acciones de Desarrollo:

Carga Inteligente: Se utiliza UnstructuredPDFLoader porque, a diferencia de los lectores básicos, este modelo identifica los elementos del documento (títulos, párrafos, elementos de listas y, críticamente, tablas).

Limpieza Previa: Se programa un pequeño script en Python para limpiar los saltos de línea inútiles o caracteres extraños que el OCR pueda haber interpretado mal.

Inyección de Metadatos: Por cada documento cargado, se debe inyectar manualmente un diccionario de metadatos. Ejemplo: {"source": "Circular_OSER_Enero2026.pdf", "obra_social": "OSER", "fecha_vigencia": "2026-01-01"}. Esto será vital para que el RAG entienda la temporalidad.

Fase 2: Fragmentación Semántica y Cuidada (Chunking)
Aquí garantizamos que ninguna regla burocrática se corte "a lo brusco", preservando el contexto para la fase de embeddings.

Tecnología: RecursiveCharacterTextSplitter.

Acciones de Desarrollo:

Definición de Separadores: Se configura la lista de separadores en orden de prioridad: ["\n\n", "\n", ".", " ", ""]. Esto obliga al algoritmo a intentar cortar siempre por cambio de párrafo primero; si el párrafo es muy largo, corta por oraciones (puntos); y solo como último recurso, corta por espacios. Nunca rompe una palabra ni una idea por la mitad.

Parametrización Empírica: Se configuran los valores iniciales para iterar (los que documentarás en el informe).

chunk_size = 800: Suficientemente amplio para abarcar una regla completa de facturación con sus excepciones.

chunk_overlap = 150: Un solapamiento de aproximadamente dos oraciones. Garantiza que si la regla de PAMI se extendió al siguiente bloque, el pronombre o el sujeto de la oración no pierdan su anclaje.

Fase 3: Vectorización y Almacenamiento Local (Embedding & Vector DB)
Transformación del texto limpio a coordenadas matemáticas para habilitar la búsqueda por similitud.

Tecnología: gemini-embedding-001 (vía GoogleGenerativeAIEmbeddings) y ChromaDB.

Acciones de Desarrollo:

Inicialización del Modelo: Instanciar la conexión a la API de Google configurando explícitamente el modelo gemini-embedding-001.

Creación de la Colección: Se crea una colección persistente en ChromaDB (guardada en una carpeta local de tu proyecto para no tener que re-vectorizar los PDFs cada vez que ejecutas el código).

Población de la Base: Se iteran los fragmentos de la Fase 2, se vectorizan y se guardan en ChromaDB junto con sus metadatos asociados.

Fase 4: Estrategia de Recuperación (Retrieval Pipeline)
Conectar la base de datos con la consulta del usuario antes de involucrar al modelo generativo.

Tecnología: Componente as_retriever() de ChromaDB en LangChain.

Acciones de Desarrollo:

Configuración de Búsqueda (Top-K): Se configura el recuperador para traer los k=4 fragmentos más relevantes. Cuatro fragmentos de 800 caracteres le darán al LLM un contexto robusto pero muy enfocado, sin saturar su memoria.

Filtrado por Metadatos (Opcional pero recomendado): Se puede implementar lógica para que, si el usuario menciona "OSER" en su consulta, el recuperador filtre primero la base vectorial por {"obra_social": "OSER"} antes de buscar similitud matemática. Esto elimina el riesgo de que el modelo confunda reglas de PAMI con las de OSER.

Fase 5: Generación Aumentada y Orquestación (LCEL)
El corazón del sistema. Se ensamblan las piezas y se le da el contexto al modelo multimodal lite.

Tecnología: gemini-3.1-flash-lite-preview (vía ChatGoogleGenerativeAI) y LangChain Expression Language (LCEL).

Acciones de Desarrollo:

Ingeniería del Prompt del Sistema (ChatPromptTemplate): Redactar la instrucción de hierro.

Ejemplo conceptual: "Eres un auditor de farmacia estricto. Responde la pregunta del usuario utilizando ÚNICAMENTE los fragmentos de contexto provistos. Si la respuesta no está, di 'No hay información suficiente'. Cita el documento de origen en tu respuesta."

Cadena LCEL: Construir el flujo encadenado:

Consulta del Usuario -> Retriever (Busca en Chroma) -> Ensambla Contexto + Prompt -> LLM (Gemini Flash Lite) -> StrOutputParser() -> Respuesta Final.