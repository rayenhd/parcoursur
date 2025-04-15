import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.rag.generate_question import generate_next_question, generate_final_recommendation

st.set_page_config(page_title="🔎 Questionnaire - 10 minutes", page_icon="🕙")

# CSS custom
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
            font-family: 'Segoe UI', sans-serif;
        }
        h1.title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            text-align: center;
            margin-top: 20px;
        }
        .question-box {
            position: absolute;
            top: 40%;
            left: -3%;
            width: 45%;
            height: 60vh;
            background-color: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .chat-bot {
            background-color: #FBBF24;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .chat-user {
            background-color: #3B82F6;
            color: white;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            text-align: right;
        }
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }
        .background img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.2;
        }
        .stTextInput{
            background-color: white !important;
            color: #1E3A8A !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 8px !important;
            padding: 10px !important;
            width: 39% !important;
        }
        .stTextInput input{
            background-color: white !important;
            border: none !important;
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# Background illustration
illu_path = "assets/illu_first.png"
if os.path.exists(illu_path):
    with open(illu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style='position: absolute; width: 100%; height: 280px;'>
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: auto; height: auto; left: 32%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.7;'>
            <div style='position: absolute; z-index: 2; padding: 20px;'>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>🕙 Questionnaire - 10 minutes</h1>", unsafe_allow_html=True)

# === Initialisation session ===
if "q10_history" not in st.session_state:
    st.session_state.q10_history = []
if "q10_current_question" not in st.session_state:
    st.session_state.q10_current_question = "T'es en quelle classe ?"
if "q10_complete" not in st.session_state:
    st.session_state.q10_complete = False
if "q10_reco" not in st.session_state:
    st.session_state.q10_reco = None
if "index_q" not in st.session_state:
    st.session_state.index_q = 0

# === Logique d'affichage ===
index = st.session_state.index_q
st.markdown("<div class='question-box'>", unsafe_allow_html=True)
# Barre de progression
progress_percentage = int((index / 3) * 100)
st.markdown(f"""
    <div style='margin-bottom: 16px;'>
        <div style='width: 38%; background-color: #E5E7EB; height: 10px; border-radius: 8px;'>
            <div style='width: {progress_percentage}%; background-color: #FBBF24; height: 100%; border-radius: 8px;'></div>
        </div>
    </div>
""", unsafe_allow_html=True)
if not st.session_state.q10_complete:
    st.write(f"Question : {st.session_state.q10_current_question}")

    user_answer = st.text_input("Ta réponse :")

    if st.button("Envoyer") and user_answer.strip():
        st.session_state.q10_history.append((st.session_state.q10_current_question, user_answer.strip()))
        print("____________ envoyé _____________")
        print(st.session_state.q10_history)
        st.session_state.index_q+=1

        if len(st.session_state.q10_history) >= 3:
            if "q10_final_reco" not in st.session_state:
                from backend.models.rag.generate_question import generate_final_recommendation
                st.session_state.q10_final_reco = generate_final_recommendation(st.session_state.q10_history)

            st.markdown("### 🔍 Recommandation personnalisée")
            st.write(st.session_state.q10_final_reco)
        else:
            from backend.models.rag.generate_question import generate_next_question
            st.session_state.q10_current_question = generate_next_question(st.session_state.q10_history)
            st.rerun()
else:
    st.success("✅ Merci pour tes réponses ! Voici ce que je te recommande :")

    if st.session_state.q10_reco is None:
        qa_pairs = [f"Q: {q}\nR: {r}" for q, r in st.session_state.q10_history]
        st.session_state.q10_reco = generate_final_recommendation(qa_pairs)

    st.markdown("### 🔍 Recommandation personnalisée")
    st.write(st.session_state.q10_reco)

    st.markdown("---")
    if st.button("🔄 Recommencer"):
        for key in ["q10_history", "q10_current_question", "q10_complete", "q10_reco"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
