import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from graph import procesar_consulta

# ==========================================
# Configuración de la página (Ancho completo)
# ==========================================
st.set_page_config(
    page_title="BimBam Buy",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Encontrar las rutas correctas para las imágenes (dentro de la carpeta assets)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(base_dir, "assets", "logo.png")
carrito_path = os.path.join(base_dir, "assets", "carrito.png")

# Ruta dinámica para buscar los documentos
BASE_DIR = Path(__file__).resolve().parent
carpeta_docs = Path(BASE_DIR, "docs")

# ==========================================
# CSS de Alta Fidelidad (Estilo Futurista Azul Eléctrico)
# ==========================================
st.markdown("""
<style>
/* Fondo general */
.stApp {
    background-color: #030914 !important;
    background-image: radial-gradient(circle at 50% 50%, #071730 0%, #030914 100%) !important;
    color: #ffffff;
}

/* Ocultar barra superior por defecto de Streamlit */
header, footer {visibility: hidden;}

/* 1. Bloqueamos el scroll de la página completa */
html, body, .stApp, .main, [data-testid="stAppViewBlockContainer"] {
    height: 100vh !important;
    overflow: hidden !important;
}

/* Ajuste de margen superior para que no se pegue arriba */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}

/* 2. Dejamos congeladas las columnas 1 (izquierda) y 3 (derecha) */
div[data-testid="column"]:nth-of-type(1),
div[data-testid="column"]:nth-of-type(3) {
    max-height: 80vh !important;
    overflow: hidden !important;
}

/* 3. Activamos el scroll únicamente en la columna 2 (el chat) */
div[data-testid="column"]:nth-of-type(2) {
    max-height: 80vh !important;
    overflow-y: auto !important;
    padding-right: 15px !important;
}

/* Personalización del scroll de la columna central */
div[data-testid="column"]:nth-of-type(2)::-webkit-scrollbar {
    width: 6px !important;
}
div[data-testid="column"]:nth-of-type(2)::-webkit-scrollbar-track {
    background: transparent !important;
}
div[data-testid="column"]:nth-of-type(2)::-webkit-scrollbar-thumb {
    background: #1d4ed8 !important;
    border-radius: 10px !important;
}

/* Botones superiores */
.top-btn {
    background-color: rgba(25, 42, 70, 0.3) !important;
    border: 1px solid #1e3a60 !important;
    color: #8da2c0 !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    font-size: 14px !important;
    transition: all 0.3s ease;
}
.top-btn:hover {
    border-color: #38bdf8 !important;
    color: #ffffff !important;
    box-shadow: 0px 0px 10px rgba(56, 189, 248, 0.4);
}

/* Tarjetas de Documentos RAG (Columna Izquierda) */
.doc-card {
    background: rgba(13, 27, 49, 0.4);
    border: 1px solid rgba(30, 58, 96, 0.6);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.doc-icon-container {
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: rgba(30, 58, 96, 0.3);
}
.doc-details {
    flex-grow: 1;
}
.doc-title {
    font-weight: 600;
    font-size: 14px;
    color: #ffffff;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
}
.doc-meta {
    font-size: 11px;
    color: #64748b;
    display: flex;
    justify-content: space-between;
}
.doc-ext {
    font-weight: bold;
    color: #38bdf8;
}

/* Botones de sugerencia rápidos */
div.stButton > button {
    background-color: rgba(13, 27, 49, 0.5) !important;
    border: 1px solid rgba(30, 58, 96, 0.8) !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    width: 100% !important;
    padding: 10px !important;
    font-size: 13px !important;
    transition: all 0.2s ease-in-out !important;
}
div.stButton > button:hover {
    border-color: #38bdf8 !important;
    color: #ffffff !important;
    background-color: rgba(30, 58, 96, 0.4) !important;
    box-shadow: 0px 0px 8px rgba(56, 189, 248, 0.2);
}

/* Estilo para los mensajes del chat */
div[data-testid="stChatMessage"] {
    background-color: rgba(13, 27, 49, 0.4) !important;
    border: 1px solid rgba(30, 58, 96, 0.5) !important;
    border-radius: 15px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
}
div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    color: #e2e8f0 !important;
}

/* Caja del chat */
[data-testid="stChatInput"]{
    background: #ffffff !important;
    border: 2px solid #1d4ed8 !important;
    border-radius: 16px !important;
}

/* Área donde escribes */
[data-testid="stChatInput"] textarea{
    color: #000000 !important;
    background: #ffffff !important;
    caret-color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder{
    color: #6b7280 !important;
}

/* Columna Derecha Info Box */
.info-box {
    background: rgba(13, 27, 49, 0.3);
    border: 1px solid rgba(30, 58, 96, 0.4);
    border-radius: 16px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Inicialización de historial y estado
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Guardar pregunta de sugerencia cliqueada
if "sugerencia_seleccionada" not in st.session_state:
    st.session_state.sugerencia_seleccionada = None

# ==========================================
# Encabezado Superior (Logo e Información del Agente)
# ==========================================
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    sub_col1, sub_col2 = st.columns([0.15, 2])
    with sub_col1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=55)
        else:
            st.write("🛡️")
    with sub_col2:
        st.markdown(
            "<h2 style='margin:0; padding:0; color:#ffffff; font-size:24px; font-weight:800;'>BIMBAM BUY</h2>"
            "<p style='margin:0; padding:0; color:#38bdf8; font-size:14px;'>Agente Inteligente</p>", 
            unsafe_allow_html=True
        )

with col_header_right:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Limpiar chat", key="btn_limpiar_chat"):
            st.session_state.messages = []
            st.session_state.sugerencia_seleccionada = None
            st.rerun()
    with c2:
        st.button("⚙️ Ajustes", key="btn_ajustes")

st.markdown("<hr style='border:0; height:1px; background:linear-gradient(to right, #1e3a60, rgba(30,58,96,0)); margin-top:15px; margin-bottom:25px;'>", unsafe_allow_html=True)

# ==========================================
# Diseño Principal en Tres Columnas
# ==========================================
col_izq, col_centro, col_der = st.columns([1, 2.2, 1], gap="medium")

# ----------------- COLUMNA IZQUIERDA: Documentos RAG (Dinámicos) -----------------
with col_izq:
    st.markdown("<h3 style='color:#38bdf8; font-size:18px; margin-bottom:5px;'>Documentos (RAG)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-bottom:15px;'>Fuentes detectadas.</p>", unsafe_allow_html=True)
    
    # Lectura dinámica de la carpeta 'docs'
    documentos_encontrados = []
    
    # Definir iconos según extensión
    ext_icons = {
        ".pdf": "📕",
        ".xlsx": "📗",
        ".xls": "📗",
        ".csv": "📗",
        ".txt": "📘",
        ".docx": "📘",
    }
    
    if carpeta_docs.exists() and carpeta_docs.is_dir():
        # Listar archivos omitiendo temporales u ocultos
        archivos = [f for f in carpeta_docs.iterdir() if f.is_file() and not f.name.startswith(".")]
        
        for file_path in archivos:
            ext = file_path.suffix.lower()
            icon = ext_icons.get(ext, "📙") # Icono por defecto si no coincide
            
            # Obtener fecha de modificación formateada
            mtime = file_path.stat().st_mtime
            fecha_mod = datetime.fromtimestamp(mtime).strftime("%d %b %Y")
            
            documentos_encontrados.append({
                "icon": icon,
                "titulo": file_path.stem, # Nombre sin extensión
                "ext": ext.replace(".", "").upper(), # ej: 'PDF'
                "fecha": fecha_mod
            })
    
    # Si la carpeta está vacía o no existe, mostrar un fallback amigable
    if not documentos_encontrados:
        st.markdown("<p style='color:#64748b; font-size:13px; font-style: italic;'>No se encontraron documentos en /docs</p>", unsafe_allow_html=True)
    else:
        for doc in documentos_encontrados:
            card_html = f"""
            <div class="doc-card">
                <div class="doc-icon-container">{doc['icon']}</div>
                <div class="doc-details">
                    <div class="doc-title" title="{doc['titulo']}">{doc['titulo']}</div>
                    <div class="doc-meta">
                        <span class="doc-ext">{doc['ext']}</span>
                        <span>{doc['fecha']}</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
    st.markdown("<p style='text-align:center; color:#38bdf8; font-size:13px; cursor:pointer; margin-top:10px;'>📂 Ver todos los documentos  &nbsp; ❯</p>", unsafe_allow_html=True)

# ----------------- COLUMNA CENTRAL: Chat e Interacción (Único Scroll) -----------------
with col_centro:
    if len(st.session_state.messages) == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; margin-bottom: 25px;'>"
            "   <h1 style='font-size:36px; font-weight:800; color:#ffffff; margin-bottom:5px;'>¡Hola, Bienvenido a BimBam Buy!</h1>"
            "   <h3 style='font-size:20px; font-weight:500; color:#38bdf8; margin-bottom:15px;'>Soy tu agente de BimBam Buy 🛡️</h3>"
            "   <p style='color:#94a3b8; font-size:15px; max-width:550px; margin:0 auto; line-height:1.5;'>"
            "       Puedo ayudarte con productos, pedidos, reembolsos, envíos, afiliados y cualquier duda sobre tu experiencia de compra."
            "   </p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        st.markdown("<p style='text-align:center; color:#64748b; font-size:13px; margin-top:40px; margin-bottom:15px;'>Puedes preguntarme sobre:</p>", unsafe_allow_html=True)
        
        sug_col1, sug_col2, sug_col3, sug_col4 = st.columns(4)
        with sug_col1:
            if st.button("💳 Métodos de pago", key="sug1"):
                st.session_state.sugerencia_seleccionada = "Qué métodos de pago aceptan"
        with sug_col2:
            if st.button("🔄 Políticas de reembolso", key="sug2"):
                st.session_state.sugerencia_seleccionada = "Políticas de reembolso"
        with sug_col3:
            if st.button("🕒 Tiempos de entrega", key="sug3"):
                st.session_state.sugerencia_seleccionada = "Tiempos de entrega"
        with sug_col4:
            if st.button("🤝 Cómo ser afiliado", key="sug4"):
                st.session_state.sugerencia_seleccionada = "Cómo ser afiliado"
                
    else:
        for mensaje in st.session_state.messages:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

    if st.session_state.sugerencia_seleccionada:
        pregunta = st.session_state.sugerencia_seleccionada
        st.session_state.sugerencia_seleccionada = None
    else:
        pregunta = st.chat_input("Pregunta lo que quieras...")

    if pregunta:
        st.session_state.messages.append({
            "role": "user",
            "content": pregunta
        })
        st.rerun()

# Procesar la respuesta del asistente
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    pregunta_actual = st.session_state.messages[-1]["content"]
    
    with col_centro:
        with st.chat_message("user"):
            st.markdown(pregunta_actual)
            
        with st.chat_message("assistant"):
            with st.spinner("Consultando..."):
                try:
                    respuesta = procesar_consulta(pregunta_actual)
                except Exception as e:
                    respuesta = f"Error:\n\n{e}"
                
                st.markdown(respuesta)
                
        st.session_state.messages.append({
            "role": "assistant",
            "content": respuesta
        })
        st.rerun()

# ----------------- COLUMNA DERECHA: BimBam Buy Info -----------------
with col_der:
    st.markdown("""
    <div class="info-box">
        <h3 style="color:#38bdf8; font-size:20px; margin-top:0; font-weight:700;">BimBam Buy</h3>
        <p style="color:#94a3b8; font-size:13px; line-height:1.6; text-align:justify;">
            E-commerce multiplataforma enfocado en la experiencia de compra digital ágil y segura.
        </p>
        <p style="color:#94a3b8; font-size:13px; line-height:1.6; text-align:justify;">
            Se destaca por un modelo de negocio orientado al cliente, con políticas robustas de reembolso, un programa de afiliados dinámico y una infraestructura logística optimizada para garantizar entregas rápidas y soporte constante al usuario final.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists(carrito_path):
        st.image(carrito_path, width="stretch")

# Pie de página
st.markdown(
    "<br><hr style='border:0; height:1px; background:rgba(30,58,96,0.3);'>"
    "<p style='text-align:center; color:#475569; font-size:12px;'>🔒 Seguridad • Confianza • Experiencia</p>", 
    unsafe_allow_html=True
)