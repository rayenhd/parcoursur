import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.rag.query_rag import answer_question

st.set_page_config(page_title="🧠 Questionnaire Express", page_icon="⏱️")

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
        .question-container {
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
        .question-button {
            background-color: #E0F2FE;
            color: #111827;
            padding: 12px;
            border-radius: 12px;
            margin: 10px 0;
            font-size: 16px;
            width: 100%;
            border: none;
            text-align: center;
        }
        .question-button:hover {
            background-color: #BFDBFE;
            cursor: pointer;
        }
        .response-box {
            background-color: #F0F9FF;
            padding: 10px 16px;
            border-radius: 12px;
            margin-bottom: 12px;
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
        button {
            background-color: #3B82F6 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 24px !important;
            font-size: 16px !important;
        }
        @media screen and (max-width: 400px) {
            h1.title {
                font-size: 24px !important;
                padding: 0 10px;
            }

            .barre{
                width:100% !important;
            }

            .question-container {
                position: static !important;
                width: 100% !important;
                height: auto !important;
                margin-top: 20px;
                padding: 16px !important;
                box-shadow: none !important;
            }

            .question-button {
                font-size: 14px !important;
                padding: 10px !important;
            }

            .chat-bot, .chat-user {
                font-size: 14px !important;
                padding: 8px !important;
            }

            .response-box {
                font-size: 14px !important;
            }

            img {
                display: none !important;
            }

            .stTextInput>div>div>input {
                font-size: 14px !important;
                padding: 10px !important;
            }

            button {
                font-size: 14px !important;
                padding: 8px 16px !important;
            }
            .chatting{
                font-size: 9px;

            }
        }

        
    </style>
""", unsafe_allow_html=True)

# Illustration background
illu_path = "app/assets/illu_first.png"
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

st.markdown("<h1 class='title'>Questionnaire - 5 minutes</h1>", unsafe_allow_html=True)

if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "reponses" not in st.session_state:
    st.session_state.reponses = []
if "rag_response" not in st.session_state:
    st.session_state.rag_response = None
if "qf_chat_history" not in st.session_state:
    st.session_state.qf_chat_history = []
if "rag_done" not in st.session_state:
    st.session_state.rag_done = False

questions = [
    {"question": "Quel type d'activité préfères-tu ?", "choix": ["Travailler avec des données", "Utiliser mes mains", "Résoudre des problèmes", "Aider les autres"]},
    {"question": "Quel environnement te motive le plus ?", "choix": ["Bureau", "Extérieur", "Salle de classe", "Lieux de soin"]},
    {"question": "Préfères-tu travailler :", "choix": ["Seul", "En équipe", "Avec le public", "Parfois seul, parfois en équipe"]},
    {"question": "Quel domaine t'inspire le plus ?", "choix": ["Écologie", "Santé", "Technologies", "Voyages / International"]},
    {"question": "Tu te sens plus à l’aise avec :", "choix": ["Actions concrètes", "Communication", "Idées abstraites", "Création artistique"]},
]

index = st.session_state.question_index

st.markdown("<div class='question-container'>", unsafe_allow_html=True)

# Barre de progression
progress_percentage = int((index  / len(questions)) * 100)
st.markdown(f"""
    <div style='margin-bottom: 16px;'>
        <div class='barre' style='width: 38%; background-color: #E5E7EB; height: 10px; border-radius: 8px;'>
            <div style='width: {progress_percentage}%; background-color: #FBBF24; height: 100%; border-radius: 8px;'></div>
        </div>
    </div>
""", unsafe_allow_html=True)

if index < len(questions):
    question = questions[index]
    st.subheader(f"Question {index+1}/5")
    st.markdown(f"**{question['question']}**")

    for choix in question["choix"]:
        if st.button(choix, key=choix, help=None):
            st.session_state.reponses.append(choix)
            st.session_state.question_index += 1
            st.rerun()
else:
    #st.success("🎉 Merci pour tes réponses ! Voici les recommandations...")

    generated = f"""
    le type d'activité que je préfère est : {st.session_state.reponses[0]}
    l'environnement qui me motive le plus est : {st.session_state.reponses[1]}
    je préfère travailler : {st.session_state.reponses[2]}
    le domaine qui m'inspire le plus est : {st.session_state.reponses[3]}
    je me sens plus à l'aise avec : {st.session_state.reponses[4]}
    Peux-tu me proposer 3 secteurs d’activité adaptés à mon profil ? Pour chaque secteur, donne-moi 2 métiers correspondant, en variant entre des métiers connus et d’autres moins connus. Donne la réponse directement sans me poser de questions.
    """
    if not st.session_state.rag_done:
        rag_answer = answer_question(generated)
        st.session_state.rag_response = rag_answer
        st.session_state.qf_chat_history = [("Bot", rag_answer)]
        st.session_state.rag_done = True
        st.rerun()

    st.markdown("---")
    #st.markdown("<h3 style='background-color:white; border-radius: 8px;'>Voila Notre proposition, Tu peux maintenant continuer la conversation avec le chatbot : </h1>" , unsafe_allow_html=True)
    st.success("Voila Notre proposition, Tu peux maintenant continuer la conversation avec le chatbot :")
   # for speaker, message in st.session_state.qf_chat_history:
    #    css_class = "chat-user" if speaker == "Vous" else "chat-bot"
     #   st.markdown(f"<div class='{css_class}'><strong>{'👤' if speaker == 'Vous' else '🤖'} {speaker} :</strong> {message}</div>", unsafe_allow_html=True)

    chat_html = ""
    if st.session_state.qf_chat_history:
        chat_html += "<div class='chatting' style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:100%; margin-bottom:20px;'>"
        for speaker, message in st.session_state.qf_chat_history:
            if speaker == "Vous":
                chat_html += f"<div style='background:#3B82F6; color:white; padding:10px 16px; border-radius:12px; text-align:right; margin-left:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
            else:
                chat_html += f"<div style='background:#FBBF24; color:black; padding:10px 16px; border-radius:12px; text-align:left; margin-right:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
        chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)
    user_input = st.text_input("Ta question :", "")

    if st.button("Envoyer") and user_input.strip():
        st.session_state.qf_chat_history.append(("Vous", user_input))
        response = answer_question(user_input)
        st.session_state.qf_chat_history.append(("Bot", response))
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.button("🔄 Recommencer"):
    for key in ["question_index", "reponses", "rag_done", "rag_response", "qf_chat_history"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()