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
    """Configura y retorna la cadena RAG completa."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
    
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
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def modo_interactivo():
    """Ejecuta el sistema RAG en un bucle infinito para consultas iterativas."""
    print("\n" + "="*60)
    print("SISTEMA DE AUDITORÍA FARMARAG - MODO INTERACTIVO")
    print("Escribe 'salir' o 'exit' para finalizar.")
    print("="*60)
    
    # Pre-cargamos la cadena para mayor velocidad en las respuestas
    chain = get_rag_chain()
    
    while True:
        pregunta = input("\n[?] Ingrese su consulta: ").strip()
        
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("[*] Cerrando sesión de auditoría. ¡Hasta luego!")
            break
            
        if not pregunta:
            continue
            
        print("[*] Consultando documentos...")
        try:
            respuesta = chain.invoke(pregunta)
            print("\n" + "-"*30)
            print("RESPUESTA:")
            print("-"*30)
            print(respuesta)
            print("-"*30)
        except Exception as e:
            print(f"[!] Ocurrió un error durante la consulta: {e}")

if __name__ == "__main__":
    modo_interactivo()
