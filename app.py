import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import os
import base64
from groq import Groq

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

def image_to_base64(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def get_background_css() -> str:
    for ext in [".jpg", ".png", ".jpeg"]:
        fondo = ASSETS_DIR / f"jungle{ext}"
        if fondo.exists():
            b64 = image_to_base64(fondo)
            mime = "png" if ext == ".png" else "jpeg"
            return f'url("data:image/{mime};base64,{b64}")'
    return ""

GROQ_KEY = (
    os.getenv("GROQ_API_KEY")
    or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
    or "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"
)
client = Groq(api_key=GROQ_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
        background-image: linear-gradient(rgba(0,0,0,0.78), rgba(4,12,6,0.88)), {bg_css if bg_css else "none"} !important;
        background-color: #0b110e !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"], [data-testid="stBottom"], footer, [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    .stChatInput textarea, .stChatInput input {{
        background-color: #FFFFFF !important;
        color: #111111 !important;
        font-size: 16px !important;
        border: 2px solid #39FF14 !important;
        border-radius: 25px !important;
    }}
    [data-testid="stChatMessage"] {{
        background: rgba(16, 26, 18, 0.82) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 18px !important;
        margin-bottom: 12px;
    }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div {{
        color: #FFFFFF !important;
        font-size: 16px !important;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(3,15,6,0.95), rgba(7,24,12,0.95)) !important;
        border-right: 2px solid #39FF1455;
    }}
    h1, h2, h3 {{
        color: #39FF14 !important;
    }}
    footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-top: -15px;">
            <span style="font-size: 64px;">🦍</span>
            <h2 style="margin: 0; font-size: 24px;">KINGKONG CHAT</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.success("🟢 SISTEMA CONECTADO", icon="⚡")
    if st.button("🗑️ Borrar Historial", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    components.html(
        """
        <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 10px; font-family: sans-serif; margin-top: 15px;">
            <div style="color: #aaa; font-size: 10px;">TIEMPO EN VIVO</div>
            <div id="live_clock" style="font-size: 22px; font-weight: bold; color: #39FF14;">00:00:00</div>
        </div>
        <script>
            function updateClock() {
                const now = new Date();
                const h = String(now.getHours()).padStart(2, '0');
                const m = String(now.getMinutes()).padStart(2, '0');
                const s = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('live_clock').innerText = h + ':' + m + ':' + s;
            }
            updateClock();
            setInterval(updateClock, 1000);
        </script>
        """,
        height=85
    )

st.markdown("<h1 style='text-align:center;'>🦍 KINGKONG CHAT</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "🦍" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Escribe un mensaje a KingKong...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🦍"):
        historial = [{"role": "system", "content": "Eres KingKong, un asistente conciso, ágil y directo."}]
        for m in st.session_state.messages:
            historial.append({"role": m["role"], "content": m["content"]})

        full_text = ""
        modelos_disponibles = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        stream = None
        error_capturado = None

        for modelo in modelos_disponibles:
            try:
                stream = client.chat.completions.create(
                    model=modelo,
                    messages=historial,
                    stream=True
                )
                break
            except Exception as err:
                error_capturado = err
                continue

        if stream is not None:
            def stream_gen():
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            full_text = st.write_stream(stream_gen())
        else:
            full_text = f"⚠️ Error en Groq: {error_capturado}"
            st.error(full_text)

    st.session_state.messages.append({"role": "assistant", "content": full_text})
