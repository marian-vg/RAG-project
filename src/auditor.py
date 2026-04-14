import json
import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from src.config import FarmaConfig

from tenacity import retry, stop_after_attempt, wait_exponential

class FarmaAuditor:
    """Clase responsable de la recuperación y generación de respuestas."""
    
    def __init__(self, config: FarmaConfig):
        self.config = config
        # Cambio a embeddings locales usando HuggingFace (MiniLM es ligero y eficiente)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=self.embeddings,
            collection_name=self.config.collection_name
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _invoke_chain(self, chain, question: str):
        """Envuelve la ejecución de la cadena en una lógica de reintentos."""
        return chain.invoke(question)

    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Desconocido")
            entidad = doc.metadata.get("entidad", "Desconocida")
            formatted.append(f"--- DOC: {source} ({entidad}) ---\n{doc.page_content}")
        return "\n\n".join(formatted)

    def _get_llm(self):
        """Fábrica de modelos según configuración, resolviendo alias."""
        
        model_name = self.config.MODEL_ALIASES.get(self.config.llm_model, self.config.llm_model)
        
        if self.config.llm_provider == "ollama":
            print(f"[*] Usando modelo local via Ollama: {model_name} (Alias: {self.config.llm_model})")
            return ChatOllama(
                model=model_name,
                temperature=self.config.temperature
            )
        else:
            print(f"[*] Usando modelo cloud via Gemini: {model_name} (Alias: {self.config.llm_model})")
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=self.config.temperature
            )

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
        
        # Fallback si falla la carga o el archivo no existe
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

    def setup_chain(self):
        """Configura la cadena LCEL con prompts estructurados para modelos pequeños."""
        retriever = self.vectorstore.as_retriever(
            search_type=self.config.search_type,
            search_kwargs={"k": self.config.top_k}
        )
        
        llm = self._get_llm()
        system_prompt = self._load_prompts()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        
        return (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )
