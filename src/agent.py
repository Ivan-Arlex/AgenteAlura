from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from database import procesar_vector_store
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()
modelo_gemini = os.getenv("MODELO_GEMINI")
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = GoogleGenerativeAI(model=modelo_gemini,
                                 google_api_key=gemini_api_key,  temperature=0.3)

class AgentState(TypedDict, total=False):
    pregunta: str
    contexto: List[str] 
    respuesta: str


retriever = None
vectorstore = None


SYSTEM_PROMPT = """
Eres un asistente experto de BimBam Buy, caracterizado por un trato ágil, 
seguro y amigable. Tu objetivo es resolver consultas utilizando ÚNICAMENTE el {contexto} proporcionado.

#REGLAS DE RESPUESTA:
1. RESPUESTA EXACTA: Responde exclusivamente con la información contenida en el contexto. Si la respuesta no está allí, di que no cuentas con esa información. NO inventes datos.
2. RESPUESTA DIRECTA Y BREVE: Responde de forma directa. Evita introducciones largas o saludos innecesarios. Responde en un máximo de 2 párrafos, puedes incluir una lista de puntos clave.
3. NEGATIVAS: Si debes dar una respuesta negativa, justifica brevemente el motivo con cortesía manteniendo una actitud profesional, servicial y empático.
4. ESTILO Y TONO: Mantén un tono profesional, servicial y empático. Incluye emojis (📦, 🚚, 💳, ✅) de forma estratégica para mantener la cercanía y mejorar la experiencia del usuario.
5. RESPUESTA ANTE AUSENCIA DE INFORMACIÓN: Si no cuentas con el dato, responde de forma natural y amable, diciendo que no dispongo de esa information y redirígelo amablemente hacia temas que sí dominas (políticas de reembolso, logística o tiempos de entrega)."

Pregunta del usuario: {pregunta}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{pregunta}")
])

def inicializar_retriever():

    global retriever, vectorstore

    if retriever is not None:
        return retriever

    if vectorstore is None:
        vectorstore = procesar_vector_store()
        print("Vectorstore cargado correctamente.")
        
    if vectorstore is not None:
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.3, "k": 4}
        )
        print("Retriever inicializado correctamente.")
    
    return retriever

def buscar_contexto(state: AgentState):

    active_retriever = inicializar_retriever()

    if active_retriever is None:
        print("El retriever no está inicializado. Asegúrate de que la base de datos FAISS se haya cargado correctamente.")
        return {
            "contexto": [],
            "respuesta": "Error técnico: El sistema de búsqueda no está disponible temporalmente. Por favor, contacta con el administrador del sistema."}
    
    try:
        documentos = active_retriever.invoke(state["pregunta"])

        textos_encontrados = [doc.page_content for doc in documentos]
        
        return {"contexto": textos_encontrados}
    
    except Exception as e:
        print(f"Error al buscar contexto: {e}")
        return {
            "contexto": [],
            "respuesta": "Error técnico: No se pudo realizar la búsqueda de información. Por favor, inténtalo de nuevo más tarde."}


def generar_respuesta(state: AgentState):

    if (state.get("contexto") is None or not state["contexto"]) and retriever is not None:
        return {"respuesta": "No se encontró información relacionada con tu consulta. Puedo ayudarte con dudas sobre **políticas de reembolso, logística o tiempos de entrega**."}

    if state.get("respuesta") is not None:
        return {"respuesta": state["respuesta"]}
    
    try:
        global llm_gemini, prompt_template

        contexto_unificado = "\n\n".join(state["contexto"])
        
        chain = prompt_template | llm_gemini
        
        respuesta = chain.invoke({
            "contexto": contexto_unificado,
            "pregunta": state["pregunta"]
        })
    
        return {"respuesta": respuesta}

    except ChatGoogleGenerativeAIError as e:
        if "429" in str(e):
            return {"respuesta": "Lo siento, he alcanzado el límite de consultas por hoy. Por favor, inténtalo nuevamente cuando las coutas se recupenren."}
        print(f"Error generando respuesta: {e}")
        return {"respuesta": "Hubo un problema con el servicio de IA. Inténtalo de nuevo en unos momentos."}
    
    except Exception as e:
        print(f"Error generando respuesta: {e}")
        return {"respuesta": "Lo siento, ocurrió un error al generar la respuesta. Por favor, inténtalo de nuevo más tarde."}


