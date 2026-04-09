import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    config = FarmaConfig(temperature=0.0, top_k=4)
    rag = FarmaRAG(config)
    print("[*] Motor cargado correctamente.")
except Exception as e:
    print(f"[!] Error cargando el motor: {e}")
    rag = None

# Modelos de datos para la API
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"status": "online", "system": "FarmaRAG Auditor", "engine_loaded": rag is not None}

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
