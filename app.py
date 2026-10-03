import streamlit as st
import datetime
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="KingKong Chat",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IDENTIFICADOR AUTOMÁTICO DE USUARIO ---
if "user_id" not in st.query_params:
    st.query_params["user_id"] = f"Usuario_{str(uuid.uuid4())[:4]}"

mi_usuario = st.query_params.get("user_id", "Usuario_1")

# --- ESTILOS CSS: FONDO SELVA NEGRO + TEXTOS 100% BLANCOS + NEÓN VERDE ---
st.markdown("""
    <style>
    /* Fondo general oscuro estilo Jungle Console */
    .stApp {
        background-color: #060d09 !important;
        color: #ffffff !important;
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #08140c !important;
        border-right: 1px solid rgba(0, 255, 102, 0.2) !important;
    }

    /* TODOS los textos del menú lateral en BLANCO NÍTIDO */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label div {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1.02rem !important;
    }

    /* BURBUJAS DE MENSAJES: TEXTO SIEMPRE BLANCO Y LEGIBLE */
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

    /* CAJA DE TEXTO PARA ESCRIBIR: FONDO OSCURO Y TEXTO BLANCO */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: #0d1a10 !important;
        border: 1.5px solid #00FF66 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6d8b76 !important;
    }

    /* TU MONO ORIGINAL 3D CON AURA NEÓN VERDE */
    .gorila-original-aura {
        font-size: 5rem;
        display: inline-block;
        filter: drop-shadow(0 0 22px #00FF66) drop-shadow(0 0 45px rgba(0, 255, 102, 0.6));
        margin-bottom: 2px;
    }

    /* TÍTULO VERDE NEÓN KINGKONG CHAT */
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
        margin-bottom: 25px !important;
    }

    /* PANEL SISTEMA CONECTADO Y RELOJ */
    .panel-consola-jungle {
        background: #0d1b11;
        border: 1px solid rgba(0, 255, 102, 0.3);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-top: 15px;
    }

    /* BOTÓN DESCARGA APK */
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

# --- INICIALIZAR HISTORIAL DE MENSAJES ---
if "mensajes_sala" not in st.session_state:
    st.session_state.mensajes_sala = [
        {
            "remitente": "IA KingKong",
            "texto": "¡Hola! Conexión establecida. Estoy a tu disposición en la jungla.",
            "hora": datetime.datetime.now().strftime("%H:%M")
        }
    ]

# --- BARRA LATERAL (SIDEBAR ORIGINAL RESTAURADO) ---
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

    # Consola en vivo
    hora_sistema = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
        <div class="panel-consola-jungle">
            <div style="color: #00FF66; font-weight: 700; font-size: 0.85rem;">⚡ SISTEMA CONECTADO</div>
            <div style="font-size: 0.72rem; color: #8da0b0; margin-top: 4px;">SESIÓN: <b style="color: #fff;">{mi_usuario}</b></div>
            <div style="font-size: 0.75rem; color: #8da0b0; margin-top: 6px;">TIEMPO EN VIVO</div>
            <div style="color: #00FF66; font-family: monospace; font-size: 1.3rem; font-weight: 800;">{hora_sistema}</div>
        </div>
    """, unsafe_allow_html=True)

    # Botón Descargar APK
    try:
        with open("KingkongChat.apk", "rb") as apk_file:
            st.download_button(
                label="📲 Descargar App Android (APK)",
                data=apk_file,
                file_name="KingkongChat.apk",
                mime="application/vnd.android.package-archive"
            )
    except FileNotFoundError:
        st.caption("ℹ️ Coloca 'KingkongChat.apk' en tu repo para descarga directa.")

# --- VISTAS SEGÚN EL MENÚ LATERAL ---

# 1. PESTAÑA PRINCIPAL: CHAT
if menu in ["💬 KingKong Chat", "👥 Sala de Conversación"]:
    # Tu mono 3D original con aura verde neón y el título
    st.markdown("""
        <div style="text-align: center; margin-top: 5px;">
            <div class="gorila-original-aura">🦍</div>
            <div class="titulo-neon">KINGKONG CHAT</div>
            <div class="subtitulo-jungle">JUNGLE CONSOLE EDITION</div>
        </div>
    """, unsafe_allow_html=True)

    # Mostrar mensajes con textos blancos
    for msg in st.session_state.mensajes_sala:
        if msg["remitente"] == "IA KingKong":
            with st.chat_message("assistant", avatar="🦍"):
                st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>🦍 KingKong IA</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)
        elif msg["remitente"] == mi_usuario:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>Tú</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message("other", avatar="🐵"):
                st.markdown(f"<span style='color: #e3b341; font-weight: bold;'>{msg['remitente']}</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #ffffff !important;'>{msg['texto']}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Interruptor con el mono para activar o silenciar la IA
    col_ia, col_info = st.columns([1, 2])
    with col_ia:
        ia_activa = st.toggle("🦍 Modo IA Activa", value=True)
    with col_info:
        if ia_activa:
            st.caption("🟢 **IA CONECTADA:** Responde al instante a tus mensajes.")
        else:
            st.caption("⚪ **IA EN PAUSA:** Modo charla libre sin respuestas automáticas.")

    # Caja de texto
    if prompt := st.chat_input("Escribe tu mensaje..."):
        hora_actual = datetime.datetime.now().strftime("%H:%M")
        
        # Guardar mensaje del usuario
        st.session_state.mensajes_sala.append({
            "remitente": mi_usuario,
            "texto": prompt,
            "hora": hora_actual
        })
        
        # Respuesta de la IA si el interruptor está activado
        if ia_activa:
            texto_min = prompt.lower().strip()
            if "hola" in texto_min:
                respuesta = "¡Hola! Estoy activa y lista en la consola de KingKong Chat. ¿Qué necesitas consultar?"
            elif "que tal" in texto_min or "cómo estás" in texto_min:
                respuesta = "¡Todo perfecto por aquí! Sistema al 100% y listo para la acción."
            else:
                respuesta = f"🦍 [KingKong IA]: He recibido tu mensaje: '{prompt}'. ¿En qué más te puedo ayudar?"

            st.session_state.mensajes_sala.append({
                "remitente": "IA KingKong",
                "texto": respuesta,
                "hora": hora_actual
            })
            
        st.rerun()

# 2. PESTAÑA: ARCHIVOS
elif menu == "📁 Archivos":
    st.markdown("<h2 style='color: #00FF66;'>📁 Gestor de Archivos</h2>", unsafe_allow_html=True)
    st.markdown("Comparte o almacena archivos en la sesión de la consola:")
    archivo = st.file_uploader("Subir documento o imagen", type=["png", "jpg", "pdf", "txt", "csv"])
    if archivo:
        st.success(f"Archivo subido: {archivo.name}")
        st.info(f"Tamaño: {round(archivo.size / 1024, 2)} KB")

# 3. PESTAÑA: AJUSTES (CONFIGURACIÓN Y RULETITA)
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
    if st.button("Limpiar conversación"):
        st.session_state.mensajes_sala = []
        st.success("Historial borrado.")
        st.rerun()
