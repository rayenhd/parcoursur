import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from backend.models.rag.query_rag import answer_question

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
        body{
            overflow-x: hidden;
        }
        /*
        
        .st-b7{
            background-color: transparent;
        }

        .st-ae.st-af.st-ag.st-ah.st-ai.st-aj.st-ak.st-al.st-am.st-an.st-ao.st-ap.st-aq.st-ar.st-as.st-at.st-au.st-av.st-aw.st-ax.st-ay.st-az.st-b0.st-b1.st-b2.st-b3.st-b4.st-b5.st-b6.st-b7.st-b8.st-b9.st-ba{
            border: none;    
            outline: none;
            background-color: transparent;
        }
            
        .title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            text-align: center;
            margin-top: 20px;
        }
        .question-box {
            position: absolute;
            top: 40%;
            left: -30%;
            width: 90%;
            height: 60vh;
            background-color: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .chat-bot {
            background-color: red;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .chat-user {
            background-color: red;
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
            color: #1E3A8A !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 8px !important;
            padding: 10px !important;
            width: 73% !important;
            position: absolute !important;
            top: 70% !important;
            height: 40vh;
            left: -19%;
        } 
        
        .stButton.st-emotion-cache-8atqhb.e1mlolmg0{
            height: 40vh;
        }

        .stTextInput input{
            background-color: #BFDBFE !important;
            border: none !important;
            color: white !important;
            position: absolute;
            top: 80%;
            border-radius: 8px !important;
            width: 100%;
            left: -4%;
        }

        */
        button{
            background-color: #150e60 !important;
            color: white !important;
        }    
        
        @media screen and (max-width: 400px) {
            h1.title {
                font-size: 24px !important;
                padding: 0 10px;
            }

            .question-box {
                width: 95% !important;
                padding: 16px !important;
                left: 20%;
                display: none !important;
            }

            .chat-bot, .chat-user {
                font-size: 14px !important;
                padding: 8px !important;
            }

            .stTextInput>div>div>input {
                font-size: 14px !important;
                padding: 10px !important;
            }
            .stTextInput {
                font-size: 14px !important;
                padding: 10px !important;
            }

            button {
                font-size: 14px !important;
                padding: 8px 16px !important;
            }

            .question{
                left: 10% !important;
            }

            img {
                display: none !important;
            }  
            .chatting{
                font-size: 9px;
            }  
            .barre{
                width: 95% !important;
                left: 4% !important;
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
        }
        
    </style>
""", unsafe_allow_html=True)

# Background illustration
illu_path = "app/assets/illu_first.png"
if os.path.exists(illu_path):
    with open(illu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style='position: absolute; width: 100%; height: 280px;'>
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: auto; height: auto; left: 32%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.4;'>
            <div style='position: absolute; z-index: 2; padding: 20px;'>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title' style='color: #150e60;'>QUESTIONNAIRE - <strong style='color:#f2ae19'>10 MINUTES </strong></h1>", unsafe_allow_html=True)

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
if "qd_chat_history" not in st.session_state:
    st.session_state.qd_chat_history = []

# === Logique d'affichage ===
index = st.session_state.index_q
st.markdown("<div class='question-box'>", unsafe_allow_html=True)
# Barre de progression
progress_percentage = int((index / 3) * 100)
st.markdown(f"""
    <div style='margin-bottom: 16px;'>
        <div  class='barre' style='width: 78%; background-color:  #150e60; height: 10px; border-radius: 8px; left:-0%; position: absolute;'>
            <div style='width: {progress_percentage}%; background-color: #FBBF24; height: 100%; border-radius: 8px;'></div>
        </div>
    </div>
""", unsafe_allow_html=True)
if not st.session_state.q10_complete:
    st.markdown(f"""<div style=' text-align: center; top:25%; left: 0%; overflow: auto; width: 80% ; height: 40vh;' class='question'> 
                <p class='aaaa' style='margin-top:20px; font-size:100%;'> <strong> {st.session_state.q10_current_question} </strong></p>
    </div><div>
    """, unsafe_allow_html=True)
    st.markdown("<div>", unsafe_allow_html=True)
    user_answer = st.text_input("")

    if st.button("Valider") and user_answer.strip():
        st.session_state.q10_history.append((st.session_state.q10_current_question, user_answer.strip()))
        print("____________ envoyé _____________")
        print(st.session_state.q10_history)
        st.session_state.index_q+=1

        if len(st.session_state.q10_history) >= 3:
            if "q10_final_reco" not in st.session_state:
                question = f"""
                voila mes réponses à différentes questions :

                {st.session_state.q10_history}
                je veux que tu me proposes les métiers qui me correspondent le mieux
                """
                st.session_state.q10_final_reco = answer_question(question)
                print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")

            #st.markdown("### 🔍 Recommandation personnalisée")
            #st.write(st.session_state.q10_final_reco)
            st.session_state.q10_complete = True
            st.rerun()

        else:
            st.session_state.q10_current_question = generate_next_question(st.session_state.q10_history)
            st.rerun()
else:
    st.success("✅ Merci pour tes réponses ! Voici ce que je te recommande :")

    if st.session_state.q10_reco is None:
        question = f"""
        voila mes réponses à différentes questions :

        {st.session_state.q10_history}
        je veux que tu me proposes les métiers qui me correspondent le mieux
        """
        #qa_pairs = [f"Q: {q}\nR: {r}" for q, r in st.session_state.q10_history]
        st.session_state.q10_reco = answer_question(question)

    #st.markdown("### 🔍 Recommandation personnalisée")
    #st.write(st.session_state.q10_reco)

    st.session_state.qd_chat_history = [("Bot", st.session_state.q10_final_reco)]
    chat_html = ""
    if st.session_state.qd_chat_history:
        chat_html += "<div class='chatting'  style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:800px; margin-bottom:20px;'>"
        for speaker, message in st.session_state.qd_chat_history:
            if speaker == "Vous":
                chat_html += f"<div style='background:#3B82F6; color:white; padding:10px 16px; border-radius:12px; text-align:right; margin-left:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
            else:
                chat_html += f"<div style='background:#FBBF24; color:black; padding:10px 16px; border-radius:12px; text-align:left; margin-right:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
        chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)


    if st.button("🔄 Recommencer"):
        for key in ["q10_history", "q10_current_question", "q10_complete", "q10_reco", "index_q"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)