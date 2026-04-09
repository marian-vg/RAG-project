from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from src.config import FarmaConfig

class FarmaAuditor:
    """Clase responsable de la recuperación y generación de respuestas."""
    
    def __init__(self, config: FarmaConfig):
        self.config = config
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.config.embedding_model)
        self.vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=self.embeddings,
            collection_name=self.config.collection_name
        )

    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "Desconocido")
            entidad = doc.metadata.get("entidad", "Desconocida")
            formatted.append(f"--- DOC: {source} ({entidad}) ---\n{doc.page_content}")
        return "\n\n".join(formatted)

    def setup_chain(self):
        """Configura la cadena LCEL."""
        retriever = self.vectorstore.as_retriever(
            search_type=self.config.search_type,
            search_kwargs={"k": self.config.top_k}
        )
        llm = ChatGoogleGenerativeAI(
            model=self.config.generation_model, 
            temperature=self.config.temperature
        )
        
        edge_prompt = self.config.prompt

        if edge_prompt:
            system_prompt = edge_prompt
        else:
            system_prompt = (
                "Si preguntan por recetas fisicas en papel expendidas luego del primero de enero de 2026, NO se reciben por decreto de OSER (Obra Social de Entre Rios), OSER declaro plena utilización de recetas electrónicas en la provincia"
                "Eres un auditor de farmacia estricto y profesional. Tu objetivo es responder consultas "
                "sobre normativas, circulares y manuales de obras sociales (PAMI, DIM, COFAER). "
                "Utiliza ÚNICAMENTE los fragmentos de contexto provistos para responder. "
                "No inventes información ni utilices conocimientos externos. "
                "Al finalizar tu respuesta, cita siempre el nombre del archivo fuente y la entidad mencionada en los metadatos."
                "Si la respuesta no se encuentra en el contexto, di exactamente: "
                "'No hay información suficiente en los documentos cargados para responder esta pregunta.' "
                "\n\n"
                "CONTEXTO:\n"
                "{context}"
            )

        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        
        return (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )
