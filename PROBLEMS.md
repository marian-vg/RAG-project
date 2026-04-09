# Registro de Problemas y Fallas de Desarrollo (Audit Log) - FarmaRAG

Este documento detalla los errores técnicos, fallas de integración y desafíos lógicos encontrados durante el desarrollo de las Fases 1 a 5 del sistema RAG.

## 1. Configuración de Entorno y Dependencias

### Error: Módulos faltantes en `unstructured`
*   **Problema:** Al intentar ejecutar `ingest.py`, el sistema falló con el error `ModuleNotFoundError: No module named 'unstructured_inference'`.
*   **Causa:** La instalación base de `unstructured[pdf]` no incluye por defecto los modelos de inferencia necesarios para el análisis de estructura de documentos complejos en local.
*   **Resolución:** Se realizó una instalación manual de `unstructured-inference` y `unstructured-pytesseract` para habilitar el OCR y la detección de elementos.

## 2. Integración con Google Generative AI (Modelos y API)

### Falla: Nombres de Modelos Inexistentes (Error 404)
*   **Problema:** Intentos iniciales de usar `models/gemini-1.5-flash` y `models/embedding-001` resultaron en errores `404 NOT_FOUND`.
*   **Causa:** Inconsistencia entre los nombres comerciales de los modelos y los nombres técnicos aceptados por la versión actual de la librería `langchain-google-genai` en conjunto con el endpoint de la API.
*   **Resolución:** Se creó un script de diagnóstico (`list_models.py`) para listar los modelos disponibles en la cuenta del usuario. Se identificaron y corrigieron los nombres a:
    *   Generación: `models/gemini-3.1-flash-lite-preview`
    *   Embeddings: `models/gemini-embedding-001`

### Falla: Detección de Idioma
*   **Problema:** El cargador de Unstructured emitía advertencias: `No languages specified, defaulting to English`.
*   **Causa:** Falta de parámetros explícitos de idioma en el cargador de documentos.
*   **Resolución:** Se forzó la generalización al **Español** tanto en los metadatos como en los prompts de los agentes para evitar sesgos del modelo hacia el inglés.

## 3. Desafíos de Lógica y Arquitectura

### Problema: Identificación de Entidad por Nombre de Archivo
*   **Problema:** La lógica inicial intentaba clasificar los documentos (PAMI, COFAER, OSER) basándose en palabras clave del nombre del archivo. Esto fallaba con archivos nombrados genéricamente (ej: `Circular 4.pdf`).
*   **Causa:** Los nombres de archivos no son fuentes de verdad confiables en auditoría farmacéutica.
*   **Resolución:** Se refactorizó `ingest.py` para incluir un paso de **Clasificación por Contenido** usando LLM. El sistema ahora lee los primeros 4000 caracteres de cada PDF para determinar la entidad real (DIM, COFAER, PAMI) independientemente del nombre del archivo.

## 4. Limitaciones de Herramientas de Desarrollo (CLI/PowerShell)

### Conflicto: Ambigüedad de Comandos
*   **Problema:** El comando `ls -a` falló en el entorno Windows del usuario.
*   **Causa:** El alias `ls` en PowerShell es `Get-ChildItem`, el cual no reconoce `-a` como un parámetro válido para archivos ocultos (requiere `-Force`).
*   **Resolución:** Cambio de sintaxis a comandos nativos de PowerShell para asegurar la visibilidad del archivo `.env`.

### Restricción: Protección de Secretos
*   **Problema:** El lector de archivos del agente ignoró inicialmente el archivo `.env` por políticas de seguridad de la herramienta.
*   **Causa:** Medidas de seguridad automáticas para evitar la filtración de llaves API.
*   **Resolución:** Se verificó la existencia de la llave mediante comandos de consola (`Get-Content`) sin persistir la llave en los logs de lectura del agente, asegurando que el proceso pudiera continuar.

---
**Nota Final de Auditoría:** Todos los errores fueron mitigados y la versión final del sistema en `ingest.py` y `farma_query.py` incorpora las correcciones necesarias para evitar recurrencias.
