import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os

# ===================================
# TEMAS
# ===================================

THEMES = {

    "🦍 Jungle Neon": {
        "primary":"#39FF14",
        "secondary":"#00C853",
        "background":"#050505",
        "sidebar":"#111111",
        "card":"#161616",
        "text":"#FFFFFF"
    },

    "💚 Matrix": {
        "primary":"#00FF00",
        "secondary":"#00CC00",
        "background":"#000000",
        "sidebar":"#050505",
        "card":"#111111",
        "text":"#FFFFFF"
    },

    "💙 Cyber Ocean": {
        "primary":"#00E5FF",
        "secondary":"#0099FF",
        "background":"#06131B",
        "sidebar":"#0D1F2D",
        "card":"#11293B",
        "text":"#FFFFFF"
    },

    "🟣 Ultra Violet": {
        "primary":"#C77DFF",
        "secondary":"#9D4EDD",
        "background":"#10002B",
        "sidebar":"#240046",
        "card":"#3C096C",
        "text":"#FFFFFF"
    },

    "❤️ Lava Red": {
        "primary":"#FF3D3D",
        "secondary":"#FF6B6B",
        "background":"#120000",
        "sidebar":"#1E0000",
        "card":"#2D0B0B",
        "text":"#FFFFFF"
    },

    "🟡 Gold Monkey": {
        "primary":"#FFD700",
        "secondary":"#FFB300",
        "background":"#050505",
        "sidebar":"#111111",
        "card":"#161616",
        "text":"#FFFFFF"
    }
}

# ===================================
# ESTADOS
# ===================================

if "theme" not in st.session_state:
    st.session_state.theme="🦍 Jungle Neon"

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "chat_width" not in st.session_state:
    st.session_state.chat_width=1400

if "font_size" not in st.session_state:
    st.session_state.font_size=16

if "radius" not in st.session_state:
    st.session_state.radius=15

if "sidebar_width" not in st.session_state:
    st.session_state.sidebar_width=300

theme = THEMES[st.session_state.theme]

PRIMARY=theme["primary"]
SECONDARY=theme["secondary"]
BACKGROUND=theme["background"]
SIDEBAR=theme["sidebar"]
CARD=theme["card"]
TEXT=theme["text"]

# ===================================
# GEMINI
# ===================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

connected=False

try:

    genai.configure(api_key=API_KEY)

    model = genai.GenerativeModel(
        "gemini-1.5-flash"
    )

    connected=True

except:
    connected=False

# ===================================
# STREAMLIT
# ===================================

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

Path("uploads").mkdir(exist_ok=True)
# ===================================
# CSS
# ===================================

st.markdown(f"""
<style>

.stApp{{
background:{BACKGROUND};
color:{TEXT};
}}

section[data-testid="stSidebar"]{{
background:{SIDEBAR};
border-right:2px solid {PRIMARY};
}}

.block-container{{
max-width:{st.session_state.chat_width}px;
}}

h1,h2,h3{{
color:{PRIMARY};
text-shadow:
0 0 10px {PRIMARY},
0 0 25px {PRIMARY};
}}

[data-testid="stChatMessage"]{{
background:{CARD};
border:1px solid {SECONDARY};
border-radius:{st.session_state.radius}px;
}}

.stChatInput input{{
background:#101010 !important;
color:white !important;
border:2px solid {PRIMARY} !important;
border-radius:{st.session_state.radius}px !important;
}}

</style>
""", unsafe_allow_html=True)

# ===================================
# SIDEBAR
# ===================================

with st.sidebar:

    st.markdown(f"""
    <h1 style="
    text-align:center;
    color:{PRIMARY};
    text-shadow:
    0 0 15px {PRIMARY},
    0 0 30px {PRIMARY};
    ">
    🦍
    </h1>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <h2 style="
    text-align:center;
    color:{PRIMARY};
    ">
    KINGKONG CHAT
    </h2>
    """, unsafe_allow_html=True)

    st.markdown("---")

    menu=st.radio(
        "",
        [
            "💬 Chat",
            "📁 Archivos",
            "⚙️ Ajustes"
        ]
    )

    st.markdown("---")

    if connected:
        st.success("🟢 IA CONECTADA")
    else:
        st.error("🔴 IA DESCONECTADA")

    reloj=datetime.now().strftime("%H:%M:%S")

    st.markdown(
        f"""
        <h2 style="
        text-align:center;
        color:{PRIMARY};
        ">
        {reloj}
        </h2>
        """,
        unsafe_allow_html=True
    )
    # ===================================
# CHAT
# ===================================

if menu=="💬 Chat":

    st.markdown(f"""
    <h1 style="
    text-align:center;
    font-size:60px;
    color:{PRIMARY};
    ">
    🦍 KINGKONG CHAT
    </h1>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:

        with st.chat_message(
            msg["role"]
        ):
            st.markdown(
                msg["content"]
            )

    prompt=st.chat_input(
        "Pregunta lo que quieras..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role":"user",
                "content":prompt
            }
        )

        try:

            response=model.generate_content(
                prompt
            )

            answer=response.text

        except Exception as e:

            answer=f"Error: {e}"

        st.session_state.messages.append(
            {
                "role":"assistant",
                "content":answer
            }
        )

        st.rerun()

# ===================================
# ARCHIVOS
# ===================================

elif menu=="📁 Archivos":

    st.title("📁 Archivos")

    file=st.file_uploader(
        "Subir archivo"
    )

    if file:

        with open(
            Path("uploads")
            / file.name,
            "wb"
        ) as f:

            f.write(
                file.getbuffer()
            )

    for archivo in Path(
        "uploads"
    ).glob("*"):

        st.write(
            f"📄 {archivo.name}"
        )

# ===================================
# AJUSTES
# ===================================

else:

    st.title("⚙️ Ajustes")

    st.subheader("🎨 Temas")

    st.session_state.theme = st.selectbox(
        "Tema",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(
            st.session_state.theme
        )
    )

    st.subheader("📏 Tamaño Chat")

    st.session_state.chat_width = st.slider(
        "Ancho",
        800,
        1900,
        st.session_state.chat_width
    )

    st.subheader("🔤 Texto")

    st.session_state.font_size = st.slider(
        "Tamaño",
        12,
        26,
        st.session_state.font_size
    )

    st.subheader("🔲 Bordes")

    st.session_state.radius = st.slider(
        "Radio",
        0,
        40,
        st.session_state.radius
    )

    st.subheader("🎭 Diseño")

    st.selectbox(
        "Modo",
        [
            "Telegram",
            "Discord",
            "ChatGPT",
            "KINGKONG"
        ]
    )

    st.success(
        "Los cambios se aplican al cambiar de página o recargar."
    )

    if st.button("🗑️ Borrar historial"):
        st.session_state.messages=[]
        st.rerun()
        
