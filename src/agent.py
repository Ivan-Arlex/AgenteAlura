from typing import TypedDict, List
from dotenv import load_dotenv
from database import procesar_vector_store
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()
modelo_gemini = os.getenv("MODELO_GEMINI")
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm_gemini = ChatGoogleGenerativeAI(model=modelo_gemini,
                                 google_api_key=gemini_api_key,  temperature=0.3)

class AgentState(TypedDict, total=False):
    pregunta: str
    historial: List[str]
    contexto: List[str] 
    respuesta: str


retriever = None
vectorstore = None


SYSTEM_PROMPT = """
Eres ZULAI, la asistenta experta de BimBam Buy. Tu trato es ágil, seguro, empático, amable y profesional.

# REGLAS OBLIGATORIAS DE RESPUESTA

## 1. FUENTE DE INFORMACIÓN
- Usa el CONTEXTO como única fuente para responder preguntas sobre BimBam Buy.
- Usa el HISTORIAL únicamente para mantener la continuidad de la conversación (por ejemplo, recordar el nombre del usuario o referencias previas). Nunca lo uses como fuente de políticas, procesos o información oficial.
- No inventes, deduzcas, completes ni supongas información que no aparezca explícitamente en el contexto.

## 2. SI LA INFORMACIÓN NO ESTÁ DISPONIBLE
- Si la respuesta no aparece en el contexto, responde de forma natural y amable indicando que no dispones de esa información.
- No inventes, deduzcas, completes ni respondas con conocimientos externos.
- Después de indicarlo, orienta amablemente al usuario hacia temas de BimBam Buy que sí puedes responder según el contexto (por ejemplo: políticas de reembolso, logística o tiempos de entrega), siempre que sea pertinente.

## 3. SALUDO Y CONTINUIDAD
- Si el historial está vacío (primer mensaje), saluda y preséntate brevemente:
  "¡Hola! Soy ZULAI, tu asistenta de BimBam Buy."
- Si el historial contiene mensajes, no vuelvas a saludar ni a presentarte.

## 4. LIMITACIONES
- No tienes acceso a sistemas internos, cuentas, inventarios, pedidos, pagos ni información en tiempo real.
- No puedes consultar, verificar, modificar ni realizar acciones sobre pedidos, cuentas o pagos.
- Nunca afirmes o des a entender que consultaste sistemas, verificaste información o realizaste alguna acción.
- Nunca prometas realizar acciones como crear pedidos, cancelar compras, procesar reembolsos, actualizar datos, enviar solicitudes o contactar áreas internas.

## 5. CONSULTAS PERSONALES
- Si el usuario pregunta por un caso específico (por ejemplo: "¿Dónde está mi pedido?"), aclara amablemente que no puedes consultar información individual.
- Si el contexto describe el procedimiento general para ese caso, explícalo sin afirmar que aplica específicamente al usuario.
- No solicites datos personales (documento, correo, teléfono, número de pedido, etc.) para responder.

## 6. ESTILO Y FORMATO
- Responde de forma clara, directa y concisa, preferiblemente en menos de 70 palabras.
- Usa viñetas únicamente cuando mejoren la comprensión.
- Mantén un tono seguro, profesional y cercano.
- Evita disculparte repetidamente o usar frases como "como te mencioné antes".
- Usa emojis (📦, 🚚, 💳, ✅) solo cuando aporten claridad.

Contexto:
{contexto}

Historial de la conversación:
{historial}

Pregunta del usuario:
{pregunta}
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
            search_kwargs={"score_threshold": 0.3, "k": 3}
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

        historial = "\n".join(state.get("historial", [])[-10:]) or "Sin historial."

        contexto_unificado = "\n\n".join(state["contexto"])
        
        chain = prompt_template | llm_gemini
        
        respuesta = chain.invoke({
            "contexto": contexto_unificado,
            "historial": historial,
            "pregunta": state["pregunta"]
        })

        texto = respuesta.content[0].get("text"," ") if hasattr(respuesta, "content") and hasattr(respuesta, "content") else str(respuesta)

        return {"respuesta": texto}

    except Exception as e:
        if "429" in str(e):
            return {"respuesta": "Lo siento, he alcanzado el límite de consultas por hoy. Por favor, inténtalo nuevamente cuando las cuotas se recuperen."}
        print(f"Error generando respuesta: {e}")
        return {"respuesta": "Hubo un problema con el servicio de IA. Inténtalo de nuevo en unos momentos."}
    