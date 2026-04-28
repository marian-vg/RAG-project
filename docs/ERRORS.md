Análisis de Errores
	En el desarrollo del sistema se presentaron algunos problemas que interfirieron con el resultado al que queríamos alcanzar, a continuación, se exponen las cinco fallas más importantes que hemos tenido al momento de trabajar:

Contaminación de contexto:
	Al principio del desarrollo del sistema, realizando unas pruebas, se dió una consulta sobre OSER, y en la respuesta se encontró con que se utilizaban normativas que pertenecen a PAMI, esto se debió a la detección de palabras comunes en la búsqueda por similitud, mezclando las reglas de diferentes archivos. Este problema se solucionó aplicando el Enriquecimiento de Metadatos, esto permite que cada fragmento es “etiquetado” con la correspondiente “entidad”, de esta forma, se sabe de qué documento viene la información y en qué página.

Saturación por concurrencia:	
    Mientras empezábamos a vectorizar los archivos, el sistema se interrumpió, esto se debió a la saturación del modelo de embeddings por intentar enviar todos los fragmentos al mismo tiempo. Esto se solucionó implementando el Procesamiento Secuencial por Lotes, de esta manera, se procesan grupos de fragmentos con pausas intermedias entre los llamados de cada grupo, manteniendo el flujo de datos dentro del límite otorgado.

Chunk Size demasiado pequeño:
	Cuando comenzamos a desarrollar el sistema, usamos un número muy pequeño de caracteres, haciendo que el sistema devuelva respuestas incompletas o directamente afirmaba que no sabía la respuesta por falta de información. Esto se soluciona gracias a elevar el valor de los caracteres a un tamaño suficiente para manejar las reglas técnicas de los documentos.

Incompatibilidad de Metadatos Complejos:
    Durante la vectorización, la base de datos ChromaDB rechazaba los fragmentos arrojando un error de tipo de datos. Esto se debió a que la librería de extracción (Unstructured) inyectaba metadatos técnicos complejos (como diccionarios de coordenadas) que la base vectorial no puede procesar. Se solucionó implementando un filtrado de metadatos que limpia las estructuras anidadas y conserva solo información plana y útil.

Dependencias de Sistema No Satisfechas (OCR):
    Al intentar mejorar la lectura de tablas mediante una estrategia de alta resolución, el sistema falló por la ausencia de Tesseract OCR en el entorno de ejecución. Dado que este es un binario externo pesado y difícil de portar, se optó por una resolución arquitectónica: cambiar a la estrategia de procesamiento rápido (fast) optimizada para documentos digitales, lo que eliminó la dependencia de software externo sin sacrificar la estructura de los datos.
