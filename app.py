import streamlit as st
import streamlit.components.v1 as components
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
    "messages": [],              # Chat con IA
    "room_messages": [],         # Chat entre personas
    "user_name": "Explorador",   # Alias en la sala
    "theme_color": "#39FF14",    # Verde neón
    "secondary_color": "#00C853",# Verde selva
    "input_color": "#FFFFFF",    # Caja de entrada blanca
    "font_size": 16,
    "radius": 18,
    "available_models": [],
    "active_model_name": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =================================================
# CONEXIÓN CON GEMINI (DETECCIÓN AUTOMÁTICA Y SEGURA)
# =================================================

load_dotenv()

API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    API_KEY = os.getenv("GEMINI_API_KEY")

connected = False

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        
        # Obtenemos los modelos reales compatibles con generateContent
        if not st.session_state.available_models:
            real_models = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    # Limpiamos el prefijo 'models/'
                    name = m.name.replace("models/", "")
                    real_models.append(name)
            
            st.session_state.available_models = real_models
            
            # Preferencia a modelos rápidos modernos
            preferidos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
            for pref in preferidos:
                if pref in real_models:
                    st.session_state.active_model_name = pref
                    break
            
            if not st.session_state.active_model_name and real_models:
                st.session_state.active_model_name = real_models[0]

        if st.session_state.active_model_name:
            connected = True
    except Exception as e:
        connected = False

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

    /* 2. Quitar la barra blanca inferior fija */
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

    /* 3. CAJA DE TEXTO BLANCA */
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

    /* 4. BURBUJAS DE CHAT CON LETRAS BLANCAS BIEN VISIBLES */
    [data-testid="stChatMessage"] {{
        background: rgba(16, 26, 18, 0.75) !important;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: {st.session_state.radius}px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
    }}

    /* Forzar texto en blanco puro en toda la conversación */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li {{
        color: #FFFFFF !important;
        font-size: {st.session_state.font_size}px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
    }}

    /* 5. Barra lateral cristal */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(3, 15, 6, 0.95), rgba(7, 24, 12, 0.95)) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid {st.session_state.theme_color}55;
    }}

    /* 6. Tipografía Neón */
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
        ["💬 Chat con IA", "👥 Sala de Chat (Sin IA)", "📁 Archivos", "⚙️ Ajustes"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Estado de la IA y modelo activo
    if connected and st.session_state.active_model_name:
        st.success("🟢 IA ONLINE", icon="⚡")
        st.caption(f"🤖 Modelo activo: `{st.session_state.active_model_name}`")
    else:
        st.error("🔴 IA OFFLINE (Revisa API Key)", icon="⚠️")

    # Reloj en vivo continuo vía JS
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
# PANTALLA: CHAT CON IA
# =================================================

if menu == "💬 Chat con IA":
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size: 42px; margin-bottom: 20px;">
        🦍 KINGKONG CHAT (IA)
        </h1>
        """,
        unsafe_allow_html=True
    )

    if not connected:
        st.info("💡 Ingresa tu `GEMINI_API_KEY` o configúrala en los Secrets:")
        temp_key = st.text_input("Gemini API Key:", type="password")
        if temp_key:
            try:
                genai.configure(api_key=temp_key)
                st.session_state.available_models = [m.name.replace("models/", "") for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
                if st.session_state.available_models:
                    st.session_state.active_model_name = st.session_state.available_models[0]
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
    prompt = st.chat_input("Escribe un mensaje a la IA...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            if connected and st.session_state.active_model_name:
                with st.spinner("Pensando en la selva... 🦍"):
                    try:
                        active_model = genai.GenerativeModel(st.session_state.active_model_name)
                        response = active_model.generate_content(prompt)
                        full_response = response.text
                        st.markdown(full_response)
                    except Exception as e:
                        full_response = f"⚠️ Error en la respuesta: {e}"
                        st.error(full_response)
            else:
                full_response = "⚠️ La IA no está conectada. Configura tu GEMINI_API_KEY."
                st.warning(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PANTALLA: SALA DE CHAT HUMANO (SIN IA)
# =================================================

elif menu == "👥 Sala de Chat (Sin IA)":
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size: 38px; margin-bottom: 5px;">
        👥 SALA DE CONVERSACIÓN
        </h1>
        <p style="text-align:center; opacity: 0.7; font-size: 14px; margin-bottom: 25px;">
        Chat directo: comparte mensajes, imágenes y archivos sin intervención de la IA.
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
    st.caption("Sube aquí cualquier foto (JPG o PNG) y se aplicará inmediatamente.")
    
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
            "Tamaño de Texto en Chat (px)",
            12, 26,
            st.session_state.font_size
        )

        st.session_state.radius = st.slider(
            "Curvatura de Bordes (px)",
            0, 35,
            st.session_state.radius
        )

        if st.session_state.available_models:
            st.subheader("🤖 Modelo de Gemini")
            st.session_state.active_model_name = st.selectbox(
                "Seleccionar modelo activo:",
                st.session_state.available_models,
                index=st.session_state.available_models.index(st.session_state.active_model_name) if st.session_state.active_model_name in st.session_state.available_models else 0
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
