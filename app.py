import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import os

# ====================================================
# TEMAS
# ====================================================

def get_theme(theme_name):

    themes = {

        "🦍 Jungle Neon": {
            "primary": "#39FF14",
            "secondary": "#00C853",
            "background": "#050505",
            "sidebar": "#111111",
            "card": "#181818",
            "text": "#FFFFFF"
        },

        "💚 Matrix": {
            "primary": "#00FF00",
            "secondary": "#00CC00",
            "background": "#000000",
            "sidebar": "#050505",
            "card": "#101010",
            "text": "#E5FFE5"
        },

        "💙 Ocean Cyber": {
            "primary": "#00E5FF",
            "secondary": "#0099FF",
            "background": "#06131B",
            "sidebar": "#0D1F2D",
            "card": "#11293B",
            "text": "#FFFFFF"
        },

        "🟣 Ultra Violet": {
            "primary": "#C77DFF",
            "secondary": "#9D4EDD",
            "background": "#10002B",
            "sidebar": "#240046",
            "card": "#3C096C",
            "text": "#FFFFFF"
        },

        "❤️ Lava Red": {
            "primary": "#FF3D3D",
            "secondary": "#FF6B6B",
            "background": "#120000",
            "sidebar": "#1E0000",
            "card": "#2D0B0B",
            "text": "#FFFFFF"
        }
    }

    return themes[theme_name]


# ====================================================
# CONFIG
# ====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

Path("uploads").mkdir(exist_ok=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "🦍 Jungle Neon"

if "chat_width" not in st.session_state:
    st.session_state.chat_width = "1200px"

theme = get_theme(
    st.session_state.theme
)

PRIMARY = theme["primary"]
SECONDARY = theme["secondary"]
BACKGROUND = theme["background"]
SIDEBAR = theme["sidebar"]
CARD = theme["card"]
TEXT = theme["text"]

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

# ====================================================
# CSS GLOBAL
# ====================================================

st.markdown(f"""
<style>

.stApp {{
    background-color:{BACKGROUND};
    color:{TEXT};
}}

section[data-testid="stSidebar"] {{
    background-color:{SIDEBAR};
    border-right:2px solid {PRIMARY};
}}

h1,h2,h3 {{
    color:{PRIMARY};
    text-shadow:
        0 0 5px {PRIMARY},
        0 0 15px {PRIMARY};
}}

.block-container {{
    max-width:{st.session_state.chat_width};
}}

[data-testid="stChatMessage"] {{
    background-color:{CARD};
    border:1px solid {SECONDARY};
    border-radius:15px;
}}

.stChatInput input {{
    background:{CARD} !important;
    color:{TEXT} !important;
    border:1px solid {PRIMARY} !important;
}}

.stButton button {{
    background:{PRIMARY};
    color:black;
    font-weight:bold;
    border-radius:12px;
}}

.neon {{
    color:{PRIMARY};
    text-shadow:
        0px 0px 10px {PRIMARY},
        0px 0px 20px {PRIMARY};
}}

</style>
""", unsafe_allow_html=True)


# ====================================================
# SIDEBAR
# ====================================================

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
    # ====================================================
# CHAT
# ====================================================

if menu == "💬 Chat":

    st.title("🦍 KINGKONG CHAT")

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        "Pregunta lo que quieras..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        try:

            response = model.generate_content(
                prompt
            )

            answer = response.text

        except Exception as e:

            answer = f"Error: {e}"

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })


# ====================================================
# ARCHIVOS
# ====================================================

elif menu == "📁 Archivos":

    st.title("📁 Archivos")

    uploaded = st.file_uploader(
        "Subir archivo"
    )

    if uploaded:

        path = (
            Path("uploads")
            / uploaded.name
        )

        with open(path, "wb") as f:
            f.write(uploaded.read())

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
            f"📄 {file.name} ({size_mb:.2f} MB)"
        )

# ====================================================
# AJUSTES
# ====================================================

else:

    st.title("⚙️ Ajustes")

    selected_theme = st.selectbox(
        "Tema visual",
        [
            "🦍 Jungle Neon",
            "💚 Matrix",
            "💙 Ocean Cyber",
            "🟣 Ultra Violet",
            "❤️ Lava Red"
        ]
    )

    st.session_state.theme = selected_theme

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

    st.subheader("🎭 Diseño")

    layout = st.selectbox(
        "Estilo",
        [
            "Telegram",
            "Discord",
            "ChatGPT",
            "Compacto",
            "Expandido"
        ]
    )

    st.info(
        f"Diseño seleccionado: {layout}"
    )

    st.markdown("---")

    st.subheader("💾 Sistema")

    if st.button(
        "🗑️ Borrar historial"
    ):

        st.session_state.messages = []

        st.success(
            "Historial eliminado"
        )

    st.markdown("---")

    st.info("""
🦍 KINGKONG CHAT V1

✅ Gemini integrado

✅ Estilo Neon

✅ Modo Telegram

✅ Gestión de archivos

✅ Preparado para KINGKONG AI

✅ Preparado para Qwen/Ollama
""")
