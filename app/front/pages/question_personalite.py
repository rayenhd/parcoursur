import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.rag.query_rag import answer_question

st.set_page_config(page_title="🧠 Test de personnalité", page_icon="🧩")

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
        .response-options {
            display: flex !important;
            justify-content: space-between !important;
            margin-top: 20px !important;
        }
        .stElementContainer button {
            background-color: #E0F2FE !important;
            color: #111827 !important;
            padding: 12px 16px !important;
            border-radius: 24px !important;
            font-size: 14px !important;
            border: none !important;
            cursor: pointer !important;
            flex: 1 !important;
            margin: 0 4px !important;
            width: 35% !important;
        }
        .response-button:hover {
            background-color: #BFDBFE;
        }
    </style>
""", unsafe_allow_html=True)

# Background illustration
illu_path = "assets/questionnaire_illustration_30min.png"
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
st.markdown("<h1 class='title'>Test de personnalité</h1>", unsafe_allow_html=True)

questions = [
    # Dimension Réaliste (R)
    "J’aime construire ou réparer des objets.",
    "J’aime travailler avec des outils ou des machines.",
    "Je préfère résoudre des problèmes pratiques.",
    "Je suis à l'aise dans les environnements extérieurs, par exemple en travaillant sur des installations industrielles.",
    "Je trouve satisfaisant de participer à des activités manuelles.",
    "Je préfère les tâches concrètes aux activités théoriques.",
    
    # Dimension Investigateur (I)
    "J’aime analyser des problèmes complexes et trouver des solutions.",
    "Je prends plaisir à comprendre comment fonctionnent les choses.",
    "Je suis passionné(e) par la recherche scientifique.",
    "J’aime résoudre des énigmes ou des puzzles.",
    "Je préfère étudier les phénomènes naturels et les lois scientifiques.",
    "J’aime explorer des idées à travers des expériences et des simulations.",
    
    # Dimension Artistique (A)
    "J’aime exprimer ma créativité à travers l’art ou la musique.",
    "J’apprécie créer ou imaginer des projets uniques.",
    "Je préfère les activités qui me permettent d’exprimer mes émotions.",
    "Je trouve gratifiant de travailler sur des projets artistiques.",
    "Je suis à l’aise dans des environnements non conventionnels, riches en expression créative.",
    "J’ai souvent des idées originales que j’aime partager avec les autres.",
    
    # Dimension Social (S)
    "J’aime aider les autres à résoudre leurs problèmes.",
    "Je suis à l’aise pour parler en public.",
    "Je trouve gratifiant d’accompagner et de soutenir les personnes.",
    "J’aime travailler en équipe et créer une dynamique collective.",
    "J’aime écouter et comprendre les besoins des autres.",
    "Je suis souvent sollicité(e) pour donner des conseils ou de l'assistance aux autres.",
    
    # Dimension Entreprenant (E)
    "J’aime persuader les autres et mener des projets.",
    "Je suis motivé(e) par des défis et des situations où je peux prendre des initiatives.",
    "J’aime organiser et diriger des activités de groupe.",
    "J’aime prendre des décisions rapides dans des situations de compétition.",
    "Je trouve stimulant de négocier ou de vendre des idées.",
    "Je suis à l’aise dans des environnements où l’autonomie et le leadership sont valorisés.",
    
    # Dimension Conventionnel (C)
    "J’aime organiser mes tâches et suivre des procédures claires.",
    "Je prends soin de respecter les règles et les normes établies.",
    "Je préfère travailler dans un cadre structuré et méthodique.",
    "J’aime les activités qui demandent rigueur et précision.",
    "Je suis à l’aise avec la gestion de données et l’utilisation d’outils bureautiques.",
    "J’apprécie travailler sur des tâches administratives ou logistiques."
]
options = ["Pas d'accord", "Neutre", "D'accord"]

if "q30_index" not in st.session_state:
    st.session_state.q30_index = 0
if "q30_answers" not in st.session_state:
    st.session_state.q30_answers = []
if "q30_response" not in st.session_state:
    st.session_state.q30_response = None
if "q30_chat" not in st.session_state:
    st.session_state.q30_chat = []

index = st.session_state.q30_index

st.markdown("<div class='question-container'>", unsafe_allow_html=True)

if index < len(questions):
    st.subheader(f"Question {index + 1}/{len(questions)}")
    st.markdown(f"**{questions[index]}**")
    st.markdown("<div class='response-options'>", unsafe_allow_html=True)
    for opt in options:
        if st.button(opt, key=f"btn_{opt}_{index}"):
            st.session_state.q30_answers.append((questions[index], opt))
            st.session_state.q30_index += 1
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.markdown("</div>", unsafe_allow_html=True)
    st.success("✅ Merci pour tes réponses ! Voici ce que je te recommande :")
    if st.session_state.q30_response is None:
        question_pour_ia = "Voici les réponses de mon test de personnalité basé sur le modèle RIASEC :\n\n"
        for i, (q, r) in enumerate(st.session_state.q30_answers, 1):
            question_pour_ia += f"{i}. {q} : {r}\n"
        question_pour_ia += "\nPeux-tu me proposer 3 secteurs d’activité dans lesquels je pourrais m’épanouir, avec 2 métiers par secteur (connus et moins connus) ? Donne la réponse directement sans me poser de questions."
        rag_response = answer_question(question_pour_ia)
        st.session_state.q30_response = rag_response
        st.session_state.q30_chat.append(("Bot", rag_response))
        st.rerun()

    st.markdown("--- Voila les meilleurs métiers proposés par l'IA")
    st.markdown("### 💬 Tu peux maintenant poser d'autres questions à l'IA :")

    for speaker, message in st.session_state.q30_chat:
        css_class = "chat-user" if speaker == "Vous" else "chat-bot"
        st.markdown(f"<div class='{css_class}'><strong>{'👤' if speaker == 'Vous' else '🤖'} {speaker} :</strong> {message}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Ta question :", key="q30_input")
    if st.button("Envoyer", key="q30_send") and user_input.strip():
        st.session_state.q30_chat.append(("Vous", user_input))
        response = answer_question(user_input)
        st.session_state.q30_chat.append(("Bot", response))
        st.rerun()

st.markdown("---")
if st.button("🔄 Recommencer le test"):
    for key in ["q30_index", "q30_answers", "q30_response", "q30_chat"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
