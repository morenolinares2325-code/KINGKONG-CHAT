import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path

# =====================================================
# CONFIGURACION
# =====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

Path("uploads").mkdir(exist_ok=True)

# =====================================================
# CONFIG INICIAL
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "main_color" not in st.session_state:
    st.session_state.main_color = "#39FF14"

if "chat_width" not in st.session_state:
    st.session_state.chat_width = "1200px"

# =====================================================
# PAGINA
# =====================================================

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

MAIN_COLOR = st.session_state.main_color

# =====================================================
# CSS KINGKONG
# =====================================================

st.markdown(f"""
<style>

.stApp {{
    background-color:#050505;
    color:white;
}}

section[data-testid="stSidebar"] {{
    background-color:#101010;
    border-right:2px solid {MAIN_COLOR};
}}

h1,h2,h3 {{
    color:{MAIN_COLOR};
    text-shadow:0 0 10px {MAIN_COLOR};
}}

.block-container {{
    max-width:{st.session_state.chat_width};
}}

[data-testid="stChatMessage"] {{
    background-color:#181818;
    border:1px solid #2a2a2a;
    border-radius:15px;
    padding:14px;
}}

.stChatInput input {{
    background:#151515 !important;
    color:white !important;
    border:1px solid {MAIN_COLOR} !important;
}}

.stButton button {{
    background:{MAIN_COLOR};
    color:black;
    border:none;
    border-radius:10px;
    font-weight:bold;
}}

div[data-testid="stFileUploader"] {{
    background:#181818;
    border-radius:12px;
    padding:10px;
}}

.neon {{
    color:{MAIN_COLOR};
    font-weight:bold;
    text-shadow:0px 0px 10px {MAIN_COLOR};
}}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        "<h2 class='neon'>🦍 KINGKONG CHAT</h2>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    menu = st.radio(
        "",
        [
            "💬 Chat",
            "📁 Archivos",
            "⚙️ Ajustes"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.success("🟢 Gemini Online")

# =====================================================
# CHAT PRINCIPAL
# =====================================================

if menu == "💬 Chat":

    st.title("🦍 KINGKONG CHAT")

    st.caption(
        "Tu centro de comunicación e IA."
    )

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        "Escribe un mensaje..."
    )

    if prompt:

        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            try:

                response = model.generate_content(
                    prompt
                )

                reply = response.text

            except Exception as e:

                reply = f"Error: {e}"

            st.markdown(reply)

        st.session_state.messages.append({
            "role":"assistant",
            "content":reply
        })

# =====================================================
# ARCHIVOS
# =====================================================

elif menu == "📁 Archivos":

    st.title("📁 Archivos")

    uploaded = st.file_uploader(
        "Subir archivo"
    )

    if uploaded:

        destination = (
            Path("uploads")
            / uploaded.name
        )

        with open(destination, "wb") as f:
            f.write(
                uploaded.getbuffer()
            )

        st.success(
            f"Archivo guardado: {uploaded.name}"
        )

    st.markdown("### Archivos disponibles")

    files = list(
        Path("uploads").glob("*")
    )

    if not files:

        st.info(
            "No hay archivos cargados."
        )

    for file in files:

        size_mb = (
            file.stat().st_size
            / 1024
            / 1024
        )

        st.markdown(
            f"📄 **{file.name}** ({size_mb:.2f} MB)"
        )

# =====================================================
# AJUSTES
# =====================================================

elif menu == "⚙️ Ajustes":

    st.title("⚙️ Ajustes")

    st.subheader("🎨 Color Principal")

    color = st.color_picker(
        "Selecciona color",
        MAIN_COLOR
    )

    if color != MAIN_COLOR:

        st.session_state.main_color = color

    st.markdown("---")

    st.subheader("📏 Tamaño del Chat")

    width = st.selectbox(
        "",
        [
            "900px",
            "1200px",
            "1500px",
            "100%"
        ],
        index=1
    )

    st.session_state.chat_width = width

    st.markdown("---")

    st.subheader("ℹ️ Información")

    st.write("""
    KINGKONG CHAT V1

    - Chat Gemini
    - Gestión de archivos
    - Preparado para Qwen
    - Preparado para KINGKONG AI
    - Preparado para VPS
    """)

    st.success(
        "Los cambios visuales se aplicarán al recargar."
    )
