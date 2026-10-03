import streamlit as st
import datetime
import uuid
import requests
import json

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="KingKong Chat",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. IDENTIFICADOR DE USUARIO PERSISTENTE ---
if "user_id" not in st.query_params:
    st.query_params["user_id"] = f"Usuario_{str(uuid.uuid4())[:4]}"

mi_usuario = st.query_params.get("user_id", "Usuario_1")

# --- 3. CONEXIÓN DIRECTA CON GROK VÍA HTTP (Sin librerías externas) ---
api_key_grok = (
    st.secrets.get("GROK_API_KEY") 
    or st.secrets.get("XAI_API_KEY") 
    or st.secrets.get("grok_api_key") 
    or ""
)

def consultar_grok(historial):
    if not api_key_grok:
        return "⚠️ Clave de Grok no configurada en st.secrets['GROK_API_KEY']."
    
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key_grok}"
    }
    
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres KingKong IA, un asistente analítico avanzado en la consola Jungle Console Edition. "
                "Eres experto en trading, mercados financieros, tecnología y programación. "
                "Responde con análisis detallados, precisos y en español a las consultas del usuario."
            )
        }
    ]
    for m in historial:
        rol = "assistant" if m["remitente"] == "IA KingKong" else "user"
        mensajes.append({"role": rol, "content": m["texto"]})
        
    payload = {
        "model": "grok-beta",
        "messages": mensajes,
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"❌ Error de Grok ({res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"

# --- 4. ESTILOS VISUALES: OSCURO SELVA + NEÓN + TEXTOS EN BLANCO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #060d09 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #08140c !important;
        border-right: 1px solid rgba(0, 255, 102, 0.2) !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label div {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1.02rem !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #101e14 !important;
        border: 1px solid rgba(0, 255, 102, 0.25) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #ffffff !important;
        font-size: 1rem !important;
    }

    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: #060d09 !important;
        border-top: 1px solid rgba(0, 255, 102, 0.15) !important;
    }
    [data-testid="stChatInput"] {
        background-color: #0d1a10 !important;
        border: 1.5px solid #00FF66 !important;
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    .gorila-original-aura {
        font-size: 4.8rem;
        display: inline-block;
        filter: drop-shadow(0 0 22px #00FF66) drop-shadow(0 0 45px rgba(0, 255, 102, 0.6));
        margin-bottom: 2px;
    }

    .titulo-neon {
        color: #00FF66 !important;
        font-weight: 900 !important;
        letter-spacing: 3px !important;
        font-size: 2.1rem !important;
        margin-top: 5px !important;
        margin-bottom: 2px !important;
        text-shadow: 0 0 15px rgba(0, 255, 102, 0.85);
        font-family: 'Segoe UI', system-ui, sans-serif;
    }

    .subtitulo-console {
        color: #8da0b0 !important;
        letter-spacing: 3px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        margin-bottom: 22px !important;
    }

    .panel-consola-jungle {
        background: #0d1b11;
        border: 1px solid rgba(0, 255, 102, 0.3);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-top: 15px;
    }

    div.stDownloadButton > button {
        background: linear-gradient(135deg, #00FF66 0%, #059669 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-top: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. INICIALIZACIÓN DE HISTORIALES SEPARADOS ---
if "mensajes_ia_solo" not in st.session_state:
    st.session_state.mensajes_ia_solo = [
        {
            "remitente": "IA KingKong",
            "texto": "¡Saludos! Soy KingKong IA con motor Grok activo. Pídeme análisis detallados del mercado o lo que necesites.",
            "hora": datetime.datetime.now().strftime("%H:%M")
        }
    ]

if "mensajes_sala_grupo" not in st.session_state:
    st.session_state.mensajes_sala_grupo = [
        {
            "remitente": "IA KingKong",
            "texto": "Sala de grupo activa. Activa el interruptor inferior cuando quieras que Grok participe en vuestra conversación.",
            "hora": datetime.datetime.now().strftime("%H:%M")
        }
    ]

# --- 6. BARRA LATERAL ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding-top: 5px;">
            <div style="font-size: 3.2rem; filter: drop-shadow(0 0 15px #00FF66);">🦍</div>
            <h3 style="color: #00FF66; margin: 4px 0 0 0; letter-spacing: 2px;">KINGKONG CHAT</h3>
            <p style="color: #8da0b0; font-size: 0.72rem;">JUNGLE CONSOLE EDITION</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    menu = st.radio(
        "Navegación",
        ["💬 KingKong Chat", "👥 Sala de Conversación", "📁 Archivos", "⚙️ Ajustes"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    hora_sistema = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
        <div class="panel-consola-jungle">
            <div style="color: #00FF66; font-weight: 700; font-size: 0.85rem;">⚡ SISTEMA CONECTADO</div>
            <div style="font-size: 0.72rem; color: #8da0b0; margin-top: 4px;">SESIÓN: <b style="color: #fff;">{mi_usuario}</b></div>
            <div style="font-size: 0.75rem; color: #8da0b0; margin-top: 6px;">TIEMPO EN VIVO</div>
            <div style="color: #00FF66; font-family: monospace; font-size: 1.3rem; font-weight: 800;">{hora_sistema}</div>
        </div>
    """, unsafe_allow_html=True)

    try:
        with open("KingkongChat.apk", "rb") as apk_file:
            st.download_button(
                label="📲 Descargar App Android (APK)",
                data=apk_file,
                file_name="KingkongChat.apk",
                mime="application/vnd.android.package-archive"
            )
    except FileNotFoundError:
        st.caption("ℹ️ Coloca 'KingkongChat.apk' en tu repo para descarga.")

# --- 7. VISTAS SEGÚN EL MENÚ ---

# ========================================================
# PESTAÑA 1: 💬 KINGKONG CHAT (IA PURA CON GROK)
# ========================================================
if menu == "💬 KingKong Chat":
    st.markdown("""
        <div style="text-align: center; margin-top: 5px;">
            <div class="gorila-original-aura">🦍</div>
            <div class="titulo-neon">KINGKONG CHAT</div>
            <div class="subtitulo-console">MODO GROK DIRECTO · ANÁLISIS TOTAL</div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.mensajes_ia_solo:
        if msg["remitente"] == "IA KingKong":
            with st.chat_message("assistant", avatar="🦍"):
                st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>🦍 KingKong IA</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>Tú</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Pide un análisis detallado a Grok..."):
        hora_envio = datetime.datetime.now().strftime("%H:%M")
        
        st.session_state.mensajes_ia_solo.append({
            "remitente": mi_usuario,
            "texto": prompt,
            "hora": hora_envio
        })
        
        with st.spinner("🦍 Grok analizando en tiempo real..."):
            respuesta_grok = consultar_grok(st.session_state.mensajes_ia_solo)

        st.session_state.mensajes_ia_solo.append({
            "remitente": "IA KingKong",
            "texto": respuesta_grok,
            "hora": hora_envio
        })
        st.rerun()

# ========================================================
# PESTAÑA 2: 👥 SALA DE GRUPO (COMPAÑEROS + TOGGLE GROK)
# ========================================================
elif menu == "👥 Sala de Conversación":
    st.markdown("""
        <div style="text-align: center; margin-top: 5px;">
            <div class="gorila-original-aura">👥</div>
            <div class="titulo-neon">SALA DE GRUPO</div>
            <div class="subtitulo-console">CHAT CON AMIGOS · PARTICIPACIÓN DE GROK OPCIONAL</div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.mensajes_sala_grupo:
        if msg["remitente"] == "IA KingKong":
            with st.chat_message("assistant", avatar="🦍"):
                st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>🦍 KingKong IA</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)
        elif msg["remitente"] == mi_usuario:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"<span style='color: #58a6ff; font-weight: bold;'>Tú</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message("other", avatar="🐵"):
                st.markdown(f"<span style='color: #e3b341; font-weight: bold;'>{msg['remitente']}</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_sw, col_desc = st.columns([1, 2])
    with col_sw:
        ia_activa_grupo = st.toggle("🦍 Modo IA en Grupo", value=False)
    with col_desc:
        if ia_activa_grupo:
            st.caption("🟢 **GROK CONECTADO:** Intervendrá en las dudas del grupo.")
        else:
            st.caption("⚪ **GROK EN REPOSO:** Charla privada.")

    if prompt_grupo := st.chat_input("Escribe a tus compañeros..."):
        hora_envio = datetime.datetime.now().strftime("%H:%M")
        
        st.session_state.mensajes_sala_grupo.append({
            "remitente": mi_usuario,
            "texto": prompt_grupo,
            "hora": hora_envio
        })
        
        if ia_activa_grupo:
            with st.spinner("🦍 Grok respondiendo en el grupo..."):
                resp_grok_grupo = consultar_grok(st.session_state.mensajes_sala_grupo)
            
            st.session_state.mensajes_sala_grupo.append({
                "remitente": "IA KingKong",
                "texto": resp_grok_grupo,
                "hora": hora_envio
            })
            
        st.rerun()

# ========================================================
# PESTAÑA 3: 📁 ARCHIVOS
# ========================================================
elif menu == "📁 Archivos":
    st.markdown("<h2 style='color: #00FF66;'>📁 Gestor de Archivos</h2>", unsafe_allow_html=True)
    st.markdown("Comparte o almacena documentos e imágenes en la consola:")
    archivo = st.file_uploader("Subir documento o imagen", type=["png", "jpg", "pdf", "txt", "csv"])
    if archivo:
        st.success(f"Archivo subido: {archivo.name}")
        st.info(f"Tamaño: {round(archivo.size / 1024, 2)} KB")

# ========================================================
# PESTAÑA 4: ⚙️ AJUSTES
# ========================================================
elif menu == "⚙️ Ajustes":
    st.markdown("<h2 style='color: #00FF66;'>⚙️ Ajustes y Configuración</h2>", unsafe_allow_html=True)
    
    st.subheader("🎨 Apariencia")
    st.color_picker("Color Neón principal", "#00FF66")
    st.checkbox("Modo Jungle Dark profundo", value=True)
    
    st.subheader("👤 Tu Perfil")
    nuevo_nombre = st.text_input("Cambiar tu identificador:", value=mi_usuario)
    if st.button("Guardar Nombre"):
        st.query_params["user_id"] = nuevo_nombre
        st.success(f"Guardado como: {nuevo_nombre}")
        st.rerun()

    st.subheader("🧹 Mensajes")
    if st.button("Limpiar historiales de chat"):
        st.session_state.mensajes_ia_solo = []
        st.session_state.mensajes_sala_grupo = []
        st.success("Historiales reiniciados.")
        st.rerun()
