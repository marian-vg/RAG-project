import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from src.unificador import FarmaRAG
from src.config import FarmaConfig
from src.auditor import (
    LLMProviderError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError
)

app = FastAPI(title="FarmaRAG API", description="Servidor para la interfaz gráfica del Auditor de Farmacia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[*] Iniciando motor FarmaRAG...")
try:
    config = FarmaConfig.load()
    rag = FarmaRAG(config)
    print(f"[*] Motor cargado con {config.llm_model} ({config.llm_provider})")
except Exception as e:
    print(f"[!] Error cargando el motor: {e}")
    rag = None

last_fallback_event = {"provider_used": None, "fallback_triggered": False}


class ConfigRequest(BaseModel):
    llm_provider: str
    llm_model: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    provider: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    provider_used: Optional[str] = None
    fallback_triggered: bool = False


class ErrorResponse(BaseModel):
    error: str
    code: str
    fallback_triggered: bool = False


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "FarmaRAG Auditor",
        "engine_loaded": rag is not None,
        "current_model": rag.config.get_friendly_name() if rag else None,
        "current_provider": rag.config.llm_provider if rag else None
    }


@app.post("/config")
def update_config(request: ConfigRequest):
    global rag
    try:
        new_config = rag.config if rag else FarmaConfig.load()
        new_config.llm_provider = request.llm_provider
        new_config.llm_model = request.llm_model

        new_config.save()

        rag = FarmaRAG(new_config)
        return {"status": "success", "new_model": new_config.llm_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=QueryResponse)
async def ask_auditor(request: QueryRequest):
    global last_fallback_event

    if not rag:
        raise HTTPException(status_code=503, detail="Motor RAG no disponible")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

    try:
        print(f"[*] Procesando consulta ({request.provider or 'default'}): {request.question}")
        respuesta, provider_used = rag.ask_with_fallback(
            request.question,
            provider_override=request.provider
        )

        last_fallback_event = {
            "provider_used": provider_used,
            "fallback_triggered": request.provider is not None or provider_used != (request.provider or rag.config.llm_provider)
        }

        return QueryResponse(
            answer=respuesta,
            provider_used=provider_used,
            fallback_triggered=last_fallback_event["fallback_triggered"]
        )

    except LLMRateLimitError as e:
        print(f"[!] Rate limit error: {e}")
        raise HTTPException(status_code=503, detail="model_overloaded")

    except LLMTimeoutError as e:
        print(f"[!] Timeout error: {e}")
        raise HTTPException(status_code=503, detail="timeout")

    except LLMConnectionError as e:
        print(f"[!] Connection error: {e}")
        raise HTTPException(status_code=503, detail="connection_error")

    except LLMProviderError as e:
        print(f"[!] Provider error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print(f"[!] Error procesando consulta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fallback-status")
def get_fallback_status():
    """Retorna el estado del último fallback para el frontend."""
    return last_fallback_event


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)