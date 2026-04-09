from typing import Optional
from src.config import FarmaConfig
from src.procesador import FarmaProcessor
from src.auditor import FarmaAuditor

class FarmaRAG:
    """Interfaz única (Fachada) para operar el sistema FarmaRAG."""
    
    def __init__(self, config: Optional[FarmaConfig] = None):
        self.config = config or FarmaConfig()
        self.processor = FarmaProcessor(self.config)
        self._auditor = None

    def ingest(self, clean_first: bool = True):
        """Carga y vectoriza los documentos."""
        self.processor.process(clean_first=clean_first)
        self._auditor = None

    @property
    def auditor(self):
        if self._auditor is None:
            self._auditor = FarmaAuditor(self.config)
        return self._auditor

    def ask(self, question: str) -> str:
        """Realiza una consulta al auditor."""
        chain = self.auditor.setup_chain()
        return chain.invoke(question)
