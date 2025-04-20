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
            overflow-x: hidden;
        }
        
        .stSpinner {
            display: none !important;
        }
        
        .title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            margin-top: 30px;
        }
        
        .st-emotion-cache-16tyu1 img{
            max-width: none;    
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
        
        @media screen and (max-width: 400px) {
            .stApp {
                padding-left: 10px;
                padding-right: 10px;
            }

            .chat-bubble {
                padding: 10px 14px;
            }

            .user-msg, .bot-msg {
                max-width: 100% !important;
                font-size: 9px;
            }
            .chatting{
                font-size: 9px;

            }
            .st-emotion-cache-16tyu1 img {
                width: 100% !important;
                height: auto !important;
                left: 0% !important;
            }

            h1.title, h1 {
                font-size: 24px !important;
                text-align: center;
            }

            input[type="text"], textarea, .stTextInput>div>div>input {
                font-size: 14px !important;
                padding: 8px !important;
            }

            button {
                width: 100% !important;
                padding: 10px !important;
                font-size: 14px !important;
            }
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
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: 120%; height: auto; left: 23%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.4;'>
            <div style='position: relative; z-index: 2; padding: 20px;'>
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
    chat_html += "<div class='chatting' style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:600px; margin-bottom:20px;'>"
    for speaker, message in st.session_state.chat_history:
        if speaker == "Vous":
            chat_html += f"<div style='background:#3B82F6; color:white; padding:10px 16px; border-radius:12px; text-align:right; margin-left:auto; margin-bottom:10px; max-width:90%;'>👤 <b>{speaker}</b><br>{message}</div>"
        else:
            chat_html += f"<div style='background:#FBBF24; color:black; padding:10px 16px; border-radius:12px; text-align:left; margin-right:auto; margin-bottom:10px; max-width:90%;'>🤖 <b>{speaker}</b><br>{message}</div>"
    chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# Zone de texte
user_input = st.text_input("", placeholder="Tape ta question...")

if st.button("Envoyer") and user_input.strip():
    st.session_state.chat_history.append(("Vous", user_input))
    response = answer_question(user_input)
    st.session_state.chat_history.append(("Bot", response))
    st.rerun()
