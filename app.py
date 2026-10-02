import streamlit as st
import streamlit.components.v1 as components
import concurrent.futures
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import base64

# =================================================
# COMPATIBILIDAD CON SDK DE GOOGLE
# =================================================

USE_NEW_SDK = False
try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        USE_NEW_SDK = False
    except ImportError:
        pass

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

# Prioridad absoluta a los modelos 3.5 a 3.1 y versiones Lite
MODELOS_RAPIDOS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash"
]

defaults = {
    "messages": [],
    "room_messages": [],
    "user_name": "Explorador",
    "theme_color": "#39FF14",
    "secondary_color": "#00C853",
    "input_color": "#FFFFFF",
    "font_size": 16,
    "radius": 18,
    "active_model_name": "gemini-3.5-flash-lite"
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =================================================
# CONEXIÓN CON API KEY
# =================================================

load_dotenv()

API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    API_KEY = os.getenv("GEMINI_API_KEY")

connected = bool(API_KEY)

def ejecutar_consulta_rapida(prompt_text: str, model_name: str, key: str, timeout_seg: int = 3) -> str:
    """Ejecuta la llamada con un timeout muy corto para no demorar."""
    def _call():
        if USE_NEW_SDK:
            client = genai.Client(api_key=key)
            res = client.models.generate_content(
                model=model_name,
                contents=prompt_text
            )
            return res.text
        else:
            import google.generativeai as legacy
            legacy.configure(api_key=key)
            m = legacy.GenerativeModel(model_name)
            res = m.generate_content(prompt_text)
            return res.text

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_call)
        return future.result(timeout=timeout_seg)

# =================================================
# ESTILOS CSS (LETRAS BLANCAS Y CERO FRANJA BLANCA)
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    /* Fondo continuo */
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

    /* Eliminar barra inferior blanca */
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

    /* Entrada de texto blanca */
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

    /* Letras 100% blancas en la conversación */
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

    /* Sidebar translúcido */
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

    if connected:
        st.success("🟢 IA ONLINE", icon="⚡")
        st.caption(f"⚡ Motor: `{st.session_state.active_model_name}`")
    else:
        st.error("🔴 IA OFFLINE (Revisa API Key)", icon="⚠️")

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
# PANTALLA: CHAT CON IA (RESPUESTAS ULTRA-RÁPIDAS)
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
        st.info("💡 Ingresa tu `GEMINI_API_KEY` temporal:")
        temp_key = st.text_input("Gemini API Key:", type="password")
        if temp_key:
            API_KEY = temp_key
            connected = True
            st.rerun()

    for msg in st.session_state.messages:
        avatar = "🦍" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    prompt = st.chat_input("Escribe un mensaje a la IA...")

    if prompt:
        # Guardar y mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            full_response = ""
            modelo_exitoso = None

            if connected and API_KEY:
                # El modelo activo va primero para contestar sin retrasos
                cola_modelos = [st.session_state.active_model_name] + [
                    m for m in MODELOS_RAPIDOS if m != st.session_state.active_model_name
                ]

                with st.spinner("🦍 Respondiendo..."):
                    for candidate in cola_modelos:
                        try:
                            # 3 segundos máximo por intento; pasa de inmediato al siguiente
                            full_response = ejecutar_consulta_rapida(prompt, candidate, API_KEY, timeout_seg=3)
                            if full_response:
                                modelo_exitoso = candidate
                                st.session_state.active_model_name = candidate  # Fijar el que funcionó
                                break
                        except Exception:
                            continue

                if full_response:
                    st.markdown(full_response)
                    st.caption(f"⚡ *Modelo: `{modelo_exitoso}`*")
                else:
                    full_response = "⚠️ No hubo respuesta rápida. Intenta enviar de nuevo."
                    st.error(full_response)
            else:
                full_response = "⚠️ La IA no está conectada. Configura tu GEMINI_API_KEY."
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
        
        st.subheader("🤖 Modelo Prioritario")
        st.session_state.active_model_name = st.selectbox(
            "Seleccionar modelo preferente:",
            MODELOS_RAPIDOS,
            index=MODELOS_RAPIDOS.index(st.session_state.active_model_name) if st.session_state.active_model_name in MODELOS_RAPIDOS else 0
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

