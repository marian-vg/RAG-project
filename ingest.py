import os
import glob
import re
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Configuración de rutas y nombres
DOCS_DIR = "documentos"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "farmarag_collection"

class DocumentMetadata(BaseModel):
    entidad: Literal["DIM", "COFAER", "PAMI", "DESCONOCIDA"] = Field(
        description="La entidad emisora o relacionada con el documento. DIM (Departamento Integral de Medicamentos), COFAER (Colegio Farmacéutico de Entre Ríos) o PAMI."
    )

def get_entidad(text: str) -> str:
    """Detecta la entidad del texto del documento usando Gemini en Español."""
    # Usando el modelo especificado en el PLAN.md que está disponible
    llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite-preview", temperature=0)
    structured_llm = llm.with_structured_output(DocumentMetadata)
    
    # Usamos los primeros 4000 caracteres para una identificación robusta
    sample_text = text[:4000]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto en auditoría de farmacia argentina. Tu tarea es identificar la entidad emisora de un documento basándote exclusivamente en su contenido. Las opciones válidas son: DIM (Departamento Integral de Medicamentos), COFAER (Colegio Farmacéutico de Entre Ríos), PAMI o DESCONOCIDA. Responde siempre en el formato estructurado solicitado."),
        ("human", "Analiza el siguiente fragmento de documento legal/circular de farmacia e identifica la entidad:\n\n{text}")
    ])
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"text": sample_text})
        return result.entidad
    except Exception as e:
        print(f"[!] Error identificando entidad: {e}")
        return "DESCONOCIDA"

def clean_text(text: str) -> str:
    """Limpieza básica de texto: elimina saltos de línea excesivos y espacios múltiples."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def ingest_docs():
    """Fases 1, 2 y 3: Ingesta, Fragmentación (Chunking) y Vectorización."""
    
    pdf_files = glob.glob(os.path.join(DOCS_DIR, "*.pdf"))
    if not pdf_files:
        print("[!] No se encontraron archivos PDF en el directorio de documentos.")
        return

    print(f"[*] Procesando {len(pdf_files)} archivos: {[os.path.basename(f) for f in pdf_files]}")

    all_chunks = []
    
    # Configuración del divisor de texto según Fase 2 del PLAN.md
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # Fase 1: Ingestión
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"\n[1] Cargando documento: {filename}...")
        
        try:
            # Se usa UnstructuredPDFLoader para preservar estructura (tablas, párrafos)
            loader = UnstructuredPDFLoader(pdf_path)
            docs = loader.load()
            
            if not docs:
                print(f"[!] No se pudo extraer contenido de {filename}")
                continue
                
            # Combinamos el contenido para detectar la entidad una sola vez por archivo
            full_text = "\n".join([doc.page_content for doc in docs])
            entidad = get_entidad(full_text)
            print(f"[*] Entidad detectada: {entidad}")
            
            # Limpieza y preparación de metadatos
            for doc in docs:
                doc.page_content = clean_text(doc.page_content)
                doc.metadata.update({
                    "source": filename,
                    "entidad": entidad,
                    "fecha_ingesta": "2026-04-08",
                    "idioma": "es"
                })
            
            # Fase 2: Fragmentación Semántica
            chunks = text_splitter.split_documents(docs)
            print(f"[2] Generados {len(chunks)} fragmentos (chunks) para {filename}")
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"[!] Error procesando {filename}: {e}")

    if not all_chunks:
        print("[!] No se generaron fragmentos. Abortando vectorización.")
        return

    # Fase 3: Vectorización (Embeddings y ChromaDB)
    print(f"\n[3] Vectorizando {len(all_chunks)} fragmentos en {CHROMA_PATH}...")
    # Usando el nombre exacto del modelo de embeddings disponible en la API
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    try:
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PATH,
            collection_name=COLLECTION_NAME
        )
        print("[*] Base de datos vectorial creada y persistida con éxito.")
    except Exception as e:
        print(f"[!] Error durante la vectorización: {e}")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("[!] Error: No se encontró GOOGLE_API_KEY en el entorno.")
    else:
        ingest_docs()
