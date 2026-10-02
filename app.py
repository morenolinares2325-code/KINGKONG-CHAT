import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import os
import base64
from groq import Groq

# =================================================
# CONFIGURACIÓN DE PÁGINA
# =================================================

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
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

# =================================================
# CONEXIÓN CON GROQ
# =================================================

GROQ_KEY = (
    os.getenv("GROQ_API_KEY")
    or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
    or "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"
)

client = Groq(api_key=GROQ_KEY)

# =================================================
# ESTADOS DE SESIÓN (SESSION STATE)
# =================================================

defaults = {
    "messages": [],
    "room_messages": [],
    "user_name": "Explorador",
    "theme_color": "#39FF14",
    "secondary_color": "#00C853",
    "input_color": "#FFFFFF",
    "font_size": 16,
    "radius": 18
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =================================================
# ESTILOS CSS (JUNGLE CONSOLE EDITION)
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
        background-image: 
            linear-gradient(rgba(0, 0, 0, 0.78), rgba(4, 12, 6, 0.88)),
            {bg_css if bg_css else "none"} !important;
        background-color: #0b110e !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }}

    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    [data-testid="stBottom"],
    footer,
    [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    .stChatFloatingInputContainer,
    [data-testid="stChatInput"],
    .stChatInputContainer {{
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding-bottom: 20px !important;
    }}

    .stChatInput textarea, 
    .stChatInput input {{
        background-color: {st.session_state.input_color} !important;
        color: #111111 !important;
        font-size: {st.session_state.font_size}px !important;
        font-weight: 500 !important;
        border: 2px solid {st.session_state.theme_color} !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4), 0 0 12px {st.session_state.theme_color}44 !important;
    }}

    .stChatInput button {{
        color: {st.session_state.theme_color} !important;
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(16, 26, 18, 0.82) !important;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: {st.session_state.radius}px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
    }}

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div, 
    [data-testid="stChatMessage"] li {{
        color: #FFFFFF !important;
        font-size: {st.session_state.font_size}px !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.95);
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(3, 15, 6, 0.95), rgba(7, 24, 12, 0.95)) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid {st.session_state.theme_color}55;
    }}

    h1, h2, h3 {{
        color: {st.session_state.theme_color} !important;
        text-shadow: 0 0 10px {st.session_state.theme_color}66, 0 0 25px {st.session_state.theme_color}33;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}

    footer {{
        visibility: hidden;
    }}
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
            <span style="font-size: 64px; filter: drop-shadow(0 0 10px {st.session_state.theme_color});">🦍</span>
            <h2 style="margin: 0; font-size: 24px; letter-spacing: 2px;">KINGKONG CHAT</h2>
            <p style="font-size: 11px; opacity: 0.6; color: #fff;">JUNGLE CONSOLE EDITION</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    menu = st.radio(
        "Navegación",
        ["💬 KingKong Chat", "👥 Sala de Conversación", "📁 Archivos", "⚙️ Ajustes"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.success("🟢 SISTEMA CONECTADO", icon="⚡")

    components.html(
        f"""
        <div style="
            text-align: center;
            padding: 8px;
            background: rgba(0,0,0,0.4);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            font-family: 'Segoe UI', Roboto, sans-serif;
            margin-top: 10px;
        ">
            <div style="color: #aaa; font-size: 10px; letter-spacing: 1px;">TIEMPO EN VIVO</div>
            <div id="live_clock" style="font-size: 22px; font-weight: bold; color: {st.session_state.theme_color};">00:00:00</div>
        </div>
        <script>
            function updateClock() {{
                const now = new Date();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('live_clock').innerText = hours + ':' + minutes + ':' + seconds;
            }}
            updateClock();
            setInterval(updateClock, 1000);
        </script>
        """,
        height=85
    )

# =================================================
# PANTALLA: CHAT PRINCIPAL (GROQ RESILIENTE)
# =================================================

if menu == "💬 KingKong Chat":
    st.markdown(
        """
        <h1 style="text-align:center; font-size: 42px; margin-bottom: 20px;">
        🦍 KINGKONG CHAT
        </h1>
        """,
        unsafe_allow_html=True
    )

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
            historial = [
                {"role": "system", "content": "Eres KingKong, un asistente conciso, ágil, directo y servicial con estilo selvático."}
            ]
            for m in st.session_state.messages:
                historial.append({"role": m["role"], "content": m["content"]})

            full_response = ""
            stream = None
            error_msg = None

            # Modelos válidos en la infraestructura actual de Groq
            candidatos = [
                "llama-3.3-70b-versatile",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768"
            ]

            for model_id in candidatos:
                try:
                    stream = client.chat.completions.create(
                        model=model_id,
                        messages=historial,
                        stream=True
                    )
                    break
                except Exception as e:
                    error_msg = str(e)
                    continue

            if stream is not None:
                def stream_text():
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                full_response = st.write_stream(stream_text())
            else:
                full_response = f"⚠️ Error en Groq: {error_msg}"
                st.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PANTALLA: SALA HUMANA (SIN IA)
# =================================================

elif menu == "👥 Sala de Conversación":
    st.markdown(
        """
        <h1 style="text-align:center; font-size: 38px; margin-bottom: 5px;">
        👥 SALA DE CONVERSACIÓN
        </h1>
        <p style="text-align:center; opacity: 0.7; font-size: 14px; margin-bottom: 25px;">
        Espacio directo entre personas: comparte mensajes, fotos y archivos sin intervención de la máquina.
        </p>
        """,
        unsafe_allow_html=True
    )

    for msg in st.session_state.room_messages:
        with st.chat_message("user", avatar="💬"):
            st.markdown(f"**{msg['user']}** <small style='opacity:0.6;'>({msg['time']})</small>", unsafe_allow_html=True)
            if msg.get("text"):
                st.markdown(msg["text"])
            if msg.get("file_name"):
                if msg.get("is_image"):
                    st.image(msg["file_path"], caption=msg["file_name"], width=350)
                else:
                    st.markdown(f"📎 **Archivo adjunto:** `{msg['file_name']}`")

    # Contenedor seguro sin colisión de variables
    st.markdown("---")
    col_u, col_t = st.columns([1, 3])
    with col_u:
        alias_in = st.text_input("Alias:", value=st.session_state.user_name, key="sala_alias_key")
    with col_t:
        text_in = st.text_input("Mensaje:", placeholder="Escribe algo aquí...", key="sala_text_key")

    file_in = st.file_uploader("Adjuntar archivo o imagen (opcional):", key="sala_file_key")
    btn_enviar = st.button("📤 Enviar Mensaje a la Sala", use_container_width=True)

    if btn_enviar and (text_in or file_in):
        st.session_state.user_name = alias_in
        hora_actual = datetime.now().strftime("%H:%M")
        nuevo_mensaje = {
            "user": alias_in,
            "time": hora_actual,
            "text": text_in if text_in else "",
            "file_name": None,
            "file_path": None,
            "is_image": False
        }

        if file_in:
            ruta_guardada = UPLOADS_DIR / file_in.name
            with open(ruta_guardada, "wb") as f:
                f.write(file_in.getbuffer())

            nuevo_mensaje["file_name"] = file_in.name
            nuevo_mensaje["file_path"] = str(ruta_guardada)
            nuevo_mensaje["is_image"] = file_in.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))

        st.session_state.room_messages.append(nuevo_mensaje)
        st.rerun()

# =================================================
# PANTALLA: ARCHIVOS Y FONDO
# =================================================

elif menu == "📁 Archivos":
    st.title("📁 Gestor de Archivos y Fondo")

    st.subheader("🖼️ Cambiar Fondo de Pantalla")
    nuevo_fondo = st.file_uploader(
        "Subir nueva imagen de fondo",
        type=["jpg", "jpeg", "png"],
        key="uploader_fondo"
    )

    if nuevo_fondo:
        dest_path = ASSETS_DIR / "jungle.jpg"
        with open(dest_path, "wb") as f:
            f.write(nuevo_fondo.getbuffer())
        st.success("✅ ¡Fondo actualizado con éxito! Recargando...")
        st.rerun()

    st.markdown("---")
    st.subheader("📄 Archivos en el servidor")
    archivos_guardados = list(UPLOADS_DIR.glob("*"))
    if archivos_guardados:
        for arc in archivos_guardados:
            st.text(f"• {arc.name} ({round(arc.stat().st_size / 1024, 1)} KB)")
    else:
        st.caption("No hay archivos subidos todavía.")

# =================================================
# PANTALLA: AJUSTES
# =================================================

else:
    st.title("⚙️ Ajustes de KingKong")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 Colores y Tema")
        st.session_state.theme_color = st.color_picker("Color Neón Principal", st.session_state.theme_color)
        st.session_state.secondary_color = st.color_picker("Color Secundario", st.session_state.secondary_color)
        st.session_state.input_color = st.color_picker("Color Fondo Entrada de Texto", st.session_state.input_color)

    with col2:
        st.subheader("📐 Dimensiones y Formato")
        st.session_state.font_size = st.slider("Tamaño de Texto en Chat (px)", 12, 26, st.session_state.font_size)
        st.session_state.radius = st.slider("Curvatura de Bordes (px)", 0, 35, st.session_state.radius)

    st.markdown("---")
    st.subheader("🧹 Mantenimiento")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Borrar Historial de Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("Historial eliminado.")
            st.rerun()

    with col_btn2:
        if st.button("🗑️ Borrar Mensajes de Sala", use_container_width=True):
            st.session_state.room_messages = []
            st.success("Historial de la sala eliminado.")
            st.rerun()
