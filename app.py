import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import base64

# =================================================
# COMPATIBILIDAD CON LIBRERÍAS DE IA
# =================================================

# 1. Groq (Ultra-rápido)
HAS_GROQ = False
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# 2. Gemini
HAS_GEMINI = False
try:
    from google import genai
    HAS_GEMINI = True
    USE_NEW_GEMINI = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        HAS_GEMINI = True
        USE_NEW_GEMINI = False
    except ImportError:
        HAS_GEMINI = False

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
    "radius": 18,
    "ai_engine": "Groq (Ultra-Rápido)",
    "groq_model": "llama-3.3-70b-versatile"
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Modelos recomendados para Groq
MODELOS_GROQ = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

# =================================================
# CARGA DE API KEYS
# =================================================

load_dotenv()

# Groq Key
GROQ_KEY = None
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
elif os.getenv("GROQ_API_KEY"):
    GROQ_KEY = os.getenv("GROQ_API_KEY")

# Gemini Key
GEMINI_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

groq_connected = bool(GROQ_KEY and HAS_GROQ)
gemini_connected = bool(GEMINI_KEY and HAS_GEMINI)

# =================================================
# ESTILOS CSS (LETRAS BLANCAS Y CERO FRANJA BLANCA)
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    /* 1. Fondo global oscuro continuo */
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

    /* 2. Quitar barra blanca inferior de Streamlit */
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

    /* 3. Píldora de texto blanca */
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

    /* 4. Letras 100% blancas en la conversación */
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

    /* 5. Barra lateral */
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
        ["💬 Chat con IA", "👥 Sala de Chat (Sin IA)", "📁 Archivos", "⚙️ Ajustes"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Selector de motor
    st.session_state.ai_engine = st.selectbox(
        "Motor de Inteligencia:",
        ["Groq (Ultra-Rápido)", "Google Gemini"],
        index=0 if "Groq" in st.session_state.ai_engine else 1
    )

    if "Groq" in st.session_state.ai_engine:
        if groq_connected:
            st.success("🟢 GROQ ONLINE", icon="⚡")
            st.caption(f"🚀 Modelo: `{st.session_state.groq_model}`")
        else:
            st.error("🔴 GROQ OFFLINE", icon="⚠️")
    else:
        if gemini_connected:
            st.success("🟢 GEMINI ONLINE", icon="⚡")
        else:
            st.error("🔴 GEMINI OFFLINE", icon="⚠️")

    # Reloj en vivo continuo
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
# PANTALLA: CHAT CON IA (STREAMING ULTRA-VELOZ)
# =================================================

if menu == "💬 Chat con IA":
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size: 42px; margin-bottom: 20px;">
        🦍 KINGKONG CHAT
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Si falta la clave de Groq, permitir ponerla aquí
    if "Groq" in st.session_state.ai_engine and not groq_connected:
        st.info("💡 Ingresa tu `GROQ_API_KEY` temporal o guárdala en Secrets / .env:")
        temp_groq = st.text_input("Groq API Key (comienza por gsk_):", type="password")
        if temp_groq:
            GROQ_KEY = temp_groq
            groq_connected = True
            st.rerun()

    # Mostrar historial
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
            full_response = ""

            # --- RESPUESTA CON GROQ (INSTANTÁNEA CON STREAMING) ---
            if "Groq" in st.session_state.ai_engine:
                if groq_connected and GROQ_KEY:
                    try:
                        client_groq = Groq(api_key=GROQ_KEY)
                        # Preparamos el historial para contexto conversacional
                        mensajes_api = [
                            {"role": "system", "content": "Eres KingKong AI, un asistente inteligente, directo, astuto y servicial en un entorno selvático y tecnológico."}
                        ]
                        for m in st.session_state.messages:
                            mensajes_api.append({"role": m["role"], "content": m["content"]})

                        stream = client_groq.chat.completions.create(
                            model=st.session_state.groq_model,
                            messages=mensajes_api,
                            stream=True
                        )

                        def generar_groq():
                            for chunk in stream:
                                if chunk.choices and chunk.choices[0].delta.content:
                                    yield chunk.choices[0].delta.content

                        full_response = st.write_stream(generar_groq())
                        st.caption(f"⚡ *Groq LPU Engine: `{st.session_state.groq_model}`*")
                    except Exception as e:
                        full_response = f"⚠️ Error en Groq: {e}"
                        st.error(full_response)
                else:
                    full_response = "⚠️ Falta configurar tu GROQ_API_KEY."
                    st.warning(full_response)

            # --- RESPUESTA CON GEMINI (ALTERNATIVA) ---
            else:
                if gemini_connected and GEMINI_KEY:
                    try:
                        import google.generativeai as legacy
                        legacy.configure(api_key=GEMINI_KEY)
                        m = legacy.GenerativeModel("gemini-3.5-flash-lite")
                        response = m.generate_content(prompt, stream=True)
                        
                        def generar_gemini():
                            for chunk in response:
                                if chunk.text:
                                    yield chunk.text

                        full_response = st.write_stream(generar_gemini())
                        st.caption("⚡ *Gemini 3.5 Flash-Lite Engine*")
                    except Exception as e:
                        full_response = f"⚠️ Error en Gemini: {e}"
                        st.error(full_response)
                else:
                    full_response = "⚠️ Falta configurar tu GEMINI_API_KEY."
                    st.warning(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PANTALLA: SALA HUMANA (SIN IA)
# =================================================

elif menu == "👥 Sala de Chat (Sin IA)":
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size: 38px; margin-bottom: 5px;">
        👥 SALA DE CONVERSACIÓN
        </h1>
        <p style="text-align:center; opacity: 0.7; font-size: 14px; margin-bottom: 25px;">
        Chat directo: mensajes, imágenes y archivos sin uso de IA.
        </p>
        """,
        unsafe_allow_html=True
    )

    with st.expander("👤 Configurar tu Nombre y Adjuntar Archivos", expanded=False):
        col_u, col_f = st.columns([1, 2])
        with col_u:
            st.session_state.user_name = st.text_input("Tu nombre / alias:", value=st.session_state.user_name)
        with col_f:
            archivo_compartido = st.file_uploader("Adjuntar archivo o imagen:", key="uploader_sala")

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

    mensaje_sala = st.chat_input("Escribe en la sala para todos...")

    if mensaje_sala or (archivo_compartido and st.button("📤 Enviar Archivo a la Sala")):
        hora_actual = datetime.now().strftime("%H:%M")
        nuevo_mensaje = {
            "user": st.session_state.user_name,
            "time": hora_actual,
            "text": mensaje_sala if mensaje_sala else "",
            "file_name": None,
            "file_path": None,
            "is_image": False
        }

        if archivo_compartido:
            ruta_guardada = UPLOADS_DIR / archivo_compartido.name
            with open(ruta_guardada, "wb") as f:
                f.write(archivo_compartido.getbuffer())
            
            nuevo_mensaje["file_name"] = archivo_compartido.name
            nuevo_mensaje["file_path"] = str(ruta_guardada)
            nuevo_mensaje["is_image"] = archivo_compartido.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))

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
        
        st.subheader("🚀 Modelo de Groq")
        st.session_state.groq_model = st.selectbox(
            "Seleccionar modelo de Groq:",
            MODELOS_GROQ,
            index=MODELOS_GROQ.index(st.session_state.groq_model) if st.session_state.groq_model in MODELOS_GROQ else 0
        )

    st.markdown("---")
    st.subheader("🧹 Mantenimiento")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Borrar Historial IA", use_container_width=True):
            st.session_state.messages = []
            st.success("Historial de IA eliminado.")
            st.rerun()

    with col_btn2:
        if st.button("🗑️ Borrar Mensajes Sala Humana", use_container_width=True):
            st.session_state.room_messages = []
            st.success("Historial de la sala eliminado.")
            st.rerun()
