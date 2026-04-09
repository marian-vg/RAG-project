import os
import glob
import re
import shutil
import time
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata

load_dotenv()

class FarmaConfig(BaseModel):
    """Configuración centralizada para el motor FarmaRAG."""
    docs_dir: str = "documentos"
    chroma_path: str = "chroma_db"
    collection_name: str = "farmarag_collection"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "models/gemini-embedding-2-preview"
    generation_model: str = "models/gemini-3.1-flash-lite-preview"
    temperature: float = 0.0
    top_k: int = 4

class DocumentMetadata(BaseModel):
    """Esquema para la detección de entidades por contenido."""
    entidad: Literal["DIM", "COFAER", "PAMI", "OSPA VIAL", "OSER", "DESCONOCIDA"] = Field(
        description="La entidad emisora o relacionada con el documento."
    )

class FarmaProcessor:
    """Clase responsable de la ingesta y procesamiento de documentos."""
    
    def __init__(self, config: FarmaConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _detect_entity(self, text: str) -> str:
        llm = ChatGoogleGenerativeAI(model=self.config.generation_model, temperature=0)
        structured_llm = llm.with_structured_output(DocumentMetadata)
        
        sample_text = text[:4000]
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en auditoría de farmacia argentina. Identifica la entidad emisora: DIM, COFAER, PAMI, OSPA VIAL, OSER o DESCONOCIDA."),
            ("human", "Analiza el documento e identifica la entidad:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        try:
            result = chain.invoke({"text": sample_text})
            return result.entidad
        except Exception as e:
            print(f"[!] Error identificando entidad: {e}")
            return "DESCONOCIDA"

    def process(self, clean_first: bool = True):
        """Ejecuta el pipeline completo de ingesta."""
        pdf_files = glob.glob(os.path.join(self.config.docs_dir, "*.pdf"))
        if not pdf_files:
            print(f"[!] No se encontraron PDFs en {self.config.docs_dir}")
            return

        print(f"[*] Procesando {len(pdf_files)} archivos con Chunk Size: {self.config.chunk_size}")
        all_chunks = []

        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            print(f"  -> Cargando: {filename}")
            
            try:
                loader = UnstructuredPDFLoader(pdf_path, strategy="fast", mode="elements")
                elements = loader.load()
                
                if not elements: continue
                
                full_text = "\n".join([el.page_content for el in elements])
                entidad = self._detect_entity(full_text)
                
                for el in elements:
                    el.page_content = self._clean_text(el.page_content)
                    el.metadata.update({
                        "source": filename,
                        "entidad": entidad,
                        "fecha_ingesta": time.strftime("%Y-%m-%d")
                    })
                
                chunks = self.text_splitter.split_documents(elements)
                all_chunks.extend(chunks)
                
            except Exception as e:
                print(f"  [!] Error en {filename}: {e}")

        if not all_chunks: return

        # Limpiar metadatos y persistencia
        all_chunks = filter_complex_metadata(all_chunks)
        if clean_first and os.path.exists(self.config.chroma_path):
            shutil.rmtree(self.config.chroma_path)

        # Vectorización
        print(f"[*] Vectorizando {len(all_chunks)} fragmentos...")
        embeddings = GoogleGenerativeAIEmbeddings(model=self.config.embedding_model)
        
        vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=embeddings,
            collection_name=self.config.collection_name
        )
        
        batch_size = 50
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            vectorstore.add_documents(batch)
            if i + batch_size < len(all_chunks):
                time.sleep(30)
        
        print("[*] Ingesta completada con éxito.")

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
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.config.top_k})
        llm = ChatGoogleGenerativeAI(
            model=self.config.generation_model, 
            temperature=self.config.temperature
        )
        
        system_prompt = (
            "Eres un auditor de farmacia estricto. Responde basándote ÚNICAMENTE en el contexto. "
            "Si no está, di que no hay información suficiente. Cita siempre la fuente y entidad.\n\n"
            "CONTEXTO:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        
        return (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt | llm | StrOutputParser()
        )

class FarmaRAG:
    """Interfaz única (Fachada) para operar el sistema FarmaRAG."""
    
    def __init__(self, config: Optional[FarmaConfig] = None):
        self.config = config or FarmaConfig()
        self.processor = FarmaProcessor(self.config)
        self._auditor = None

    def ingest(self, clean_first: bool = True):
        """Carga y vectoriza los documentos."""
        self.processor.process(clean_first=clean_first)
        # Forzar recarga del auditor tras nueva ingesta
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
