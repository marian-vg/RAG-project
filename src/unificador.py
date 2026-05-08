from typing import Optional, List, Dict, Any, Tuple
from src.config import FarmaConfig
from src.procesador import FarmaProcessor
from src.auditor import FarmaAuditor

class FarmaRAG:
    """Interfaz única (Fachada) para operar el sistema FarmaRAG."""
    
    def __init__(self, config: Optional[FarmaConfig] = None):
        self.config = config or FarmaConfig()
        self.procesador = FarmaProcessor(self.config)
        self._auditor = None

    def ingest(self, clean_first: bool = True):
        """Carga y vectoriza los documentos."""
        self.procesador.process(clean_first=clean_first)
        self._auditor = None

    @property
    def auditor(self):
        if self._auditor is None:
            self._auditor = FarmaAuditor(self.config)
        return self._auditor

    def ask(self, question: str, provider_override: str = None) -> str:
        """Realiza una consulta al auditor con lógica de reintentos y soporte de override."""
        chain = self.auditor.setup_chain(provider_override=provider_override)
        return self.auditor._invoke_chain(chain, question)

    def ask_with_fallback(self, question: str, preferred_provider: str = None):
        """
        Realiza una consulta con fallback automático entre providers.
        Retorna: (respuesta, provider_used)
        """
        return self.auditor.ask_with_fallback(question, preferred_provider=preferred_provider)

    def ask_with_sources(self, question: str, preferred_provider: str = None) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Realiza una consulta con fallback y retorna los documentos fuente usados.
        Retorna: (respuesta, provider_used, source_documents)
        Cada source_document tiene: chunk_text, source, page/titulo/section de metadata
        """
        detected_entity = None
        if self.config.filter_by_entity:
            detected_entity = self.auditor._detect_entity_from_query(question)

        search_kwargs = {
            "k": self.config.top_k,
        }
        if detected_entity:
            search_kwargs["filter"] = {"entidad": detected_entity}

        docs = self.auditor.vectorstore.similarity_search(question, **search_kwargs)
        sources = []
        for doc in docs:
            meta = doc.metadata or {}
            sources.append({
                "chunk_text": doc.page_content,
                "source": meta.get("source", meta.get("titulo", "desconocido")),
                "page": meta.get("page"),
                "section": meta.get("section"),
                "entidad": meta.get("entidad")
            })

        result, provider = self.auditor.ask_with_fallback(question, preferred_provider=preferred_provider)
        return result, provider, sources
