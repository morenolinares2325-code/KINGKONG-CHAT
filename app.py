import streamlit as st
import datetime
import uuid

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="KingKong Chat",
    page_icon="🦍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. IDENTIFICADOR DE USUARIO AUTOMÁTICO (Persistente) ---
if "user_id" not in st.query_params:
    nuevo_id = f"Usuario_{str(uuid.uuid4())[:4]}"
    st.query_params["user_id"] = nuevo_id

mi_usuario = st.query_params.get("user_id", "Usuario_1")

# --- 3. ESTILOS VISUALES (TELEGRAM DARK + NEÓN CYBERPUNK) ---
st.markdown("""
    <style>
    /* Fondo principal y barra lateral estilo Telegram Dark */
    .stApp {
        background-color: #0e1621 !important;
        color: #e4ecf2 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #17212b !important;
        border-right: 1px solid rgba(0, 255, 102, 0.15) !important;
    }

    /* Forzar textos de la barra lateral en BLANCO NÍTIDO */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label div {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1.02rem !important;
    }

    /* Efecto hover suave en el menú lateral */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background-color: #242f3d !important;
        border-radius: 8px;
    }

    /* Cabecera Neón de bienvenida */
    .hero-banner {
        text-align: center;
        padding: 20px 10px;
        background: radial-gradient(circle at center, rgba(0, 255, 102, 0.09) 0%, rgba(14, 22, 33, 0) 70%);
        border-radius: 20px;
        margin-bottom: 20px;
    }

    .neon-gorilla-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 86px;
        height: 86px;
        border-radius: 50%;
        background: linear-gradient(145deg, #1f2c38, #111a22);
        border: 2px solid #00FF66;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.5), inset 0 0 10px rgba(0, 255, 102, 0.25);
        margin-bottom: 12px;
    }

    .neon-title {
        color: #00FF66 !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        letter-spacing: 3px !important;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.65), 0 0 25px rgba(0, 255, 102, 0.3);
        margin: 0 !important;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }

    .neon-subtitle {
        color: #ffffff !important;
        background: rgba(36, 47, 61, 0.85);
        border: 1px solid rgba(0, 255, 102, 0.3);
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 2px;
        padding: 4px 14px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
    }

    /* Panel de estado y tiempo en vivo */
    .status-panel {
        background-color: #1a2530;
        border: 1px solid rgba(0, 255, 102, 0.2);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-top: 15px;
    }

    /* Botón de descarga de APK */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #00FF66 0%, #059669 100%) !important;
        color: #0a1118 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        box-shadow: 0 4px 14px rgba(0, 255, 102, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding-top: 10px;">
            <div class="neon-gorilla-circle" style="width: 70px; height: 70px;">
                <svg viewBox="0 0 24 24" width="40" height="40" fill="#00FF66" style="filter: drop-shadow(0 0 6px #00FF66);">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3 0 .78-.3 1.48-.79 2.01.62.33 1.13.82 1.48 1.43.34.61.51 1.32.51 2.06 0 1.93-1.57 3.5-3.5 3.5s-3.5-1.57-3.5-3.5c0-.74.17-1.45.51-2.06.35-.61.86-1.1 1.48-1.43C11.3 9.48 11 8.78 11 8c0-1.66 1.34-3 3-3zm-2.5 10.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm5 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                </svg>
            </div>
            <h3 style="color: #00FF66; margin: 4px 0 0 0; letter-spacing: 2px;">KINGKONG CHAT</h3>
            <p style="color: #8da0b0; font-size: 0.75rem; margin-top: 2px;">CONSOLA TELEGRAM DARK</p>
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

    # Panel de Estado del Sistema y Tiempo en Vivo
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
        <div class="status-panel">
            <div style="color: #00FF66; font-weight: 700; font-size: 0.85rem;">⚡ SISTEMA CONECTADO</div>
            <div style="font-size: 0.72rem; color: #8da0b0; margin-top: 6px;">TU SESIÓN: <b style="color: #fff;">{mi_usuario}</b></div>
            <div style="margin-top: 8px; font-size: 0.75rem; color: #8da0b0;">TIEMPO EN VIVO</div>
            <div style="color: #00FF66; font-family: monospace; font-size: 1.25rem; font-weight: 800;">{hora_actual}</div>
        </div>
    """, unsafe_allow_html=True)

    # Botón de Descarga del APK
    try:
        with open("KingkongChat.apk", "rb") as file_apk:
            st.download_button(
                label="📲 Descargar App Android",
                data=file_apk,
                file_name="KingkongChat.apk",
                mime="application/vnd.android.package-archive"
            )
    except FileNotFoundError:
        st.caption("ℹ️ Coloca 'KingkongChat.apk' en tu repo para activar la descarga.")

# --- 5. CABECERA PRINCIPAL DEL CHAT ---
st.markdown("""
    <div class="hero-banner">
        <div class="neon-gorilla-circle">
            <svg viewBox="0 0 24 24" width="48" height="48" fill="#00FF66" style="filter: drop-shadow(0 0 8px #00FF66);">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3 0 .78-.3 1.48-.79 2.01.62.33 1.13.82 1.48 1.43.34.61.51 1.32.51 2.06 0 1.93-1.57 3.5-3.5 3.5s-3.5-1.57-3.5-3.5c0-.74.17-1.45.51-2.06.35-.61.86-1.1 1.48-1.43C11.3 9.48 11 8.78 11 8c0-1.66 1.34-3 3-3zm-2.5 10.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm5 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
            </svg>
        </div>
        <h1 class="neon-title">KINGKONG CHAT</h1>
        <div class="neon-subtitle">JUNGLE CONSOLE EDITION · TELEGRAM PRO</div>
    </div>
""", unsafe_allow_html=True)

# --- 6. HISTORIAL DE MENSAJES (SALA COMPARTIDA) ---
if "mensajes_sala" not in st.session_state:
    st.session_state.mensajes_sala = [
        {
            "remitente": "IA KingKong",
            "texto": "¡Bienvenido a la sala! Estoy en reposo. Activa el interruptor inferior cuando quieras que participe en vuestra conversación.",
            "hora": datetime.datetime.now().strftime("%H:%M")
        }
    ]

# Dibujar mensajes con formato diferenciado
for msg in st.session_state.mensajes_sala:
    if msg["remitente"] == "IA KingKong":
        with st.chat_message("assistant", avatar="🦍"):
            st.markdown(f"<span style='color: #00FF66; font-weight: bold;'>🦍 KingKong IA</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
            st.write(msg["texto"])
    elif msg["remitente"] == mi_usuario:
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"<span style='color: #58a6ff; font-weight: bold;'>Tú</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
            st.write(msg["texto"])
    else:
        with st.chat_message("other", avatar="🐵"):
            st.markdown(f"<span style='color: #e3b341; font-weight: bold;'>{msg['remitente']}</span> · <small style='color: #8da0b0;'>{msg['hora']}</small>", unsafe_allow_html=True)
            st.write(msg["texto"])

# --- 7. BARRA INFERIOR: INTERRUPTOR IA + ENTRADA DE TEXTO ---
col_ia, col_info = st.columns([1, 2])
with col_ia:
    # Interruptor con el gorila para activar/desactivar la IA a voluntad
    ia_activa = st.toggle("🦍 Modo IA Participante", value=False)

if not ia_activa:
    with col_info:
        st.caption("🔒 *La IA está en silencio. Charla privada entre compañeros.*")
else:
    with col_info:
        st.caption("⚡ *La IA está atenta y responderá a cada mensaje del grupo.*")

# Envío del mensaje
if prompt := st.chat_input("Escribe un mensaje para la sala..."):
    hora_envio = datetime.datetime.now().strftime("%H:%M")
    
    # 1. Guardar mensaje del usuario emisor
    st.session_state.mensajes_sala.append({
        "remitente": mi_usuario,
        "texto": prompt,
        "hora": hora_envio
    })
    
    # 2. Si el interruptor de la IA está activado, responde en la misma conversación
    if ia_activa:
        # Aquí puedes conectar la llamada a tu API de IA favorita
        respuesta_ia = f"🦍 [KingKong IA]: He recibido tu mensaje, @{mi_usuario}. Estoy lista para ayudaros con lo que necesitéis."
        st.session_state.mensajes_sala.append({
            "remitente": "IA KingKong",
            "texto": respuesta_ia,
            "hora": hora_envio
        })
    
    st.rerun()
