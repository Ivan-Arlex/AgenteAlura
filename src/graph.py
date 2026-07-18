from agent import buscar_informacion, generar_respuesta, determinar_siguiente_paso, respuesta_error_infraestructura, respuesta_sin_contexto, validar_retriever, AgentState
from langgraph.graph import StateGraph, START, END 
import os

grafo_compilado = None

def crear_grafo():
    """
    Crea un workflow(grafo) de AgentState(que es el estado del grafo) para el flujo de conversación del agente.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("nodo_informacion", buscar_informacion)
    workflow.add_node("nodo_respuesta", generar_respuesta)
    workflow.add_node("nodo_sin_contexto", respuesta_sin_contexto)
    workflow.add_node("nodo_error_tecnico", respuesta_error_infraestructura)

    workflow.add_conditional_edges(START, validar_retriever, {
        "error de infraestructura": "nodo_error_tecnico",
        "continuar busqueda": "nodo_informacion"
    })
    workflow.add_conditional_edges("nodo_informacion", determinar_siguiente_paso, {
        "error en busqueda": "nodo_sin_contexto",
        "contexto disponible": "nodo_respuesta"
    })
    workflow.add_edge("nodo_respuesta", END)
    workflow.add_edge("nodo_sin_contexto", END)
    workflow.add_edge("nodo_error_tecnico", END)

    return workflow.compile()




def generar_visualizacion(grafo):
    """Genera y guarda la imagen del grafo dentro de la carpeta assets."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")
        
        os.makedirs(assets_dir, exist_ok=True)
        
        ruta_guardado = os.path.join(assets_dir, "grafo_flujo.png")
        
        png_data = grafo.get_graph().draw_mermaid_png()
        with open(ruta_guardado, "wb") as f:
            f.write(png_data)
            
        print(f"Imagen del grafo generada correctamente en: {ruta_guardado}")
    except Exception as e:
        print(f"Error al generar la imagen: {e}")

def obtener_grafo():
    """
    Retorna la instancia única del grafo compilado (Singleton).
    Se compila una sola vez cuando se solicita por primera vez.
    """
    global grafo_compilado
    if grafo_compilado is None:
        grafo_compilado = crear_grafo()

        if os.getenv("GENERAR_GRAFO") == "True":
            generar_visualizacion(grafo_compilado)

    return grafo_compilado

def procesar_consulta(pregunta_usuario: str)-> str:
    """
    Función principal para procesar la consulta del usuario.
    - Obtiene la instancia del grafo de la funcion obtener_grafo (patron Singleton).
    """

    print(f"\n--- Procesando consulta: '{pregunta_usuario}' ---")

    grafo = obtener_grafo()
    
    estado_inicial = {"pregunta": pregunta_usuario}
    
    resultado = grafo.invoke(estado_inicial)
    
    print("")
    print("-"*50)
    print("Respuesta final del agente:")
    print(resultado.get("respuesta", "No se obtuvo respuesta."))
    return resultado.get("respuesta", "No se obtuvo respuesta.")

