import os
import glob
import re
import shutil
import time
from typing import Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

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
        """Limpieza profunda para reducir ruido en modelos pequeños."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'[-_=*]{4,}', '', text)
        text = re.sub(r'^(OSER:|COFAER:|DIM:|PAMI:|RECETAS OFICIALES EXTRAVIADAS|CIRCULAR|NOTA):\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\(.*\)\s*$', '', text)
        return text.strip()

    def _extract_entity_from_filename(self, filename: str) -> Optional[str]:
        """Heurística rápida para evitar llamadas al LLM."""
        filename_upper = filename.upper()
        entities = ["DIM", "COFAER", "PAMI", "OSPA VIAL", "OSER"]
        for ent in entities:
            if ent in filename_upper:
                return ent
        return None

    def _is_valid_chunk(self, chunk: Document) -> bool:
        """Filtra chunks vacíos o que son solo headers sin contenido real."""
        content = chunk.page_content.strip()
        if not content:
            return False
        if len(content) < 20:
            return False
        return True

    def _detect_entity(self, text: str, filename: str) -> str:
        # 1. Intentar por nombre de archivo
        entidad_rapida = self._extract_entity_from_filename(filename)
        if entidad_rapida:
            print(f"    [+] Entidad detectada por nombre: {entidad_rapida}")
            return entidad_rapida

        # 2. Fallback al LLM (Solo si no se detectó por nombre)
        print(f"    [?] Consultando LLM para identificar entidad en {filename}...")
        llm = ChatGoogleGenerativeAI(model=self.config.generation_model, temperature=0)
        structured_llm = llm.with_structured_output(DocumentMetadata)
        
        sample_text = text[:4000]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en auditoría de farmacia argentina. Tu tarea es identificar la entidad emisora de un documento basándote exclusivamente en su contenido. Las opciones válidas son: DIM, COFAER, PAMI, OSPA VIAL, OSER o DESCONOCIDA. Responde siempre en el formato estructurado solicitado."),
            ("human", "Analiza el documento e identifica la entidad:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        try:
            result = chain.invoke({"text": sample_text})
            return result.entidad
        except Exception as e:
            print(f"    [!] Error identificando entidad con LLM: {e}")
            return "DESCONOCIDA"

    def process(self, clean_first: bool = True):
        """Ejecuta el pipeline de ingesta optimizado."""
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
                loader = UnstructuredPDFLoader(
                    pdf_path, 
                    strategy="fast", 
                    mode="elements",
                    languages=["spa"]
                )
                elements = loader.load()
                
                if not elements: continue
                
                full_text = "\n".join([el.page_content for el in elements])
                entidad = self._detect_entity(full_text, filename)
                
                for el in elements:
                    el.page_content = self._clean_text(el.page_content)
                    el.metadata.update({
                        "source": filename,
                        "entidad": entidad,
                        "fecha_ingesta": time.strftime("%Y-%m-%d")
                    })
                
                chunks = self.text_splitter.split_documents(elements)
                valid_chunks = [c for c in chunks if self._is_valid_chunk(c)]
                all_chunks.extend(valid_chunks)
                if len(chunks) != len(valid_chunks):
                    print(f"    [~] Filtrados {len(chunks) - len(valid_chunks)} chunks invalidos")
                
            except Exception as e:
                print(f"  [!] Error en {filename}: {e}")

        if not all_chunks: return

        if clean_first and os.path.exists(self.config.chroma_path):
            print(f"[*] Limpiando base de datos en {self.config.chroma_path}...")
            shutil.rmtree(self.config.chroma_path)

# Vectorización local
        print(f"[*] Vectorizando {len(all_chunks)} fragmentos localmente...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

        vectorstore = Chroma(
            persist_directory=self.config.chroma_path,
            embedding_function=embeddings,
            collection_name=self.config.collection_name,
            collection_metadata={"hnsw:space": "cosine"}
        )

        # Al ser local, no necesitamos batching con sleeps largos
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            print(f"  [+] Indexando lote {(i//batch_size)+1}/{(len(all_chunks)//batch_size)+1}")
            try:
                vectorstore.add_documents(batch)
            except Exception as e:
                print(f"  [!] Error indexando lote: {e}")
                raise e

        print("[*] Ingesta completada.")
