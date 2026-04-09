# FarmaRAG - Auditor de Farmacia Inteligente

FarmaRAG es un sistema avanzado de Recuperación Aumentada por Generación (RAG) diseñado para asistir en la auditoría de normativas farmacéuticas. Utiliza inteligencia artificial para analizar circulares y manuales de entidades como DIM, COFAER y PAMI, ofreciendo respuestas precisas y citadas basadas exclusivamente en la documentación oficial cargada, garantizando así el cumplimiento normativo y la reducción de errores humanos en la interpretación de pautas de facturación.

## 🚀 Guía de Ejecución

Para poner en marcha el sistema completo (Motor + Interfaz Gráfica), siga estos pasos:

### 1. Preparación del Entorno
Asegúrese de tener instaladas las dependencias necesarias y configurada su clave de API en el archivo `.env`:
```bash
pip install -r requirements.txt
# El archivo .env debe contener: GOOGLE_API_KEY=tu_llave_aqui
```

### 2. Ingesta de Documentos (Opcional si ya existe la DB)
Si ha añadido nuevos PDFs a la carpeta `/documentos`, ejecute el procesador para actualizar la base de datos vectorial:
```bash
python ingest.py
```

### 3. Iniciar el Servidor (Backend)
Abra una terminal y ejecute el servidor de la API:
```bash
python server.py
```
*El servidor estará disponible en `http://localhost:8000`.*

### 4. Iniciar la Interfaz Gráfica (Frontend)
Abra una **segunda terminal**, diríjase a la carpeta de la vista e inicie el entorno de desarrollo:
```bash
cd Views
npm run dev
```
*La interfaz se abrirá automáticamente en su navegador (usualmente en `http://localhost:5173`).*

---
**Nota:** El sistema cuenta con un **Modo Auditor Estricto**, por lo que si una consulta no tiene sustento en los documentos, el chatbot informará que no posee información suficiente en lugar de improvisar una respuesta.
