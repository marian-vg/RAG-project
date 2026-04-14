import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.unificador import FarmaRAG
from src.config import FarmaConfig

# Inicializar la aplicación FastAPI
app = FastAPI(title="FarmaRAG API", description="Servidor para la interfaz gráfica del Auditor de Farmacia")

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el motor RAG (se carga una vez al iniciar el servidor)
print("[*] Iniciando motor FarmaRAG...")
try:
    # Cargar configuración persistente (JSON) si existe
    config = FarmaConfig.load()
    rag = FarmaRAG(config)
    print(f"[*] Motor cargado con {config.llm_model} ({config.llm_provider})")
except Exception as e:
    print(f"[!] Error cargando el motor: {e}")
    rag = None

# Modelos de datos para la API
class ConfigRequest(BaseModel):
    llm_provider: str  # "ollama" o "gemini"
    llm_model: str

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="La pregunta debe tener entre 3 y 500 caracteres.")

class QueryResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "system": "FarmaRAG Auditor", 
        "engine_loaded": rag is not None,
        "current_model": rag.config.llm_model if rag else None
    }

@app.post("/config")
def update_config(request: ConfigRequest):
    """
    Endpoint para cambiar el modelo en caliente con persistencia.
    """
    global rag
    try:
        # Obtenemos la config actual o cargamos la base
        new_config = rag.config if rag else FarmaConfig.load()
        new_config.llm_provider = request.llm_provider
        new_config.llm_model = request.llm_model
        
        # Guardar para futuros reinicios
        new_config.save()
        
        # Reinicializar el motor con la nueva configuración
        rag = FarmaRAG(new_config)
        return {"status": "success", "new_model": new_config.llm_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=QueryResponse)
async def ask_auditor(request: QueryRequest):
    """
    Endpoint para realizar consultas al auditor de farmacia.
    """
    if not rag:
        raise HTTPException(status_code=503, detail="Motor RAG no disponible")
        
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
    
    try:
        print(f"[*] Procesando consulta: {request.question}")
        respuesta = rag.ask(request.question)
        return QueryResponse(answer=respuesta)
    except Exception as e:
        print(f"[!] Error procesando consulta: {e}")
        # Retornamos el error detallado para ayudar a la depuración
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Ejecutar servidor en puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
