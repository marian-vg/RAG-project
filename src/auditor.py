import json
import os
import time
from typing import List, Tuple, Optional
from threading import Lock
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import FarmaConfig

LLM_TIMEOUT = 30
PROVIDER_ORDER = ["gemini", "ollama"]


class LLMProviderError(Exception):
    def __init__(self, provider: str, message: str, is_retryable: bool = True):
        self.provider = provider
        self.is_retryable = is_retryable
        super().__init__(message)


class LLMRateLimitError(LLMProviderError):
    def __init__(self, provider: str, message: str = "Rate limit exceeded"):
        super().__init__(provider, message, is_retryable=True)


class LLMConnectionError(LLMProviderError):
    def __init__(self, provider: str, message: str):
        super().__init__(provider, message, is_retryable=True)


class LLMTimeoutError(LLMProviderError):
    def __init__(self, provider: str, message: str = "Provider timeout"):
        super().__init__(provider, message, is_retryable=True)


class CircuitBreaker:
    """Circuit breaker para proteger contra fallos en cascada de providers LLM."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failures = {}
        self._lock = Lock()

    def record_failure(self, provider: str):
        with self._lock:
            if provider not in self._failures:
                self._failures[provider] = {"count": 0, "last_failure": 0}
            self._failures[provider]["count"] += 1
            self._failures[provider]["last_failure"] = time.time()

    def record_success(self, provider: str):
        with self._lock:
            if provider in self._failures:
                self._failures[provider]["count"] = 0

    def is_open(self, provider: str) -> bool:
        with self._lock:
            if provider not in self._failures:
                return False
            failure_data = self._failures[provider]
            if failure_data["count"] >= self.failure_threshold:
                if time.time() - failure_data["last_failure"] < self.recovery_timeout:
                    return True
                else:
                    failure_data["count"] = 0
                    return False
            return False

    def get_status(self) -> dict:
        with self._lock:
            return {
                provider: {
                    "failures": data["count"],
                    "open": data["count"] >= self.failure_threshold,
                    "last_failure": data["last_failure"]
                }
                for provider, data in self._failures.items()
            }


CIRCUIT_BREAKER = CircuitBreaker(failure_threshold=3, recovery_timeout=60)


class FarmaAuditor:
    def __init__(self, config: FarmaConfig):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=self.embeddings,
            collection_name=self.config.collection_name
        )

    def _invoke_with_timeout(self, chain, question: str):
        return chain.invoke(question)

    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Desconocido")
            entidad = doc.metadata.get("entidad", "Desconocida")
            formatted.append(f"--- DOC: {source} ({entidad}) ---\n{doc.page_content}")
        return "\n\n".join(formatted)

    def _get_llm(self, provider_override: str = None):
        provider = provider_override or self.config.llm_provider
        model_name = self.config.MODEL_ALIASES.get(self.config.llm_model, self.config.llm_model)

        if provider == "ollama" and "gemini" in model_name.lower():
            model_name = self.config.MODEL_ALIASES.get("Qwen 2.5", "qwen2.5:0.5b")

        if provider == "ollama":
            print(f"[*] Usando modelo local via Ollama: {model_name}")
            return ChatOllama(
                model=model_name,
                temperature=self.config.temperature,
                timeout=LLM_TIMEOUT
            )
        else:
            print(f"[*] Usando modelo cloud via Gemini: {model_name}")
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=self.config.temperature,
                timeout=20
            )

    def _classify_error(self, provider: str, error: Exception) -> LLMProviderError:
        error_msg = str(error).lower()

        if "rate limit" in error_msg or "429" in error_msg or "overloaded" in error_msg or "too many requests" in error_msg:
            return LLMRateLimitError(provider)
        if "timeout" in error_msg or isinstance(error, TimeoutError):
            return LLMTimeoutError(provider, str(error))
        if "connection" in error_msg or "network" in error_msg or "10061" in error_msg or "10060" in error_msg:
            return LLMConnectionError(provider, str(error))
        if "refused" in error_msg:
            return LLMConnectionError(provider, "Connection refused - is the service running?")

        return LLMProviderError(provider, str(error), is_retryable=True)

    def _load_prompts(self):
        file_path = "src/prompts.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    template = data.get("system_prompt_template", "")
                    rules = "\n".join(data.get("rules", []))
                    return template.replace("{rules}", rules)
            except Exception as e:
                print(f"[!] Error cargando prompts.json: {e}")

        return (
            "Eres un auditor de farmacia estricto. Tu tarea es responder consultas sobre normativas "
            "de obras sociales (PAMI, DIM, COFAER, OSER, OSPA VIAL) usando SOLO el contexto provisto.\n\n"
            "REGLAS CRÍTICAS:\n"
            "1. Si la respuesta no está en el contexto, di: 'No hay información suficiente'.\n"
            "2. NO inventes datos. NO uses conocimiento previo.\n"
            "3. Caso especial OSER: Desde el 01/01/2026 NO se reciben recetas físicas en papel por decreto de OSER.\n"
            "4. Cita siempre la FUENTE y la ENTIDAD al final.\n\n"
            "<contexto>\n"
            "{context}\n"
            "</contexto>"
        )

    def setup_chain(self, provider_override: str = None):
        retriever = self.vectorstore.as_retriever(
            search_type=self.config.search_type,
            search_kwargs={"k": self.config.top_k}
        )

        llm = self._get_llm(provider_override=provider_override)
        system_prompt = self._load_prompts()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])

        return (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )

    def ask_with_fallback(self, question: str, preferred_provider: str = None) -> Tuple[str, str]:
        providers_to_try = []

        if preferred_provider:
            providers_to_try.append(preferred_provider)
            if preferred_provider == "gemini":
                providers_to_try.append("ollama")
            else:
                providers_to_try.append("gemini")
        else:
            providers_to_try = PROVIDER_ORDER.copy()

        last_error = None

        for provider in providers_to_try:
            if CIRCUIT_BREAKER.is_open(provider):
                print(f"[*] Circuit breaker abierto para {provider}, saltando...")
                continue

            try:
                print(f"[*] Intentando con provider: {provider}")
                chain = self.setup_chain(provider_override=provider)
                result = chain.invoke(question)
                print(f"[*] Consulta exitosa con {provider}")
                CIRCUIT_BREAKER.record_success(provider)
                return result, provider
            except Exception as e:
                last_error = e
                classified_error = self._classify_error(provider, e)
                print(f"[!] Error con {provider}: {classified_error}")

                if CIRCUIT_BREAKER.is_open(provider):
                    print(f"[*] Circuit breaker abierto para {provider} tras múltiples fallos")
                else:
                    CIRCUIT_BREAKER.record_failure(provider)

                if not classified_error.is_retryable:
                    raise classified_error
                continue

        raise last_error
