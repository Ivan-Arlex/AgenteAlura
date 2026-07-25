import os
import base64
from pathlib import Path
import streamlit as st
from graph import procesar_consulta

import time

inicio = time.time()

st.set_page_config(
    page_title="BimBam Buy - ZULAI, Agente de Compra Inteligente",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def get_image_base64(path: str) -> str:
    """Convierte una imagen local a base64 para incrustarla en HTML/CSS."""
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            ext = Path(path).suffix.replace(".", "")
            return f"data:image/{ext};base64,{encoded}"
    return ""

def format_file_size(bytes_size: int) -> str:
    """Formatea el tamaño de archivo a KB o MB."""
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size / (1024 * 1024):.1f} MB"

@st.cache_data(ttl=300)
def get_docs_list():
    """Lee dinámicamente la carpeta de documentos (src/docs o docs)."""
    possible_paths = [
        Path("src/docs"),
        Path("docs"),
        Path("../src/docs")
    ]
    docs_dir = None
    for p in possible_paths:
        if p.exists() and p.is_dir():
            docs_dir = p
            break

    files_list = []
    if docs_dir:
        for file in docs_dir.iterdir():
            if file.is_file() and not file.name.startswith("."):
                size = format_file_size(file.stat().st_size)
                ext = file.suffix.lower().replace(".", "")
                files_list.append({
                    "name": file.name,
                    "size": size,
                    "ext": ext,
                    "path": str(file)
                })
    return files_list

ASSETS_DIR = Path("assets")
LOGO_PATH = ASSETS_DIR / "logo.png"
CARRITO_PATH = ASSETS_DIR / "carrito.png"

logo_b64 = get_image_base64(str(LOGO_PATH))
carrito_b64 = get_image_base64(str(CARRITO_PATH))

st.markdown("""
<style>
    /* Ocultar elementos nativos preservando el botón para reabrir la barra lateral */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Botón flotante siempre visible para reabrir la barra lateral cuando está colapsada */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        color: #F8FAFC !important;
        background-color: #0c1028 !important;
        border: 1px solid rgba(168, 85, 247, 0.6) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        margin-top: 8px !important;
        margin-left: 8px !important;
        z-index: 999999 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="collapsedControl"]:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.5) !important;
        transform: scale(1.05);
    }
    [data-testid="collapsedControl"] svg {
        fill: #F8FAFC !important;
        color: #F8FAFC !important;
    }

    /* Estilo Global Oscuro Futurista */
    [data-testid="stAppViewContainer"] {
        background-color: #050714 !important;
        background-image: radial-gradient(circle at 50% 0%, #151038 0%, #050714 75%) !important;
        color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    body, p, div, span, label, h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Sidebar Estilizado */
    [data-testid="stSidebar"] {
        background-color: #090c21 !important;
        border-right: 1px solid rgba(139, 92, 246, 0.3) !important;
    }

    /* Botones Globales con estilo futurista */
    .stButton > button {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(168, 85, 247, 0.5) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        padding: 4px 12px !important;
        font-size: 13px !important;
    }
    .stButton > button:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;
        color: #00f2fe !important;
        transform: translateY(-1px);
    }
    .stButton > button p, .stButton > button div, .stButton > button span {
        color: #FFFFFF !important;
    }

    /* Tarjetas y Paneles Glassmorphism */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }

    .banner-card {
        background: linear-gradient(135deg, rgba(30, 18, 75, 0.95) 0%, rgba(12, 16, 42, 0.95) 100%);
        border: 1px solid rgba(168, 85, 247, 0.5);
        border-radius: 18px;
        padding: 18px 22px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.25);
        margin-bottom: 15px;
    }

    /* Lista de Documentos con Iconografía Tecnológica */
    .doc-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(22, 30, 60, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .doc-item:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }

    /* Footer Fijo */
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #040610;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 8px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #CBD5E1;
        z-index: 999;
    }

    .status-online {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dot-green {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
    }

    /* Cuadro de Chat Futurista */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        padding-top: 10px !important;
        padding-bottom: 25px !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: #0c1028 !important;
        border: 1px solid rgba(168, 85, 247, 0.6) !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.7), 0 0 15px rgba(139, 92, 246, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #00f2fe !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #FFFFFF !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }

    /* Estilo de Mensajes de Chat */
    [data-testid="stChatMessage"] {
        background-color: rgba(20, 27, 52, 0.85) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 14px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stChatMessage"] * {
        color: #F8FAFC !important;
    }

    /* Estilo personalizado legible para Toasts (st.toast) */
    [data-testid="stToast"] {
        background-color: #0c1028 !important;
        border: 1px solid rgba(168, 85, 247, 0.6) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.7), 0 0 15px rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
    }
    [data-testid="stToast"] * {
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "historial" not in st.session_state:
    st.session_state.historial = []

def clear_chat_callback():
    st.session_state.messages = []

def set_faq_callback(query_text):
    st.session_state.pending_faq = query_text

with st.sidebar:
    # Botones superiores en la barra lateral
    col_sb_act1, col_sb_act2 = st.columns(2)
    with col_sb_act1:
        st.button("🗑️ Limpiar", use_container_width=True, key="btn_clean_sidebar", on_click=clear_chat_callback)
    with col_sb_act2:
        if st.button("⚙️ Ajustes", use_container_width=True, key="btn_settings_sidebar"):
            st.toast("Panel de ajustes", icon="⚙️")

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if logo_b64:
        st.markdown(f'''
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <img src="{logo_b64}" style="width: 40px; height: 40px; object-fit: contain; filter: drop-shadow(0 0 8px rgba(0,242,254,0.6));">
                <div>
                    <h2 style="margin:0; font-size: 20px; font-weight: 800; background: linear-gradient(90deg, #FFFFFF, #C084FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">BimBam Buy</h2>
                    <p style="margin:0; font-size: 11px; color: #a78bfa; font-weight: 500;">ZULAI, Agente de Compra Inteligente</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <div style="font-size: 28px;">🛒</div>
                <div>
                    <h2 style="margin:0; font-size: 20px; font-weight: 800; background: linear-gradient(90deg, #FFFFFF, #C084FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">BimBam Buy</h2>
                    <p style="margin:0; font-size: 11px; color: #a78bfa; font-weight: 500;">Agente de Compra Inteligente</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<p style='font-size: 12px; font-weight: 700; color: #CBD5E1; margin-top: 6px; letter-spacing: 0.5px;'>DOCUMENTOS (RAG)</p>", unsafe_allow_html=True)

    docs = get_docs_list()
    if docs:
        for doc in docs:
            if doc['ext'] == "pdf":
                icon_symbol, icon_color = "⚛️", "#FF4B4B"
            elif doc['ext'] in ["xlsx", "xls", "csv"]:
                icon_symbol, icon_color = "💎", "#10B981"
            else:
                icon_symbol, icon_color = "⚡", "#3B82F6"
            
            st.markdown(f'''
                <div class="doc-item">
                    <div style="display: flex; align-items: center; gap: 10px; overflow: hidden;">
                        <span style="font-size: 16px; filter: drop-shadow(0 0 6px {icon_color});">{icon_symbol}</span>
                        <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            <div style="font-size: 12px; font-weight: 600; color: #F1F5F9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{doc['name']}</div>
                            <div style="font-size: 10px; color: #94A3B8;">{doc['ext'].upper()} • {doc['size']}</div>
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 12px; color: #94A3B8; font-style: italic;'>No se encontraron documentos en la carpeta docs.</p>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(139, 92, 246, 0.2); margin: 15px 0;'>", unsafe_allow_html=True)

    st.markdown('''
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 14px;">🛡️</span>
                <strong style="color: #00f2fe; font-size: 13px;">SOBRE BIMBAM BUY</strong>
            </div>
            <p style="font-size: 11px; color: #CBD5E1; line-height: 1.4; margin-bottom: 6px;">
                E-commerce multiplataforma enfocado en la experiencia de compra digital ágil y segura con inteligencia artificial.
            </p>
            <p style="font-size: 11px; color: #CBD5E1; line-height: 1.4; margin: 0;">
                Logística optimizada, reembolsos y programa de afiliados orientados al cliente.
            </p>
        </div>
    ''', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    carrito_html = f'<img src="{carrito_b64}" style="width: 70px; filter: drop-shadow(0 0 12px rgba(168,85,247,0.5));">' if carrito_b64 else '<div style="font-size: 36px;">🛒</div>'

    st.markdown(f'''
        <div class="banner-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: nowrap; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 14px; max-width: 85%;">
                    <div style="font-size: 28px; background: rgba(124, 58, 237, 0.25); padding: 8px; border-radius: 12px; border: 1px solid rgba(168, 85, 247, 0.5);">
                        🛡️
                    </div>
                    <div>
                        <h3 style="margin: 0 0 4px 0; font-size: 18px; font-weight: 800; color: #FFFFFF;">
                            ¡Hola! Soy ZULAI, tu Agente de Compra Inteligente
                        </h3>
                        <p style="margin: 0; font-size: 12px; color: #CBD5E1; line-height: 1.3;">
                            Estoy aquí para ayudarte a encontrar información precisa y confiable sobre BimBam Buy. Pregúntame lo que necesites.
                        </p>
                    </div>
                </div>
                <div>
                    {carrito_html}
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # Preguntas Frecuentes HORIZONTALES (solo se muestran al inicio)
    st.markdown("<p style='font-weight: 700; color: #E2E8F0; font-size: 12px; letter-spacing: 0.5px; margin: 8px 0 6px 0;'>🔍¿PREGUNTAS FRECUENTES?🔎</p>", unsafe_allow_html=True)
    
    faq_col1, faq_col2, faq_col3, faq_col4 = st.columns(4)
    with faq_col1:
        st.button("💳 Métodos de pago", use_container_width=True, key="faq1", on_click=set_faq_callback, args=("¿Cuáles son los métodos de pago disponibles?",))
    with faq_col2:
        st.button("🔄 Reembolsos", use_container_width=True, key="faq2", on_click=set_faq_callback, args=("¿Cómo funciona la política de reembolsos?",))
    with faq_col3:
        st.button("🕒 Tiempos de entrega", use_container_width=True, key="faq3", on_click=set_faq_callback, args=("¿Cuáles son los tiempos de entrega estimados?",))
    with faq_col4:
        st.button("🤝 Ser afiliado", use_container_width=True, key="faq4", on_click=set_faq_callback, args=("¿Qué necesito para unirme al programa de afiliados?",))

if len(st.session_state.messages) == 0:
    st.markdown("<p style='text-align: center; color: #C084FC; font-size: 13px; font-weight: 700; margin: 15px 0 10px 0;'>✨ ¿Con qué puedo ayudarte hoy?</p>", unsafe_allow_html=True)

chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_input = st.chat_input("Escribe tu pregunta aquí...")

faq_query = st.session_state.pop("pending_faq", None)
prompt_to_process = user_input or faq_query

if prompt_to_process:
    # Registrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    
    # Procesar la respuesta del agente
    with st.spinner("⚡Generando respuesta..."):
        try:
            respuesta = procesar_consulta(
                pregunta=prompt_to_process,
                historial=st.session_state.historial
                )
        except Exception as e:
            respuesta = f"Ocurrió un error al procesar la consulta: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta})

        st.session_state.historial.append(
            f"Usuario: {prompt_to_process}"
        )
        st.session_state.historial.append(
            f"ZULAI: {respuesta}"
        )

st.markdown('''
    <div class="custom-footer">
        <div class="status-online">
            <div class="dot-green"></div>
            <span style="color: #E2E8F0; font-weight: 500;">Agente en línea</span>
        </div>
        <div style="color: #CBD5E1;">
            <strong style="color: #FFFFFF;">BimBam Buy</strong> ©
        </div>
        <div style="color: #34D399; font-weight: 600;">
            🔒 Información segura
        </div>
    </div>
''', unsafe_allow_html=True)
print(f"Render completo: {time.time()-inicio:.2f} s")