import os
import re
import uuid
import json
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.unificador import FarmaRAG
from src.config import FarmaConfig
from src.auditor import (
    LLMProviderError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FarmaRAG API", description="Servidor para la interfaz gráfica del Auditor de Farmacia")
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOGS_DIR = "logs"
DEAD_LETTER_FILE = os.path.join(LOGS_DIR, "failed_queries.jsonl")

def ensure_logs_dir():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def sanitize_input(text: str) -> str:
    """Sanitiza input del usuario para prevenir prompt injection."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    return text[:1000]

def structured_log(level: str, event: str, request_id: str, **kwargs):
    """Loguea en formato JSON estructurado."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "event": event,
        "request_id": request_id,
        **kwargs
    }
    print(json.dumps(log_entry))

def log_dead_letter(request_id: str, question: str, error: str, provider: str = None):
    """Registra queries fallidas en dead letter log."""
    ensure_logs_dir()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "question": question,
        "error": error,
        "provider": provider
    }
    with open(DEAD_LETTER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

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


@app.get("/health")
def deep_health_check():
    """Deep health check endpoint."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "engine_loaded": rag is not None,
        "components": {}
    }

    try:
        if rag:
            health["components"]["config"] = {
                "llm_provider": rag.config.llm_provider,
                "llm_model": rag.config.llm_model,
                "friendly_name": rag.config.get_friendly_name()
            }
            health["components"]["vectorstore"] = {
                "path": rag.config.chroma_path,
                "collection": rag.config.collection_name
            }
        else:
            health["components"]["config"] = "not_loaded"
    except Exception as e:
        health["components"]["config"] = f"error: {str(e)}"

    try:
        ensure_logs_dir()
        health["components"]["logging"] = "ok"
    except Exception as e:
        health["components"]["logging"] = f"error: {str(e)}"

    return health


@app.get("/aliases")
def get_model_aliases():
    """Retorna mapeo de nombres amigables a IDs técnicos."""
    if not rag:
        raise HTTPException(status_code=503, detail="Motor RAG no disponible")
    return {
        "friendly_to_technical": rag.config.MODEL_ALIASES
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
@limiter.limit("10/minute")
async def ask_auditor(request: Request, body: QueryRequest):
    global last_fallback_event
    request_id = str(uuid.uuid4())

    if not rag:
        structured_log("ERROR", "engine_not_loaded", request_id)
        raise HTTPException(status_code=503, detail="Motor RAG no disponible")

    question = sanitize_input(body.question)
    if not question:
        structured_log("WARNING", "empty_question", request_id)
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

    if len(question) < 3:
        raise HTTPException(status_code=400, detail="La pregunta debe tener al menos 3 caracteres")

    try:
        structured_log("INFO", "query_start", request_id, question_length=len(question))
        start_time = time.time()

        respuesta, provider_used = rag.ask_with_fallback(
            question,
            preferred_provider=body.provider
        )

        duration = time.time() - start_time
        structured_log("INFO", "query_success", request_id, provider=provider_used, duration_ms=round(duration*1000, 2))

        last_fallback_event = {
            "provider_used": provider_used,
            "fallback_triggered": body.provider is not None or provider_used != (body.provider or rag.config.llm_provider)
        }

        return QueryResponse(
            answer=respuesta,
            provider_used=provider_used,
            fallback_triggered=last_fallback_event["fallback_triggered"]
        )

    except LLMRateLimitError as e:
        duration = time.time() - start_time
        structured_log("ERROR", "rate_limit", request_id, provider=body.provider or rag.config.llm_provider)
        log_dead_letter(request_id, question, str(e), body.provider)
        raise HTTPException(status_code=503, detail="model_overloaded")

    except LLMTimeoutError as e:
        duration = time.time() - start_time
        structured_log("ERROR", "timeout", request_id, provider=body.provider or rag.config.llm_provider, duration_ms=round(duration*1000, 2))
        log_dead_letter(request_id, question, str(e), body.provider)
        raise HTTPException(status_code=503, detail="timeout")

    except LLMConnectionError as e:
        duration = time.time() - start_time
        structured_log("ERROR", "connection_error", request_id, provider=body.provider or rag.config.llm_provider)
        log_dead_letter(request_id, question, str(e), body.provider)
        raise HTTPException(status_code=503, detail="connection_error")

    except LLMProviderError as e:
        structured_log("ERROR", "provider_error", request_id, error=str(e))
        log_dead_letter(request_id, question, str(e), body.provider)
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        structured_log("ERROR", "unknown_error", request_id, error=str(e))
        log_dead_letter(request_id, question, str(e), body.provider)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fallback-status")
def get_fallback_status():
    """Retorna el estado del último fallback para el frontend."""
    return last_fallback_event


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limit_exceeded", "code": "rate_limit", "fallback_triggered": False}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
