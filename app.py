import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# Carpetas
Path("uploads").mkdir(exist_ok=True)
Path("chats").mkdir(exist_ok=True)

st.set_page_config(
    page_title="KINGKONG CHAT",
    page_icon="🦍",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar estilo Telegram

with st.sidebar:

    st.title("🦍 KINGKONG CHAT")

    st.markdown("---")

    chat_name = st.radio(
        "Chats",
        [
            "💻 Programación",
            "📈 Bolsa",
            "📁 Documentos",
            "🧠 Personal"
        ],
        label_visibility="collapsed"
    )

st.title(chat_name)

# Archivos

uploaded_file = st.file_uploader(
    "Subir archivo",
    type=None
)

if uploaded_file:

    save_path = Path("uploads") / uploaded_file.name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(
        f"Archivo guardado: {uploaded_file.name}"
    )

# Historial

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat

prompt = st.chat_input(
    "Escribe un mensaje..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        response = model.generate_content(prompt)

        reply = response.text

        st.markdown(reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )
