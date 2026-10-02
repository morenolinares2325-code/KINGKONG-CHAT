import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import base64

# =================================================
# CONFIGURACIÓN DE PÁGINA
# =================================================

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# RUTAS Y FUNCIONES AUXILIARES
# =================================================

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"

ASSETS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

def image_to_base64(path: Path) -> str:
    """Convierte una imagen local a base64 de manera segura."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def get_background_css() -> str:
    """Detecta y genera el CSS para el fondo de pantalla."""
    posibles_fondos = [
        ASSETS_DIR / "jungle.jpg",
        ASSETS_DIR / "jungle.png",
        ASSETS_DIR / "jungle.jpeg"
    ]
    for fondo in posibles_fondos:
        if fondo.exists():
            b64 = image_to_base64(fondo)
            mime = "png" if fondo.suffix.lower() == ".png" else "jpeg"
            return f'url("data:image/{mime};base64,{b64}")'
    return ""

# =================================================
# ESTADOS DE SESIÓN (SESSION STATE)
# =================================================

defaults = {
    "messages": [],
    "theme_color": "#39FF14",       # Verde neón
    "secondary_color": "#00C853",   # Verde selva
    "input_color": "#FFFFFF",       # Caja de chat blanca
    "font_size": 16,
    "radius": 18,
    "chat_width": 1000
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =================================================
# CONEXIÓN CON GEMINI (SECRETS Y .ENV)
# =================================================

load_dotenv()

# Lee de st.secrets (Streamlit Cloud o .streamlit/secrets.toml) o de .env
API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    API_KEY = os.getenv("GEMINI_API_KEY")

connected = False
model = None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # Usamos gemini-2.0-flash para evitar el 404
        model = genai.GenerativeModel("gemini-2.0-flash")
        connected = True
    except Exception as e:
        connected = False

# =================================================
# ESTILOS CSS AVANZADOS (SIN FRANJA BLANCA)
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    /* 1. Fondo global oscuro de jungla */
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

    /* 2. Barra superior transparente */
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    /* 3. ELIMINAR LA FRANJA BLANCA INFERIOR DE STREAMLIT */
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

    /* 4. ÚNICAMENTE LA CAJA DE TEXTO BLANCA ESTILO TELEGRAM */
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

    /* 5. Barra lateral con efecto cristal */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(3, 15, 6, 0.95), rgba(7, 24, 12, 0.95)) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid {st.session_state.theme_color}55;
    }}

    /* 6. Burbujas de mensajes */
    [data-testid="stChatMessage"] {{
        background: rgba(16, 26, 18, 0.70) !important;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {st.session_state.radius}px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
    }}

    [data-testid="stChatMessage"]:hover {{
        border-color: {st.session_state.theme_color}66;
    }}

    /* 7. Tipografía Neón */
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
# SIDEBAR (PANEL LATERAL)
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
        ["💬 Chat", "📁 Archivos", "⚙️ Ajustes"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Estado de la IA
    if connected:
        st.success("🟢 IA ONLINE (Gemini)", icon="⚡")
    else:
        st.error("🔴 IA OFFLINE (Revisa API Key)", icon="⚠️")

    # Reloj en vivo
    reloj = datetime.now().strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <small style="color: #aaa;">HORA LOCAL</small>
            <div style="font-size: 20px; font-weight: bold; color: {st.session_state.theme_color};">{reloj}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =================================================
# PANTALLA: CHAT
# =================================================

if menu == "💬 Chat":
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size: 42px; margin-bottom: 20px;">
        🦍 KINGKONG CHAT
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Si falta la API Key, opción de ingresarla en pantalla
    if not connected:
        st.info("💡 Ingresa tu `GEMINI_API_KEY` temporal o guárdala en Secrets / .env:")
        temp_key = st.text_input("Gemini API Key:", type="password")
        if temp_key:
            try:
                genai.configure(api_key=temp_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                connected = True
                st.success("¡Conectado exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al conectar: {e}")

    # Mostrar historial de mensajes
    for msg in st.session_state.messages:
        avatar = "🦍" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Entrada de mensaje
    prompt = st.chat_input("Escribe un mensaje en la selva...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            if connected and model:
                try:
                    response = model.generate_content(prompt, stream=True)
                    
                    def stream_generator():
                        for chunk in response:
                            yield chunk.text

                    full_response = st.write_stream(stream_generator())
                except Exception as e:
                    full_response = f"⚠️ Error en la jungla: {e}"
                    st.error(full_response)
            else:
                full_response = "⚠️ La IA no está conectada. Configura tu GEMINI_API_KEY en los Secrets de Streamlit o en el archivo `.env`."
                st.warning(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PANTALLA: ARCHIVOS Y FONDO
# =================================================

elif menu == "📁 Archivos":
    st.title("📁 Gestor de Archivos y Fondo")

    st.subheader("🖼️ Cambiar Fondo de Pantalla")
    st.caption("Sube aquí cualquier foto (JPG o PNG). Se aplicará al instante como fondo.")
    
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

    st.subheader("📄 Subir otros archivos a la carpeta `uploads/`")
    uploaded = st.file_uploader("Seleccionar archivo", key="uploader_archivos")

    if uploaded:
        with open(UPLOADS_DIR / uploaded.name, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"Archivo guardado: `{uploaded.name}`")

    archivos_guardados = list(UPLOADS_DIR.glob("*"))
    if archivos_guardados:
        st.write("### 📂 Archivos en el servidor:")
        for arc in archivos_guardados:
            st.text(f"• {arc.name} ({round(arc.stat().st_size / 1024, 1)} KB)")

# =================================================
# PANTALLA: AJUSTES Y PERSONALIZACIÓN
# =================================================

else:
    st.title("⚙️ Ajustes de KingKong")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 Colores y Tema")
        st.session_state.theme_color = st.color_picker(
            "Color Neón Principal",
            st.session_state.theme_color
        )

        st.session_state.secondary_color = st.color_picker(
            "Color Secundario",
            st.session_state.secondary_color
        )

        st.session_state.input_color = st.color_picker(
            "Color Fondo Entrada de Texto",
            st.session_state.input_color
        )

    with col2:
        st.subheader("📐 Dimensiones y Formato")
        st.session_state.font_size = st.slider(
            "Tamaño de Texto en Input (px)",
            12, 26,
            st.session_state.font_size
        )

        st.session_state.radius = st.slider(
            "Curvatura de Bordes (px)",
            0, 35,
            st.session_state.radius
        )

    st.markdown("---")
    
    st.subheader("🧹 Mantenimiento")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🗑️ Borrar Historial de Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("Historial eliminado.")
            st.rerun()

    with col_btn2:
        if st.button("🔄 Restaurar Estilos por Defecto", use_container_width=True):
            st.session_state.theme_color = "#39FF14"
            st.session_state.secondary_color = "#00C853"
            st.session_state.input_color = "#FFFFFF"
            st.session_state.font_size = 16
            st.session_state.radius = 18
            st.rerun()
