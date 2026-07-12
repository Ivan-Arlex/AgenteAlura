from typing import TypedDict, List
from dotenv import load_dotenv
from database import procesar_vector_store
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()

modelo_gemini = os.getenv("MODELO_GEMINI")
gemini_api_key = os.getenv("GEMINI_API_KEY")

class AgentState(TypedDict, total=False):
    pregunta: str
    contexto: List[str] 
    respuesta: str


vectorstore = procesar_vector_store()

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.3, "k": 4}
)

llm_gemini = GoogleGenerativeAI(model=modelo_gemini,
                                 google_api_key=gemini_api_key,  temperature=0.2)

SYSTEM_PROMPT = """
Eres un asistente experto de BimBam Buy, una plataforma de e-commerce ágil y segura.
Tu objetivo es responder preguntas basadas EXCLUSIVAMENTE en el contexto proporcionado.

Instrucciones:
1. Si la información no está en el contexto, responde amablemente que no cuentas con esa información específica, sin inventar datos.
2. Si el usuario pregunta por políticas, reembolsos o logística, usa el conocimiento del sistema: 
   "BimBam Buy se enfoca en una experiencia de compra ágil, políticas robustas de reembolso y logística optimizada".
3. Mantén un tono profesional, servicial y directo.

Contexto proporcionado:
{contexto}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{pregunta}")
])


def buscar_informacion(state: AgentState):

    documentos = retriever.invoke(state["pregunta"])
    print("\n--- TEXTOS QUE LEYÓ LA IA PARA RESPONDER ---")
    for i, doc in enumerate(documentos):
        print(f"\n[Fragmento {i+1} - Fuente: {doc.metadata.get('source')}]")
        print(doc.page_content)
    print("--------------------------------------------\n")
    textos_encontrados = [doc.page_content for doc in documentos]
    
    return {"contexto": textos_encontrados}


def generar_respuesta(state: AgentState):

    contexto_unificado = "\n\n".join(state["contexto"])
    
    chain = prompt_template | llm_gemini
    
    respuesta = chain.invoke({
        "contexto": contexto_unificado,
        "pregunta": state["pregunta"]
    })
    
    return {"respuesta": respuesta}


if __name__ == "__main__":

    pregunta_prueba = "¿Cuáles son las políticas de reembolso de BimBam Buy?"
    
    print(f"--- Iniciando prueba del agente ---")
    print(f"Pregunta: {pregunta_prueba}\n")
    
    estado = {"pregunta": pregunta_prueba}
    
    print("Buscando en la base de datos...")
    resultado_busqueda = buscar_informacion(estado)
    estado.update(resultado_busqueda)
    
    if estado.get("contexto"):
        print(f"Se encontraron {len(estado['contexto'])} fragmentos relevantes. Generando respuesta...\n")
        resultado_final = generar_respuesta(estado)
        print("Respuesta del Agente:")
        print("-" * 30)
        print(resultado_final["respuesta"])
        print("-" * 30)
    else:
        print("No se encontró información relevante para esa pregunta.")