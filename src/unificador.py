from typing import Optional
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
