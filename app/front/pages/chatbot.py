# pages/1_Chatbot_orientation.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import streamlit as st
from backend.models.rag.query_rag import answer_question
from PIL import Image
import base64

st.set_page_config(page_title="Chatbot d'orientation", page_icon="🤖")

# CSS personnalisé pour ressembler à l'illustration
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            margin-top: 30px;
        }
        .subtitle {
            font-size: 18px;
            color: #3B82F6;
            margin-bottom: 20px;
        }
        .chat-bubble {
            padding: 12px 18px;
            border-radius: 16px;
            margin-bottom: 10px;
            max-width: 85%;
            line-height: 1.5;
            font-size: 16px;
        }
        .user-msg {
            background-color: #3B82F6;
            color: white;
            text-align: right;
            margin-left: auto;
        }
        .bot-msg {
            background-color: #FBBF24;
            color: black;
            text-align: left;
            margin-right: auto;
        }
        input[type="text"], textarea, .stTextInput>div>div>input {
            background-color: #E0F2FE !important;
            color: #111827 !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        button {
            background-color: #3B82F6 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 24px !important;
            font-size: 16px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Image de fond et titre par-dessus
illu_path = os.path.abspath("assets/chatbot_illu.png")
if os.path.exists(illu_path):
    with open(illu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style='position: relative; width: 100%; height: 280px;'>
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: auto; height: auto; left: 32%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.4;'>
            <div style='position: relative; z-index: 2; padding: 20px;'>
                <img src='assets/logo.png' width='100'>
                <h1 style='color:#1E3A8A;'>Chatbot d'orientation</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Initialisation de la session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Affichage de l'historique
st.markdown('', unsafe_allow_html=True)

chat_html = ""
if st.session_state.chat_history:
    chat_html += "<div style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:600px; margin-bottom:20px;'>"
    for speaker, message in st.session_state.chat_history:
        if speaker == "Vous":
            chat_html += f"<div style='background:#3B82F6; color:white; padding:10px 16px; border-radius:12px; text-align:right; margin-left:auto; margin-bottom:10px; max-width:90%;'>👤 <b>{speaker}</b><br>{message}</div>"
        else:
            chat_html += f"<div style='background:#FBBF24; color:black; padding:10px 16px; border-radius:12px; text-align:left; margin-right:auto; margin-bottom:10px; max-width:90%;'>🤖 <b>{speaker}</b><br>{message}</div>"
    chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# Zone de texte
st.markdown('<div class="subtitle">Pose ta question</div>', unsafe_allow_html=True)
user_input = st.text_input("", placeholder="Tape ta question...")

if st.button("Envoyer") and user_input.strip():
    st.session_state.chat_history.append(("Vous", user_input))
    response = answer_question(user_input)
    st.session_state.chat_history.append(("Bot", response))
    st.rerun()
