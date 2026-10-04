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
        st.error(f"Error al sincronizar mensaje: {e}")

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
# ESTILOS CSS CON FONDO VISIBLE Y MICRÓFONO INTEGRADO
# =================================================

bg_css = get_background_css()

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {{
        background-image: 
            linear-gradient(rgba(4, 10, 6, 0.40), rgba(6, 13, 9, 0.55)),
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
        border-radius: 24px !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.35) !important;
        padding-right: 48px !important;
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
# LLAMADAS GROQ CON AUTO-DETECCIÓN DINÁMICA
# =================================================

def obtener_modelo_activo(para_vision=False):
    """Consulta en directo a la API de Groq para seleccionar un modelo disponible."""
    try:
        modelos_disponibles = [m.id for m in client.models.list().data]
        if para_vision:
            preferencias_vision = [
                "qwen/qwen3.8-27b",
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview"
            ]
            for p in preferencias_vision:
                if p in modelos_disponibles:
                    return p

        preferencias = [
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "qwen/qwen3-32b",
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ]
        for p in preferencias:
            if p in modelos_disponibles:
                return p
        for m in modelos_disponibles:
            if not any(bad in m for bad in ["whisper", "guard", "safeguard", "orpheus"]):
                return m
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

def llamar_a_groq(historial_mensajes, imagen_b64=None):
    modelo_elegido = obtener_modelo_activo(para_vision=bool(imagen_b64))
    historial = [
        {
            "role": "system",
            "content": (
                "Eres KingKong IA, un asistente avanzado, conciso y de alto rendimiento. "
                "Eres analítico, profesional y experto en trading, mercados financieros, tecnología y visión artificial. "
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

    # Si se adjunta imagen a la consulta
    if imagen_b64:
        ultimo_usr = historial[-1]["content"] if historial and historial[-1]["role"] == "user" else "Describe esta imagen"
        historial[-1] = {
            "role": "user",
            "content": [
                {"type": "text", "text": ultimo_usr},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_b64}"}}
            ]
        }

    try:
        stream = client.chat.completions.create(
            model=modelo_elegido,
            messages=historial,
            stream=True
        )
        def stream_text():
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        return st.write_stream(stream_text())
    except Exception as e:
        err_msg = f"⚠️ Error en Groq ({modelo_elegido}): {e}"
        st.error(err_msg)
        return err_msg

# =================================================
# INYECTOR DEL BOTÓN DE MICRÓFONO DENTRO DEL INPUT
# =================================================

def render_mic_telegram():
    components.html(
        f"""
        <style>
            #tg-mic {{
                position: fixed;
                bottom: 18px;
                right: 56px;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: {st.session_state.theme_color};
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 17px;
                box-shadow: 0 0 10px rgba(0, 255, 102, 0.45);
                z-index: 9999999;
                transition: transform 0.15s ease, background 0.2s ease;
            }}
            #tg-mic:active {{
                transform: scale(0.9);
            }}
            #tg-mic.recording {{
                background: #ff3333 !important;
                box-shadow: 0 0 16px rgba(255, 50, 50, 0.8) !important;
                animation: tg_pulse 1s infinite;
            }}
            @keyframes tg_pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.12); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
        <button id="tg-mic" title="Hablar por voz">🎙️</button>
        <script>
            const micBtn = document.getElementById('tg-mic');
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRec) {{
                const rec = new SpeechRec();
                rec.lang = 'es-ES';
                rec.continuous = false;
                rec.interimResults = false;
                let active = false;

                micBtn.addEventListener('click', () => {{
                    if (!active) {{
                        rec.start();
                    }} else {{
                        rec.stop();
                    }}
                }});

                rec.onstart = () => {{
                    active = true;
                    micBtn.classList.add('recording');
                }};
                rec.onend = () => {{
                    active = false;
                    micBtn.classList.remove('recording');
                }};
                rec.onresult = (e) => {{
                    const phrase = e.results[0][0].transcript;
                    const doc = window.parent.document;
                    const area = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    if (area) {{
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                        setter.call(area, phrase);
                        area.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        area.focus();
                    }}
                }};
            }} else {{
                micBtn.style.display = 'none';
            }}
        </script>
        """,
        height=0
    )

# =================================================
# PESTAÑA 1: 💬 KINGKONG CHAT
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
            if msg.get("image"):
                st.image(f"data:image/jpeg;base64,{msg['image']}", width=320)
            if msg.get("content"):
                st.markdown(msg["content"])

    # Adjuntar Foto o GIF a KingKong
    with st.expander("📎 Adjuntar Foto o GIF para KingKong", expanded=False):
        foto_subida = st.file_uploader("Sube una imagen o captura", type=["jpg", "jpeg", "png", "gif", "webp"], key="foto_ia")

    # Inyección del botón de micrófono en la barra
    render_mic_telegram()

    if prompt := st.chat_input("Escribe a KingKong (o pulsa 🎙️ para dictar)..."):
        img_b64 = None
        if foto_subida:
            img_b64 = base64.b64encode(foto_subida.read()).decode()

        st.session_state.messages.append({"role": "user", "content": prompt, "image": img_b64})
        with st.chat_message("user", avatar="👤"):
            if img_b64:
                st.image(f"data:image/jpeg;base64,{img_b64}", width=320)
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦍"):
            full_response = llamar_a_groq(st.session_state.messages, imagen_b64=img_b64)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# =================================================
# PESTAÑA 2: 👥 SALA DE GRUPO
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

    col_t1, col_t2 = st.columns([3, 1])
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
        if st.button("🔄 Actualizar"):
            st.rerun()

    col_tgl, col_info = st.columns([1, 2])
    with col_tgl:
        ia_en_grupo = st.toggle("🦍 Modo IA Fijo", value=False)
    with col_info:
        if ia_en_grupo:
            st.caption("🟢 **IA PERMANENTE:** Responde a todos los mensajes.")
        else:
            st.caption("💡 Menciona **@ia** o **@kingkong** para llamarla solo cuando quieras.")

    mensajes_sala = cargar_mensajes_compartidos()

    for msg in mensajes_sala:
        es_ia = msg.get("user") == "KingKong IA"
        es_propio = msg.get("user") == st.session_state.user_name
        avatar = "🦍" if es_ia else ("👤" if es_propio else "💬")
        
        with st.chat_message("assistant" if es_ia else "user", avatar=avatar):
            color_autor = st.session_state.theme_color if es_ia else ("#00FF66" if es_propio else "#58a6ff")
            nombre_mostrar = "Tú" if es_propio else msg['user']
            st.markdown(f"<span style='color: {color_autor}; font-weight: bold;'>{nombre_mostrar}</span> <small style='opacity:0.6;'>({msg['time']})</small>", unsafe_allow_html=True)
            if msg.get("image"):
                st.image(f"data:image/jpeg;base64,{msg['image']}", width=280)
            if msg.get("text"):
                st.markdown(msg["text"])

    # Adjuntar Foto o GIF a la Sala
    with st.expander("📷 Enviar Foto o GIF a la Sala", expanded=False):
        foto_sala = st.file_uploader("Elige una foto o GIF para el grupo", type=["jpg", "jpeg", "png", "gif", "webp"], key="foto_sala_up")
        if foto_sala is not None and st.button("📤 Enviar Imagen"):
            img_b64 = base64.b64encode(foto_sala.read()).decode()
            guardar_mensaje_compartido({
                "user": st.session_state.user_name,
                "role": "user",
                "time": datetime.now().strftime("%H:%M"),
                "text": "📷 *[Imagen compartida]*",
                "image": img_b64
            })
            st.rerun()

    # Inyección del botón de micrófono en la barra
    render_mic_telegram()

    if texto_grupo := st.chat_input("Escribe al grupo (usa @ia o pulsa 🎙️)..."):
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

    st.subheader("⬇ Archivos y Scripts Disponibles")
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

            if ver:
                if extension in [".py", ".mq5", ".pine", ".json", ".txt", ".csv", ".html", ".js", ".css"]:
                    try:
                        with open(arc, "r", encoding="utf-8", errors="ignore") as f_code:
                            contenido = f_code.read()
                        st.code(contenido, language="python" if extension in [".py", ".pine", ".mq5"] else None)
                    except Exception as e:
                        st.error(f"Error al leer: {e}")
                elif extension in [".jpg", ".png", ".jpeg", ".webp", ".gif"]:
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
