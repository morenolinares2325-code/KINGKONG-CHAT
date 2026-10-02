import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import base64

# ======================
# FUNCIONES
# ======================

def image_to_base64(path):

    with open(path, "rb") as f:

        return base64.b64encode(
            f.read()
        ).decode()


# ======================
# CONFIG
# ======================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

connected = False

try:

    genai.configure(
        api_key=API_KEY
    )

    model = genai.GenerativeModel(
        "gemini-1.5-flash"
    )

    connected = True

except:

    connected = False

# ======================
# ESTADOS
# ======================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme_color" not in st.session_state:
    st.session_state.theme_color = "#39FF14"

if "secondary_color" not in st.session_state:
    st.session_state.secondary_color = "#00C853"

if "text_color" not in st.session_state:
    st.session_state.text_color = "#FFFFFF"

if "input_color" not in st.session_state:
    st.session_state.input_color = "#FFFFFF"

if "sidebar_color" not in st.session_state:
    st.session_state.sidebar_color = "#061208"

if "font_size" not in st.session_state:
    st.session_state.font_size = 16

if "chat_width" not in st.session_state:
    st.session_state.chat_width = 1400

if "radius" not in st.session_state:
    st.session_state.radius = 20

Path("uploads").mkdir(exist_ok=True)

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

bg_image = image_to_base64(
    "assets/jungle.jpg"
)
# ======================
# CSS
# ======================

st.markdown(
f"""
<style>

.stApp {{

background-image:

linear-gradient(
rgba(0,0,0,.72),
rgba(0,0,0,.82)
),

url("data:image/jpeg;base64,{bg_image}");

background-size:cover;

background-position:center;

background-attachment:fixed;
}}

section[data-testid="stSidebar"] {{

background:
linear-gradient(
180deg,
rgba(5,15,8,.95),
rgba(8,25,10,.95),
rgba(5,15,8,.95)
);

border-right:
2px solid {st.session_state.theme_color};

backdrop-filter:
blur(12px);
}}

[data-testid="stChatMessage"] {{

background:
rgba(15,15,15,.55);

backdrop-filter:
blur(10px);

border:
1px solid rgba(255,255,255,.15);

border-radius:
{st.session_state.radius}px;
}}

h1,h2,h3 {{

color:{st.session_state.theme_color};

text-shadow:

0 0 15px {st.session_state.theme_color},

0 0 35px {st.session_state.theme_color};

}}

.stChatInput input {{

background:
{st.session_state.input_color}
!important;

color:
black
!important;

border:
3px solid
{st.session_state.theme_color}
!important;

border-radius:
25px !important;

font-size:
{st.session_state.font_size}px
!important;
}}

.stButton button {{

background:
linear-gradient(
135deg,
{st.session_state.theme_color},
{st.session_state.secondary_color}
);

color:black;

font-weight:bold;

border:none;
}}

footer {{
visibility:hidden;
}}

</style>
""",
unsafe_allow_html=True
)

# ======================
# SIDEBAR
# ======================

with st.sidebar:

    st.markdown(
    f"""
    <h1 style='
    text-align:center;
    font-size:70px;
    color:{st.session_state.theme_color};
    '>
    🦍
    </h1>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
    f"""
    <h2 style='
    text-align:center;
    color:{st.session_state.theme_color};
    '>
    KINGKONG CHAT
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.markdown("---")

    menu = st.radio(
        "",
        [
            "💬 Chat",
            "📁 Archivos",
            "⚙️ Ajustes"
        ]
    )

    st.markdown("---")

    if connected:

        st.success(
            "🟢 IA CONECTADA"
        )

    else:

        st.error(
            "🔴 IA DESCONECTADA"
        )

    reloj = datetime.now().strftime(
        "%H:%M:%S"
    )

    st.markdown(
        f"""
        <h2 style="
        text-align:center;
        color:
        {st.session_state.theme_color};
        ">
        {reloj}
        </h2>
        """,
        unsafe_allow_html=True
    )
    if menu == "💬 Chat":

    st.markdown(
        f"""
        <h1 style="
        text-align:center;
        font-size:70px;
        color:
        {st.session_state.theme_color};
        ">
        🦍 KINGKONG CHAT
        </h1>
        """,
        unsafe_allow_html=True
    )

    for msg in st.session_state.messages:

        with st.chat_message(
            msg["role"]
        ):

            st.markdown(
                msg["content"]
            )

    prompt = st.chat_input(
        "Pregunta lo que quieras..."
    )

    if prompt:

        st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        })

        try:

            response = model.generate_content(
                prompt
            )

            answer = response.text

        except Exception as e:

            answer = str(e)

        st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        })

        st.rerun()


elif menu == "📁 Archivos":

    st.title("📁 Archivos")

    uploaded = st.file_uploader(
        "Subir archivo"
    )

    if uploaded:

        with open(
            Path("uploads")
            / uploaded.name,
            "wb"
        ) as f:

            f.write(
                uploaded.getbuffer()
            )

        st.success(
            uploaded.name
        )

else:

    st.title("⚙️ Ajustes")

    st.subheader("🎨 Colores")

    st.session_state.theme_color = st.color_picker(
        "Color Principal",
        st.session_state.theme_color
    )

    st.session_state.secondary_color = st.color_picker(
        "Color Secundario",
        st.session_state.secondary_color
    )

    st.session_state.text_color = st.color_picker(
        "Color Texto",
        st.session_state.text_color
    )

    st.session_state.input_color = st.color_picker(
        "Color Input",
        st.session_state.input_color
    )

    st.markdown("---")

    st.subheader("📏 Diseño")

    st.session_state.chat_width = st.slider(
        "Ancho Chat",
        800,
        1900,
        st.session_state.chat_width
    )

    st.session_state.font_size = st.slider(
        "Texto",
        12,
        28,
        st.session_state.font_size
    )

    st.session_state.radius = st.slider(
        "Radio Bordes",
        0,
        40,
        st.session_state.radius
    )

    st.markdown("---")

    if st.button(
        "🗑️ Borrar historial"
    ):

        st.session_state.messages = []

        st.rerun()
        
