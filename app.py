import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# --------------------------------------------------
# CARPETAS
# --------------------------------------------------

Path("uploads").mkdir(exist_ok=True)

# --------------------------------------------------
# TEMA KINGKONG
# --------------------------------------------------

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

st.markdown("""
<style>

/* Fondo principal */
.stApp{
    background-color:#0d1117;
    color:#f5f5f5;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#111111;
}

/* Títulos */
h1,h2,h3{
    color:#39ff14;
}

/* Inputs */
.stChatInput input{
    background-color:#1b1b1b !important;
    color:white !important;
}

/* Botones */
.stButton button{
    background-color:#39ff14;
    color:black;
    border:none;
    font-weight:bold;
}

/* File uploader */
[data-testid="stFileUploader"]{
    background-color:#1b1b1b;
    border-radius:12px;
    padding:10px;
}

/* Mensajes */
[data-testid="stChatMessage"]{
    background-color:#161b22;
    border-radius:12px;
    padding:10px;
    margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# ESTADO CHAT
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        "## 🦍 KINGKONG CHAT"
    )

    st.markdown("---")

    section = st.radio(
        "",
        [
            "📁 Archivos",
            "🤖 IA",
            "⚙️ Sistema"
        ]
    )

    st.markdown("---")

    st.success("🟢 Gemini Online")

# --------------------------------------------------
# ARCHIVOS
# --------------------------------------------------

if section == "📁 Archivos":

    st.title("📁 Archivos")

    uploaded_file = st.file_uploader(
        "Subir archivo"
    )

    if uploaded_file:

        save_path = (
            Path("uploads")
            / uploaded_file.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(
            f"Archivo guardado: {uploaded_file.name}"
        )

    st.subheader("Archivos disponibles")

    files = list(Path("uploads").glob("*"))

    if not files:
        st.info("No hay archivos")

    for file in files:
        st.write(f"📄 {file.name}")

# --------------------------------------------------
# IA
# --------------------------------------------------

elif section == "🤖 IA":

    st.title("🤖 KINGKONG CHAT")

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        "Pregunta a Gemini..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

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

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

# --------------------------------------------------
# SISTEMA
# --------------------------------------------------

else:

    st.title("⚙️ Sistema")

    st.info(
        "Preparado para futuras configuraciones."
    )

    st.write(
        "• Cambiar IA\n"
        "• Conectar Qwen\n"
        "• Exportar historial\n"
        "• Importar backup\n"
        "• Configuración usuario"
    )
