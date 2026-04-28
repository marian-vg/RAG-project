import json
import os
import time
from typing import List, Tuple, Optional
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
    """Excepción base para errores de provider LLM."""
    def __init__(self, provider: str, message: str, is_retryable: bool = True):
        self.provider = provider
        self.is_retryable = is_retryable
        super().__init__(message)


class LLMRateLimitError(LLMProviderError):
    """Error específico para rate limiting."""
    def __init__(self, provider: str, message: str = "Rate limit exceeded"):
        super().__init__(provider, message, is_retryable=True)


class LLMConnectionError(LLMProviderError):
    """Error de conexión a provider."""
    def __init__(self, provider: str, message: str):
        super().__init__(provider, message, is_retryable=True)


class LLMTimeoutError(LLMProviderError):
    """Error de timeout."""
    def __init__(self, provider: str, message: str = "Provider timeout"):
        super().__init__(provider, message, is_retryable=True)


class FarmaAuditor:
    """Clase responsable de la recuperación y generación de respuestas."""

    def __init__(self, config: FarmaConfig):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=self.embeddings,
            collection_name=self.config.collection_name
        )

    def _invoke_with_timeout(self, chain, question: str):
        """Invoca el chain con manejo de errores específico por provider."""
        return chain.invoke(question)

    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Desconocido")
            entidad = doc.metadata.get("entidad", "Desconocida")
            formatted.append(f"--- DOC: {source} ({entidad}) ---\n{doc.page_content}")
        return "\n\n".join(formatted)

    def _get_llm(self, provider_override: str = None):
        """Fábrica de modelos según configuración, resolviendo alias y permitiendo overrides."""
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
        """Clasifica el error según el provider y el tipo de excepción."""
        error_msg = str(error).lower()
        error_type = type(error).__name__

        if provider == "gemini":
            if isinstance(error, RateLimitError):
                return LLMRateLimitError(provider)
            if "timeout" in error_msg or isinstance(error, TimeoutError):
                return LLMTimeoutError(provider, str(error))
            if "connection" in error_msg or "network" in error_msg or "10061" in error_msg or "10060" in error_msg:
                return LLMConnectionError(provider, str(error))
            if "overloaded" in error_msg or "429" in error_msg or "503" in error_msg:
                return LLMRateLimitError(provider)
        else:
            if "timeout" in error_msg or isinstance(error, TimeoutError):
                return LLMTimeoutError(provider, str(error))
            if "connection" in error_msg or "network" in error_msg or "10061" in error_msg or "10060" in error_msg:
                return LLMConnectionError(provider, str(error))
            if "refused" in error_msg:
                return LLMConnectionError(provider, "Connection refused - is the service running?")

        return LLMProviderError(provider, str(error), is_retryable=True)

    def _load_prompts(self):
        """Carga prompts desde archivo JSON con fallback."""
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
        """Configura la cadena LCEL con soporte para override de proveedor."""
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
        """
        Ejecuta la consulta con fallback automático entre providers.
        Retorna: (respuesta, provider_used)
        Si ambos fallan, levanta la última excepción.
        """
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
            try:
                print(f"[*] Intentando con provider: {provider}")
                chain = self.setup_chain(provider_override=provider)
                result = chain.invoke(question)
                print(f"[*] Consulta exitosa con {provider}")
                return result, provider
            except Exception as e:
                last_error = e
                classified_error = self._classify_error(provider, e)
                print(f"[!] Error con {provider}: {classified_error}")
                if not classified_error.is_retryable:
                    raise classified_error
                continue

        raise last_error