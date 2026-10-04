import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import os
import json
import base64
import time
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
SHARED_CHAT_FILE = BASE_DIR / "shared_chat_history.json"

try:
    if not ASSETS_DIR.exists():
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

try:
    if not UPLOADS_DIR.exists():
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

MAX_MENSAJES_SALA = 200

# =================================================
# HISTORIAL COMPARTIDO (AUTORRECICLABLE)
# =================================================

def cargar_mensajes_compartidos():
    if SHARED_CHAT_FILE.exists():
        try:
            with open(SHARED_CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_mensaje_compartido(nuevo_msg):
    mensajes = cargar_mensajes_compartidos()
    mensajes.append(nuevo_msg)
    if len(mensajes) > MAX_MENSAJES_SALA:
        mensajes = mensajes[-MAX_MENSAJES_SALA:]
    try:
        with open(SHARED_CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(mensajes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al sincronizar: {e}")

# =================================================
# PERSISTENCIA Y DETECCIÓN DE FONDO
# =================================================

def image_to_base64(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def get_background_css() -> str:
    rutas = [
        BASE_DIR / "mono.jpg",
        BASE_DIR / "mono.png",
        BASE_DIR / "mono.jpeg",
        ASSETS_DIR / "mono.jpg",
        ASSETS_DIR / "jungle.jpg",
        BASE_DIR / "jungle.jpg"
    ]
    for r in rutas:
        if r.exists():
            b64 = image_to_base64(r)
            mime = "png" if r.suffix.lower() == ".png" else "jpeg"
            return f'url("data:image/{mime};base64,{b64}")'
    return ""

default_settings = {
    "theme_color": "#00FF66",
    "secondary_color": "#00C853",
    "input_color": "#0d1a10",
    "text_color": "#FFFFFF",
    "code_bg_color": "#17212b",
    "code_text_color": "#00FF66",
    "font_size": 16,
    "radius": 14,
    "user_name": ""
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

# =================================================
# CONEXIÓN GROQ
# =================================================

GROQ_KEY = (
    os.getenv("GROQ_API_KEY")
    or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
    or "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"
)

client = Groq(api_key=GROQ_KEY)

# =================================================
# ESTILOS CSS CON FONDO VISIBLE
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    /* Fondo con transparencia optimizada para resaltar la imagen */
    [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
        background-image: 
            linear-gradient(rgba(4, 10, 6, 0.45), rgba(6, 13, 9, 0.60)),
            {bg_css if bg_css else "none"} !important;
        background-color: #060d09 !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }}

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
        border: 1.8px solid {st.session_state.theme_color} !important;
        border-radius: 18px !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.3) !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background-color: #0d1a10 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        caret-color: {st.session_state.theme_color} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: #728c7b !important;
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(14, 26, 17, 0.88) !important;
        backdrop-filter: blur(12px);
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

    [data-testid="stChatMessage"] pre,
    [data-testid="stChatMessage"] div[data-testid="stCodeBlock"],
    [data-testid="stChatMessage"] pre > code {{
        background-color: {st.session_state.code_bg_color} !important;
        color: {st.session_state.code_text_color} !important;
        font-family: 'Consolas', monospace !important;
        border-radius: 10px !important;
    }}

    .gorila-original-aura {{
        font-size: 4.8rem;
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
        margin-bottom: 18px;
    }}

    [data-testid="stSidebar"] a[data-testid="baseButton-secondary"],
    div.stDownloadButton > button {{
        background: linear-gradient(135deg, {st.session_state.theme_color} 0%, #059669 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-top: 10px !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
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

    st.link_button(
        label="📲 Descargar App Android (APK)",
        url="https://appsgeyser.io/20240166/KingKongChat",
        use_container_width=True
    )

# =================================================
# LLAMADAS GROQ (CHAT Y TRANSCRIPCIÓN DE AUDIO)
# =================================================

def llamar_a_groq(historial_mensajes):
    historial = [
        {
            "role": "system",
            "content": (
                "Eres KingKong IA, un asistente avanzado, conciso y de alto rendimiento. "
                "Eres analítico, profesional y experto en trading, mercados financieros y tecnología. "
                "Responde siempre en español de forma estructurada y precisa."
            )
        }
    ]
    ultimos = historial_mensajes[-8:]
    for m in ultimos:
        txt = (m.get("content") or m.get("text") or "").strip()
        if txt and not txt.startswith("⚠️"):
            if len(txt) > 12000:
                txt = txt[:12000] + "\n\n[... Truncado ...]"
            historial.append({"role": m.get("role", "user"), "content": txt})

    modelos = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]

    stream = None
    ultimo_error = None
    for m_id in modelos:
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

def transcribir_audio(audio_bytes):
    try:
        temp_audio = BASE_DIR / "temp_audio.wav"
        with open(temp_audio, "wb") as f:
            f.write(audio_bytes)
        with open(temp_audio, "rb") as f_aud:
            transcripcion = client.audio.transcriptions.create(
                file=("audio.wav", f_aud.read()),
                model="whisper-large-v3",
                language="es"
            )
        if temp_audio.exists():
            temp_audio.unlink()
        return transcripcion.text
    except Exception as e:
        st.error(f"Error procesando voz con Groq Whisper: {e}")
        return None

# =================================================
# PESTAÑA 1: 💬 KINGKONG CHAT (IA PURA + VOZ)
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

    # Grabar nota de voz opcional
    with st.expander("🎙️ Grabar Nota de Voz a KingKong"):
        audio_grabado = st.audio_input("Habla para consultar a la IA")
        if audio_grabado:
            texto_voz = transcribir_audio(audio_grabado.getvalue())
            if texto_voz:
                st.session_state.messages.append({"role": "user", "content": f"🎙️ {texto_voz}"})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"🎙️ *{texto_voz}*")
                with st.chat_message("assistant", avatar="🦍"):
                    resp = llamar_a_groq(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": resp})

    if prompt := st.chat_input("Escribe a KingKong..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            full_response = llamar_a_groq(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PESTAÑA 2: 👥 SALA CON AUTO-REFRESCO, VOZ Y MENCIÓN @IA
# =================================================

elif menu == "👥 Sala de Conversación":
    if not st.session_state.user_name:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 25px;">
                <div class="gorila-original-aura">👥</div>
                <div class="titulo-kingkong-neon">SALA DE GRUPO</div>
                <p style="color: #8da0b0; font-size: 0.9rem; margin-top: 8px;">Introduce tu alias para acceder al historial compartido</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            alias_temp = st.text_input("Tu Nombre / Alias:", placeholder="Ej: Alex, Trader...")
            if st.button("🚀 Entrar al Chat", use_container_width=True):
                if alias_temp.strip():
                    st.session_state.user_name = alias_temp.strip()
                    st.rerun()
        st.stop()

    # Barra superior con autorefresco
    col_t1, col_t2, col_t3 = st.columns([2.5, 1, 0.8])
    with col_t1:
        st.markdown(
            f"""
            <div style="padding-bottom: 2px;">
                <span style="font-size: 1.4rem; font-weight: 800; color: {st.session_state.theme_color};">👥 SALA DE GRUPO</span>
                <span style="font-size: 0.85rem; color: #8da0b0; margin-left: 10px;">Tú: <b style="color: #fff;">{st.session_state.user_name}</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_t2:
        auto_sync = st.toggle("🔄 Auto-sincronizar", value=True, help="Refresca mensajes en vivo cada 4 segundos")
    with col_t3:
        if st.button("🔄 Manual"):
            st.rerun()

    # Temporizador de auto-refresco
    if auto_sync:
        components.html(
            """
            <script>
                setTimeout(function() {
                    window.parent.document.querySelector('button[kind="secondaryFormSubmit"], button:has(div:contains("Manual"))')?.click();
                }, 4000);
            </script>
            """,
            height=0
        )

    col_tgl, col_info = st.columns([1, 2])
    with col_tgl:
        ia_en_grupo = st.toggle("🦍 Modo IA Permanente", value=False)
    with col_info:
        if ia_en_grupo:
            st.caption("🟢 **IA PERMANENTE:** Responde a cada intervención.")
        else:
            st.caption("💡 **TIP:** Menciona **@ia** o **@kingkong** en tu mensaje para llamarla solo cuando quieras.")

    # Notas de voz en la sala
    with st.expander("🎙️️ Enviar Nota de Voz a la Sala"):
        audio_sala = st.audio_input("Graba tu mensaje de voz para el grupo")
        if audio_sala:
            texto_transcrito = transcribir_audio(audio_sala.getvalue())
            if texto_transcrito:
                guardar_mensaje_compartido({
                    "user": st.session_state.user_name,
                    "role": "user",
                    "time": datetime.now().strftime("%H:%M"),
                    "text": f"🎙️ *[Audio]:* {texto_transcrito}"
                })
                st.rerun()

    mensajes_sala = cargar_mensajes_compartidos()

    for msg in mensajes_sala:
        es_ia = msg.get("user") == "KingKong IA"
        es_propio = msg.get("user") == st.session_state.user_name
        avatar = "🦍" if es_ia else ("👤" if es_propio else "💬")
        
        with st.chat_message("assistant" if es_ia else "user", avatar=avatar):
            color_autor = st.session_state.theme_color if es_ia else ("#00FF66" if es_propio else "#58a6ff")
            nombre_mostrar = "Tú" if es_propio else msg['user']
            st.markdown(f"<span style='color: {color_autor}; font-weight: bold;'>{nombre_mostrar}</span> <small style='opacity:0.6;'>({msg['time']})</small>", unsafe_allow_html=True)
            if msg.get("text"):
                st.markdown(msg["text"])

    if texto_grupo := st.chat_input("Escribe al grupo (usa @ia para consultarle)..."):
        hora_envio = datetime.now().strftime("%H:%M")
        
        guardar_mensaje_compartido({
            "user": st.session_state.user_name,
            "role": "user",
            "time": hora_envio,
            "text": texto_grupo
        })

        debe_responder_ia = ia_en_grupo or ("@ia" in texto_grupo.lower()) or ("@kingkong" in texto_grupo.lower())

        if debe_responder_ia:
            with st.spinner("🦍 KingKong IA respondiendo..."):
                historial_actual = cargar_mensajes_compartidos()
                formato_ia = [{"role": m.get("role", "user"), "content": m.get("text", "")} for m in historial_actual]
                resp_ia = llamar_a_groq(formato_ia)
                guardar_mensaje_compartido({
                    "user": "KingKong IA",
                    "role": "assistant",
                    "time": datetime.now().strftime("%H:%M"),
                    "text": resp_ia
                })

        st.rerun()

# =================================================
# PESTAÑA 3: 📁 ARCHIVOS CON VISOR DE CÓDIGO
# =================================================

elif menu == "📁 Archivos":
    st.markdown(f"<h2 style='color: {st.session_state.theme_color};'>📁 Gestor y Visor de Archivos</h2>", unsafe_allow_html=True)

    st.subheader("⬆ Subir Archivo al Servidor")
    archivo_nuevo = st.file_uploader("Elige código (.py, .mq5, .pine), documento o imagen", type=None)
    if archivo_nuevo is not None:
        ruta_destino = UPLOADS_DIR / archivo_nuevo.name
        with open(ruta_destino, "wb") as f:
            f.write(archivo_nuevo.getbuffer())
        st.success(f"✅ ¡'{archivo_nuevo.name}' subido con éxito!")
        st.rerun()

    st.markdown("---")

    st.subheader("⬇️ Archivos y Scripts Disponibles")
    archivos_servidor = sorted(list(UPLOADS_DIR.glob("*")), key=lambda x: x.stat().st_mtime, reverse=True)

    if archivos_servidor:
        for arc in archivos_servidor:
            col_info, col_view, col_down, col_del = st.columns([3, 1, 1, 0.7])
            peso_kb = round(arc.stat().st_size / 1024, 1)
            extension = arc.suffix.lower()
            
            with col_info:
                st.markdown(f"📄 **{arc.name}**  \n<small style='color: #8da0b0;'>Tamaño: {peso_kb} KB</small>", unsafe_allow_html=True)
            
            with col_view:
                ver = st.checkbox("👁️ Ver", key=f"v_{arc.name}")

            with col_down:
                try:
                    with open(arc, "rb") as f_down:
                        st.download_button(
                            label="📥 Bajar",
                            data=f_down,
                            file_name=arc.name,
                            key=f"down_{arc.name}",
                            use_container_width=True
                        )
                except Exception:
                    st.caption("Error")

            with col_del:
                if st.button("🗑️", key=f"del_{arc.name}", help=f"Eliminar {arc.name}"):
                    try:
                        arc.unlink()
                        st.success(f"Eliminado: {arc.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo eliminar: {e}")

            # Visor expandible en pantalla
            if ver:
                if extension in [".py", ".mq5", ".pine", ".json", ".txt", ".csv", ".html", ".js", ".css"]:
                    try:
                        with open(arc, "r", encoding="utf-8", errors="ignore") as f_code:
                            contenido = f_code.read()
                        st.code(contenido, language="python" if extension in [".py", ".pine", ".mq5"] else None)
                    except Exception as e:
                        st.error(f"Error al leer: {e}")
                elif extension in [".jpg", ".png", ".jpeg", ".webp"]:
                    st.image(str(arc), width=380)
                else:
                    st.info("Vista previa no soportada para este tipo de archivo binario.")

            st.markdown("<hr style='margin: 8px 0; border: 0.5px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    else:
        st.info("No hay archivos subidos todavía. Puedes subir tus scripts o documentos arriba.")

    st.markdown("---")
    st.subheader("🖼️ Actualizar Foto de Fondo")
    nuevo_fondo = st.file_uploader("Subir imagen de fondo", type=["jpg", "jpeg", "png"], key="fondo_key")
    if nuevo_fondo:
        dest_fondo = BASE_DIR / "mono.jpg"
        with open(dest_fondo, "wb") as f:
            f.write(nuevo_fondo.getbuffer())
        st.success("✅ ¡Fondo actualizado!")
        st.rerun()

# =================================================
# PESTAÑA 4: ⚙️ AJUSTES
# =================================================

else:
    st.title("⚙️ Ajustes de KingKong")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 Colores")
        st.session_state.theme_color = st.color_picker("Color Neón Principal", st.session_state.theme_color)
        st.session_state.secondary_color = st.color_picker("Color Secundario", st.session_state.secondary_color)
        st.session_state.text_color = st.color_picker("Color de Texto General", st.session_state.text_color)

    with col2:
        st.subheader("👤 Tu Perfil")
        nuevo_alias = st.text_input("Cambiar tu alias:", value=st.session_state.user_name)
        if st.button("Guardar nuevo alias"):
            st.session_state.user_name = nuevo_alias.strip()
            st.success(f"Alias actualizado a: {nuevo_alias}")
            st.rerun()

        st.session_state.font_size = st.slider("Tamaño de Fuente (px)", 12, 26, st.session_state.font_size)
        st.session_state.radius = st.slider("Curvatura de Bordes (px)", 0, 35, st.session_state.radius)

    st.markdown("---")
    col_save, col_clear = st.columns(2)

    with col_save:
        if st.button("💾 Guardar Ajustes Permanentes", use_container_width=True):
            settings_to_save = {
                "theme_color": st.session_state.theme_color,
                "secondary_color": st.session_state.secondary_color,
                "input_color": "#0d1a10",
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
                st.success("✅ Ajustes guardados.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    with col_clear:
        if st.button("🗑️ Vaciar Historial Compartido", use_container_width=True):
            if SHARED_CHAT_FILE.exists():
                SHARED_CHAT_FILE.unlink()
            st.session_state.messages = []
            st.success("Historiales vaciados por completo.")
            st.rerun()
