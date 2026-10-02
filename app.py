import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import os
import base64
from groq import Groq

# =================================================
# CONFIGURACIÓN
# =================================================

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(file).resolve().parent if "file" in locals() else Path.cwd()
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"

ASSETS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

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

# Conexión directa a Groq
GROQ_KEY = (
    os.getenv("GROQ_API_KEY")
    or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
    or "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"
)
client = Groq(api_key=GROQ_KEY)

# =================================================
# ESTADOS DE SESIÓN
# =================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "room_messages" not in st.session_state:
    st.session_state.room_messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "Explorador"
if "theme_color" not in st.session_state:
    st.session_state.theme_color = "#39FF14"
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "radius" not in st.session_state:
    st.session_state.radius = 18

# =================================================
# ESTILOS CSS
# =================================================

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
        font-size: {st.session_state.font_size}px !important;
        border: 2px solid {st.session_state.theme_color} !important;
        border-radius: 25px !important;
    }}
    [data-testid="stChatMessage"] {{
        background: rgba(16, 26, 18, 0.82) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: {st.session_state.radius}px !important;
        margin-bottom: 12px;
    }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div {{
        color: #FFFFFF !important;
        font-size: {st.session_state.font_size}px !important;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(3,15,6,0.95), rgba(7,24,12,0.95)) !important;
        border-right: 2px solid {st.session_state.theme_color}55;
    }}
    h1, h2, h3 {{
        color: {st.session_state.theme_color} !important;
    }}
    footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# SIDEBAR
# =================================================
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: -15px;">
            <span style="font-size: 64px;">🦍</span>
            <h2 style="margin: 0; font-size: 24px;">KINGKONG CHAT</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    menu = st.radio("Navegación", ["💬 KingKong Chat", "👥 Sala de Conversación", "📁 Archivos", "⚙️ Ajustes"], label_visibility="collapsed")
    st.markdown("---")
    st.success("🟢 SISTEMA CONECTADO", icon="⚡")

    components.html(
        f"""
        <div style="text-align: center; padding: 8px; background: rgba(0,0,0,0.4); border-radius: 10px; font-family: sans-serif;">
            <div style="color: #aaa; font-size: 10px;">TIEMPO EN VIVO</div>
            <div id="live_clock" style="font-size: 22px; font-weight: bold; color: {st.session_state.theme_color};">00:00:00</div>
        </div>
        <script>
            function updateClock() {{
                const now = new Date();
                const h = String(now.getHours()).padStart(2, '0');
                const m = String(now.getMinutes()).padStart(2, '0');
                const s = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('live_clock').innerText = h + ':' + m + ':' + s;
            }}
            updateClock();
            setInterval(updateClock, 1000);
        </script>
        """,
        height=80
    )

# =================================================
# CHAT PRINCIPAL (GROQ DIRECTO)
# =================================================

if menu == "💬 KingKong Chat":
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

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=historial,
                stream=True
            )

            def stream_gen():
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            full_text = st.write_stream(stream_gen())

        st.session_state.messages.append({"role": "assistant", "content": full_text})

# =================================================
# SALA DE CONVERSACIÓN HUMANA
# =================================================

elif menu == "👥 Sala de Conversación":
    st.markdown("<h1 style='text-align:center;'>👥 SALA DE CONVERSACIÓN</h1>", unsafe_allow_html=True)

    for msg in st.session_state.room_messages:
        with st.chat_message("user", avatar="💬"):
            st.markdown(f"{msg['user']} <small>({msg['time']})</small>", unsafe_allow_html=True)
            if msg.get("text"):
                st.markdown(msg["text"])
            if msg.get("file_name"):
                if msg.get("is_image"):
                    st.image(msg["file_path"], caption=msg["file_name"], width=300)
                else:
                    st.markdown(f"📎 {msg['file_name']}")

    with st.form("form_sala", clear_on_submit=True):
c1, c2 = st.columns([1, 3])
        with c1:
            u_name = st.text_input("Alias:", value=st.session_state.user_name)
        with c2:
            t_msg = st.text_input("Mensaje:", placeholder="Escribe aquí...")
        up_file = st.file_uploader("Adjuntar archivo/imagen:", key="file_sala")
        submit = st.form_submit_button("📤 Enviar", use_container_width=True)

        if submit and (t_msg or up_file):
            st.session_state.user_name = u_name
            ahora = datetime.now().strftime("%H:%M")
            nuevo = {
                "user": u_name,
                "time": ahora,
                "text": t_msg if t_msg else "",
                "file_name": None,
                "file_path": None,
                "is_image": False
            }
            if up_file:
                path = UPLOADS_DIR / up_file.name
                with open(path, "wb") as f:
                    f.write(up_file.getbuffer())
                nuevo["file_name"] = up_file.name
                nuevo["file_path"] = str(path)
                nuevo["is_image"] = up_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            st.session_state.room_messages.append(nuevo)
            st.rerun()

# =================================================
# GESTOR DE ARCHIVOS
# =================================================

elif menu == "📁 Archivos":
    st.title("📁 Gestor de Archivos y Fondo")
    nuevo_fondo = st.file_uploader("Cambiar fondo", type=["jpg", "jpeg", "png"])
    if nuevo_fondo:
        with open(ASSETS_DIR / "jungle.jpg", "wb") as f:
            f.write(nuevo_fondo.getbuffer())
        st.success("Fondo actualizado.")
        st.rerun()

    st.markdown("---")
    for arc in list(UPLOADS_DIR.glob("*")):
        st.text(f"• {arc.name}")

# =================================================
# AJUSTES
# =================================================

else:
    st.title("⚙️ Ajustes")
    st.session_state.theme_color = st.color_picker("Color Neón", st.session_state.theme_color)
    st.session_state.font_size = st.slider("Tamaño de Fuente", 12, 24, st.session_state.font_size)
    st.session_state.radius = st.slider("Curvatura Burbujas", 0, 30, st.session_state.radius)
    if st.button("🗑️ Borrar Historial Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
