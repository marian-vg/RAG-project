import os
import glob
import re
import shutil
import time
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores.utils import filter_complex_metadata

from src.config import FarmaConfig

load_dotenv()

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
        time.sleep(2)
        llm = ChatGoogleGenerativeAI(model=self.config.generation_model, temperature=0)
        structured_llm = llm.with_structured_output(DocumentMetadata)
        
        sample_text = text[:4000]

        

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en auditoría de farmacia argentina. Tu tarea es identificar la entidad emisora de un documento basándote exclusivamente en su contenido. Las opciones válidas son: DIM (Departamento Integral de Medicamentos), COFAER (Colegio Farmacéutico de Entre Ríos), PAMI, OSPA VIAL, OSER o DESCONOCIDA. Responde siempre en el formato estructurado solicitado."),
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
        """Ejecuta el pipeline de ingesta con batching inteligente para evitar cuotas."""
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
                # Especificamos languages=["spa"] y restauramos estrategia/modo
                loader = UnstructuredPDFLoader(
                    pdf_path, 
                    strategy="fast", 
                    mode="elements",
                    languages=["spa"]
                )
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

        # Limpiar metadatos
        all_chunks = filter_complex_metadata(all_chunks)
        
        # Elimiación segura de DB previa
        if clean_first and os.path.exists(self.config.chroma_path):
            print(f"[*] Limpiando base de datos en {self.config.chroma_path}...")
            for _ in range(5):
                try:
                    shutil.rmtree(self.config.chroma_path)
                    break
                except PermissionError:
                    time.sleep(2)

        # Vectorización con Batching
        print(f"[*] Vectorizando {len(all_chunks)} fragmentos en lotes de 20...")
        embeddings = GoogleGenerativeAIEmbeddings(model=self.config.embedding_model)
        
        vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=embeddings,
            collection_name=self.config.collection_name
        )
        
        batch_size = 20
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            print(f"  [+] Indexando lote {(i//batch_size)+1}/{(len(all_chunks)//batch_size)+1}")
            try:
                vectorstore.add_documents(batch)
                if i + batch_size < len(all_chunks):
                    time.sleep(25)
            except Exception as e:
                if "429" in str(e):
                    print("  [!] Límite alcanzado. Esperando 60s extra...")
                    time.sleep(60)
                    vectorstore.add_documents(batch)
                else:
                    raise e
        
        print("[*] Ingesta completada.")
