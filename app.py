import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import os
import json
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
CONFIG_FILE = BASE_DIR / "theme_config.json"

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
# PERSISTENCIA DE CONFIGURACIÓN DE COLORES
# =================================================

default_settings = {
    "theme_color": "#00FF66",
    "secondary_color": "#00C853",
    "input_color": "#0d1a10",
    "text_color": "#FFFFFF",
    "code_bg_color": "#17212b",
    "code_text_color": "#00FF66",
    "font_size": 16,
    "radius": 14,
    "user_name": "Explorador"
}

saved_settings = {}
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            saved_settings = json.load(f)
    except Exception:
        pass

for key, default_val in default_settings.items():
    if key not in st.session_state:
        st.session_state[key] = saved_settings.get(key, default_val)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "room_messages" not in st.session_state:
    st.session_state.room_messages = []

# =================================================
# CONEXIÓN CON GROQ (TU MOTOR ORIGINAL)
# =================================================

GROQ_KEY = (
    os.getenv("GROQ_API_KEY")
    or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
    or "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"
)

client = Groq(api_key=GROQ_KEY)

# =================================================
# ESTILOS CSS: OSCURO SELVA + NEÓN + TEXTO BLANCO
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    /* 1. Fondo de la aplicación */
    [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
        background-image: 
            linear-gradient(rgba(4, 10, 6, 0.88), rgba(6, 13, 9, 0.95)),
            {bg_css if bg_css else "none"} !important;
        background-color: #060d09 !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }}

    /* 2. Barra lateral en blanco nítido y estilo Jungle Dark */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(5, 16, 9, 0.98), rgba(8, 22, 13, 0.98)) !important;
        backdrop-filter: blur(15px);
        border-right: 1.5px solid {st.session_state.theme_color}44 !important;
    }}
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label div {{
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1.02rem !important;
    }}

    /* 3. Eliminación del marco blanco inferior */
    [data-testid="stBottom"],
    footer,
    [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    .stChatFloatingInputContainer,
    [data-testid="stChatInput"],
    .stChatInputContainer {{
        background-color: #0d1a10 !important;
        border: 1.5px solid {st.session_state.theme_color} !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.25) !important;
    }}

    .stChatInput textarea, 
    .stChatInput input {{
        background-color: transparent !important;
        color: #ffffff !important;
        font-size: {st.session_state.font_size}px !important;
    }}
    .stChatInput textarea::placeholder {{
        color: #728c7b !important;
    }}

    /* 4. Mensajes del chat: Legibles, fondo oscuro y texto blanco */
    [data-testid="stChatMessage"] {{
        background: rgba(14, 26, 17, 0.9) !important;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 255, 102, 0.25) !important;
        border-radius: {st.session_state.radius}px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
        margin-bottom: 12px;
    }}

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li {{
        color: #ffffff !important;
        font-size: {st.session_state.font_size}px !important;
    }}

    /* 5. Cajas de código */
    [data-testid="stChatMessage"] pre,
    [data-testid="stChatMessage"] div[data-testid="stCodeBlock"],
    [data-testid="stChatMessage"] pre > code {{
        background-color: {st.session_state.code_bg_color} !important;
        color: {st.session_state.code_text_color} !important;
        font-family: 'Consolas', monospace !important;
        border-radius: 10px !important;
    }}

    /* 6. Tu mono original con resplandor neón */
    .gorila-original-aura {{
        font-size: 5rem;
        display: inline-block;
        filter: drop-shadow(0 0 20px {st.session_state.theme_color}) drop-shadow(0 0 40px {st.session_state.theme_color}77);
        margin-bottom: 2px;
    }}

    .titulo-kingkong-neon {{
        color: {st.session_state.theme_color} !important;
        font-weight: 900 !important;
        letter-spacing: 3px !important;
        font-size: 2.2rem !important;
        margin: 5px 0 0 0 !important;
        text-shadow: 0 0 15px {st.session_state.theme_color}99;
        text-align: center;
    }}

    .subtitulo-jungle {{
        color: #8da0b0 !important;
        letter-spacing: 2.5px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-align: center;
        margin-bottom: 22px;
    }}

    /* Botón de descarga APK */
    div.stDownloadButton > button {{
        background: linear-gradient(135deg, {st.session_state.theme_color} 0%, #059669 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-top: 10px !important;
    }}

    footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# SIDEBAR (PANEL LATERAL COMPLETO)
# =================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: -10px;">
            <span style="font-size: 55px; filter: drop-shadow(0 0 12px {st.session_state.theme_color});">🦍</span>
            <h2 style="margin: 0; font-size: 22px; letter-spacing: 2px; color: {st.session_state.theme_color};">KINGKONG CHAT</h2>
            <p style="font-size: 11px; opacity: 0.7; color: #fff;">JUNGLE CONSOLE EDITION</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    menu = st.radio(
        "Navegación",
        ["💬 KingKong Chat", "👥 Sala de Conversación", "📁 Archivos", "⚙️ Ajustes"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.success("🟢 SISTEMA CONECTADO", icon="⚡")

    components.html(
        f"""
        <div style="
            text-align: center;
            padding: 8px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 102, 0.2);
            font-family: 'Segoe UI', Roboto, sans-serif;
            margin-top: 5px;
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

    # Botón de Descarga del APK
    try:
        with open("KingkongChat.apk", "rb") as apk_f:
            st.download_button(
                label="📲 Descargar App Android (APK)",
                data=apk_f,
                file_name="KingkongChat.apk",
                mime="application/vnd.android.package-archive"
            )
    except FileNotFoundError:
        st.caption("ℹ️️ Coloca 'KingkongChat.apk' en tu repo para descarga.")

# =================================================
# FUNCIÓN DE LLAMADA A GROQ CON STREAMING
# =================================================

def llamar_a_groq(historial_mensajes):
    historial = [
        {
            "role": "system",
            "content": (
                "Eres KingKong IA, un asistente avanzado, conciso y de alto rendimiento. "
                "Eres analítico, profesional y experto en trading, mercados financieros y tecnología. "
                "Responde siempre en español y de forma directa y estructurada."
            )
        }
    ]
    ultimos_mensajes = historial_mensajes[-8:]
    for m in ultimos_mensajes:
        txt = (m.get("content") or m.get("text") or "").strip()
        if txt and not txt.startswith("⚠️"):
            if len(txt) > 12000:
                txt = txt[:12000] + "\n\n[... Truncado ...]"
            historial.append({"role": m.get("role", "user"), "content": txt})

    candidatos = []
    try:
        modelos_remotos = client.models.list().data
        for mod in modelos_remotos:
            m_id = mod.id.lower()
            if any(bad in m_id for bad in ["whisper", "guard", "orpheus", "safeguard"]):
                continue
            candidatos.append(mod.id)
    except Exception:
        pass

    prioritarios = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    lista_final = [m for m in prioritarios if m in candidatos] + [m for m in candidatos if m not in prioritarios]
    if not lista_final:
        lista_final = prioritarios

    stream = None
    ultimo_error = None
    for m_id in lista_final:
        try:
            stream = client.chat.completions.create(
                model=m_id,
                messages=historial,
                stream=True
            )
            break
        except Exception as e:
            ultimo_error = e
            continue

    if stream is not None:
        def stream_text():
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        return st.write_stream(stream_text())
    else:
        err_msg = f"⚠️ Error en Groq: {ultimo_error}"
        st.error(err_msg)
        return err_msg

# =================================================
# PESTAÑA 1: 💬 KINGKONG CHAT (SOLO CON LA IA)
# =================================================

if menu == "💬 KingKong Chat":
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 5px;">
            <div class="gorila-original-aura">🦍</div>
            <div class="titulo-kingkong-neon">KINGKONG CHAT</div>
            <div class="subtitulo-jungle">JUNGLE CONSOLE EDITION · GROQ ULTRA-FAST</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for msg in st.session_state.messages:
        avatar = "🦍" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    prompt = st.chat_input("Escribe a KingKong (pide análisis de EUR/USD, datos, etc.)...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            full_response = llamar_a_groq(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PESTAÑA 2: 👥 SALA DE CONVERSACIÓN (COMPAÑEROS + TOGGLE IA)
# =================================================

elif menu == "👥 Sala de Conversación":
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 5px;">
            <div class="gorila-original-aura">👥</div>
            <div class="titulo-kingkong-neon">SALA DE GRUPO</div>
            <div class="subtitulo-jungle">ESPACIO DE CONVERSACIÓN Y COMPARTICIÓN</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for msg in st.session_state.room_messages:
        es_ia = msg.get("user") == "KingKong IA"
        avatar = "🦍" if es_ia else "💬"
        with st.chat_message("assistant" if es_ia else "user", avatar=avatar):
            color_autor = st.session_state.theme_color if es_ia else "#58a6ff"
            st.markdown(f"<span style='color: {color_autor}; font-weight: bold;'>{msg['user']}</span> <small style='opacity:0.6;'>({msg['time']})</small>", unsafe_allow_html=True)
            if msg.get("text"):
                st.markdown(msg["text"])
            if msg.get("file_name"):
                if msg.get("is_image"):
                    st.image(msg["file_path"], caption=msg["file_name"], width=350)
                else:
                    st.markdown(f"📎 **Archivo adjunto:** `{msg['file_name']}`")

    st.markdown("<br>", unsafe_allow_html=True)

    # Interruptor para activar la IA en el grupo
    col_tgl, col_info = st.columns([1, 2])
    with col_tgl:
        ia_en_grupo = st.toggle("🦍 IA Activa en Grupo", value=False)
    with col_info:
        if ia_en_grupo:
            st.caption("🟢 **IA CONECTADA:** Leerá los mensajes del grupo y participará.")
        else:
            st.caption("⚪ **IA EN SILENCIO:** Modo charla libre privada entre personas.")

    col_u, col_t = st.columns([1, 3])
    with col_u:
        alias_in = st.text_input("Tu Alias:", value=st.session_state.user_name, key="sala_alias_key")
    with col_t:
        text_in = st.text_input("Mensaje para el grupo:", placeholder="Escribe algo aquí...", key="sala_text_key")

    file_in = st.file_uploader("Adjuntar archivo o imagen (opcional):", key="sala_file_key")
    btn_enviar = st.button("📤 Enviar al Grupo", use_container_width=True)

    if btn_enviar and (text_in or file_in):
        st.session_state.user_name = alias_in
        hora_actual = datetime.now().strftime("%H:%M")
        nuevo_mensaje = {
            "user": alias_in,
            "role": "user",
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

        # Si el interruptor de IA está encendido, Groq interviene en la conversación
        if ia_en_grupo and text_in:
            with st.spinner("🦍 KingKong IA respondiendo al grupo..."):
                mensajes_formateados = [{"role": m.get("role", "user"), "content": m.get("text", "")} for m in st.session_state.room_messages]
                resp_ia = llamar_a_groq(mensajes_formateados)
                st.session_state.room_messages.append({
                    "user": "KingKong IA",
                    "role": "assistant",
                    "time": datetime.now().strftime("%H:%M"),
                    "text": resp_ia,
                    "file_name": None,
                    "file_path": None,
                    "is_image": False
                })

        st.rerun()

# =================================================
# PESTAÑA 3: 📁 ARCHIVOS Y FONDO
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
# PESTAÑA 4: ⚙️ AJUSTES (CONFIGURACIÓN Y RULETITA)
# =================================================

else:
    st.title("⚙️ Ajustes de KingKong")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 Colores Generales")
        st.session_state.theme_color = st.color_picker("Color Neón Principal", st.session_state.theme_color)
        st.session_state.secondary_color = st.color_picker("Color Secundario", st.session_state.secondary_color)
        st.session_state.text_color = st.color_picker("Color de Texto General", st.session_state.text_color)
        st.session_state.input_color = st.color_picker("Color Fondo Entrada de Texto", st.session_state.input_color)

    with col2:
        st.subheader("💻 Colores de Bloques de Código")
        st.session_state.code_bg_color = st.color_picker("Fondo del Bloque de Código", st.session_state.code_bg_color)
        st.session_state.code_text_color = st.color_picker("Texto del Bloque de Código", st.session_state.code_text_color)
        st.session_state.font_size = st.slider("Tamaño de Fuente (px)", 12, 26, st.session_state.font_size)
        st.session_state.radius = st.slider("Curvatura de Bordes (px)", 0, 35, st.session_state.radius)

    st.markdown("---")
    col_save, col_clear = st.columns(2)

    with col_save:
        if st.button("💾 Guardar Colores y Ajustes", use_container_width=True):
            settings_to_save = {
                "theme_color": st.session_state.theme_color,
                "secondary_color": st.session_state.secondary_color,
                "input_color": st.session_state.input_color,
                "text_color": st.session_state.text_color,
                "code_bg_color": st.session_state.code_bg_color,
                "code_text_color": st.session_state.code_text_color,
                "font_size": st.session_state.font_size,
                "radius": st.session_state.radius,
                "user_name": st.session_state.user_name
            }
            try:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(settings_to_save, f, indent=4)
                st.success("✅ Ajustes guardados permanentemente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    with col_clear:
        if st.button("🗑️ Borrar Historial de Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.room_messages = []
            st.success("Historiales eliminados.")
            st.rerun()
