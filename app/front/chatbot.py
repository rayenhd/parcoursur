# pages/1_Chatbot_orientation.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from backend.models.rag.query_rag import answer_question  # suppose que tu as déjà un fichier rag_query.py contenant la fonction RAG

st.set_page_config(page_title="Chatbot d'orientation", page_icon="🤖")
st.title("💬 Chatbot d'orientation scolaire et professionnelle")

# Initialisation de la session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🟣 Affichage de l'historique
st.subheader("🟣 Historique de la conversation")
for speaker, message in st.session_state.chat_history:
    if speaker == "Vous":
        st.write(f"**👤 {speaker}**: {message}")
    else:
        st.write(f"**🤖 {speaker}**: {message}")

# 🟣 Zone de texte pour continuer la conversation
st.subheader("Pose ta question")

user_input = st.text_input("Ta question :", "")

if st.button("Envoyer") and user_input.strip():
    # Sauvegarder la question
    st.session_state.chat_history.append(("Vous", user_input))

    # Générer la réponse
    response = answer_question(user_input)

    # Sauvegarder la réponse
    st.session_state.chat_history.append(("Bot", response))

    # Rafraîchir la page proprement
    st.rerun()