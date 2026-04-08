import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

load_dotenv()

# Configuración
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "farmarag_collection"
MODEL_NAME = "models/gemini-3.1-flash-lite-preview"
EMBEDDING_MODEL = "models/gemini-embedding-001"

def format_docs(docs: List[Document]) -> str:
    """Formatea los documentos para el prompt, incluyendo la fuente y entidad."""
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "Desconocido")
        entidad = doc.metadata.get("entidad", "Desconocida")
        content = f"--- DOCUMENTO: {source} (Entidad: {entidad}) ---\n{doc.page_content}"
        formatted.append(content)
    return "\n\n".join(formatted)

def get_rag_chain():
    """Configura y retorna la cadena RAG completa (Fase 4 y 5)."""
    
    # Inicializar Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    
    # Cargar Vector Store (Fase 4)
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # Configurar Retriever (Fase 4: Top-K=4)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Configurar LLM (Fase 5)
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
    
    # Ingeniería de Prompt (Fase 5)
    system_prompt = (
        "Eres un auditor de farmacia estricto y profesional. Tu objetivo es responder consultas "
        "sobre normativas, circulares y manuales de obras sociales (PAMI, DIM, COFAER). "
        "Utiliza ÚNICAMENTE los fragmentos de contexto provistos para responder. "
        "Si la respuesta no se encuentra en el contexto, di exactamente: "
        "'No hay información suficiente en los documentos cargados para responder esta pregunta.' "
        "No inventes información ni utilices conocimientos externos. "
        "Al finalizar tu respuesta, cita siempre el nombre del archivo fuente y la entidad mencionada en los metadatos."
        "\n\n"
        "CONTEXTO:\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    # Cadena LCEL (Fase 5)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def consultar(pregunta: str):
    """Ejecuta una consulta y muestra la respuesta."""
    print(f"\n[?] Pregunta: {pregunta}")
    print("[*] Buscando en la base de datos y generando respuesta...")
    
    chain = get_rag_chain()
    respuesta = chain.invoke(pregunta)
    
    print("\n" + "="*50)
    print("RESPUESTA DEL AUDITOR:")
    print("="*50)
    print(respuesta)
    print("="*50 + "\n")

if __name__ == "__main__":
    # Prueba rápida si se ejecuta directamente
    test_query = "¿Cuáles son los requisitos para las recetas de veterinarios según DIM?"
    consultar(test_query)
