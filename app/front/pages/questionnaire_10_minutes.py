import os
import re
import faiss
import pickle
import tempfile
from typing import List

import streamlit as st
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools import DuckDuckGoSearchRun
from openai import AzureOpenAI
st.set_page_config(page_title="🔎 Questionnaire - 10 minutes", page_icon="🕙")

# === Configuration
load_dotenv()
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
USE_WEB_SEARCH = True
AZURE_DEPLOYMENT = "gpt-4o"


from typing import List, Tuple
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from openai import AzureOpenAI
import streamlit as st

AZURE_API_KEY = st.secrets["azure"]["AZURE_API_KEY"]
AZURE_ENDPOINT = st.secrets["azure"]["AZURE_ENDPOINT"]
AZURE_DEPLOYMENT = "gpt-4o"  # ou ton nom de déploiement
AZURE_API_VERSION = st.secrets["azure"]["AZURE_API_VERSION"]



client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY
)


# === Prompt Template pour générer la prochaine question
prompt_template = PromptTemplate.from_template("""
Tu es un conseiller en orientation scolaire et professionnelle.
Tu dois poser une série de 7 questions personnalisées pour aider un jeune à découvrir les secteurs d'activités et les métiers qui pourraient lui correspondre.

Voici l'historique des questions déjà posées et des réponses fournies :
{history}

Propose maintenant une nouvelle question simple, claire et fermée (avec des choix). Ne pose pas une question déjà posée.
Ta réponse doit être au format :
Question: <texte de la question>
Choix: <choix1>, <choix2>, <choix3>, <choix4>
""")


def generate_next_question(history_pairs: list[tuple[str, str]]) -> str:
    # Reformatage de l'historique
    history_text = "\n".join([f"Q: {q}\nR: {r}" for q, r in history_pairs]) or "(aucune question posée)"

    prompt = f"""
Tu joues le rôle d’un conseiller d’orientation expert. Tu vas poser 7 questions à un utilisateur pour cerner son profil.

Voici les échanges précédents :
{history_text}

Pose-moi une nouvelle question (courte, claire, adaptée à un jeune) pour continuer à mieux cerner ma personnalité et mes préférences professionnelles.

Réponds uniquement par la question, sans explication ni commentaire.
""".strip()

    # Appel au LLM
    response = answer_question(prompt)

    # Debug
    print("🧠 Réponse du LLM pour la question suivante :")
    print(response)

    # Nettoyage de la réponse : on garde la première ligne non vide
    lines = [line.strip() for line in response.split("\n") if line.strip()]
    if not lines:
        raise ValueError("Format de la réponse du LLM incorrect.")
    
    return response

def generate_final_recommendation(history_pairs: List[Tuple[str, str]]) -> str:
    history_text = "\n".join([f"Q: {q}\nR: {r}" for q, r in history_pairs])
    prompt = f"""
Tu es un conseiller d’orientation scolaire et professionnelle. Voici le profil d’un utilisateur basé sur ses réponses à 7 questions :

{history_text}

À partir de ces réponses, propose 3 secteurs d’activité dans lesquels il pourrait s’épanouir.
Pour chaque secteur, donne 2 métiers pertinents (un très connu, un moins connu).
Explique brièvement pourquoi ces suggestions sont adaptées à la personne.
Donne une réponse claire, bienveillante, professionnelle et directement exploitable.
"""

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Tu es un assistant d’orientation scolaire bienveillant, drôle et clair."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    return response

# === Initialisation des modèles et outils
embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
web_search_tool = DuckDuckGoSearchRun()

# === GCS : téléchargement & chargement des vectorstores
bucket_name = "parcoursur_vectorized_data"
prefix = "vectorstore/chunks"

def download_blob(bucket_name, source_blob_name, destination_file_name):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def load_all_vectorstores(bucket_name, prefix):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    stores = []
    temp_dir = tempfile.mkdtemp()

    vectorstore_dirs = {}
    for blob in blobs:
        parts = blob.name.split('/')
        if len(parts) >= 2:
            dir_name = parts[1]
            vectorstore_dirs.setdefault(dir_name, []).append(blob)

    for dir_name, blob_list in vectorstore_dirs.items():
        local_dir = os.path.join(temp_dir, dir_name)
        os.makedirs(local_dir, exist_ok=True)

        required_files = ["faiss_index.bin", "docstore.pkl", "id_mapping.pkl"]
        for file_name in required_files:
            blob_path = f"{prefix}/{dir_name}/{file_name}"
            local_path = os.path.join(local_dir, file_name)
            download_blob(bucket_name, blob_path, local_path)

        try:
            index = faiss.read_index(os.path.join(local_dir, "faiss_index.bin"))
            with open(os.path.join(local_dir, "docstore.pkl"), "rb") as f:
                docstore = pickle.load(f)
            with open(os.path.join(local_dir, "id_mapping.pkl"), "rb") as f:
                id_map = pickle.load(f)
            store = FAISS(index=index, docstore=docstore, index_to_docstore_id=id_map,
                          embedding_function=embedding_model)
            stores.append(store)
        except Exception as e:
            print(f"❌ Erreur dans {dir_name}: {e}")

    return stores

# === Recherche vectorielle
def get_relevant_documents(query: str, k=5) -> List[Document]:
    docs = []
    stores = load_all_vectorstores(bucket_name, prefix)
    for store in stores:
        try:
            docs += store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erreur dans un chunk : {e}")
    return docs[:k]

# === Prompt d'orientation
prompt_template = PromptTemplate.from_template("""
Tu es un conseiller expert en orientation scolaire et professionnelle qui doit :
- Répondre avec un ton simple et respectueux, compréhensible pour les jeunes
- Répondre également avec humour mais toujours dans le respect
- Utiliser un langage clair et facile à comprendre
- Prendre en compte les attentes de l'utilisateur
Tu dois proposer 3 secteurs d'activités dans lesquels pourrait se retrouver l'utilisateur, et 2 métiers par secteur en expliquant brièvement chaque métier.
Pour chaque métier, tu dois proposer un parcours scolaire adapté à suivre après le bac.
Base-toi uniquement sur les index fournis. Si tu ne trouves pas la réponse, pose une question pour orienter l'utilisateur.

Voici l'historique de la conversation :
{history}

Nouvelle question de l'utilisateur :
{input}

Voici des documents pertinents :
{context}
""")

# === Historique simplifié
history = []

# === Fonction principale
def answer_question(question: str, use_web: bool = False) -> str:
    if "memory_history" not in st.session_state:
        st.session_state.memory_history = []

    st.session_state.memory_history.append(f"Human: {question}")

    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    web_docs = []
    if use_web:
        web_docs = [Document(page_content="[Web] " + web_search_tool.run(question))]

    context = "\n\n".join(set(doc.page_content for doc in internal_docs + web_docs))

    prompt = prompt_template.format(
        input=question,
        history="\n".join(st.session_state.memory_history[-5:]),
        context=context
    )

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Tu es un assistant d’orientation scolaire bienveillant, drôle et clair."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1200
    )

    answer = response.choices[0].message.content.strip()
    st.session_state.memory_history.append(f"AI: {answer}")
    return answer


import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.rag.generate_question import generate_next_question, generate_final_recommendation


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
        st.session_state.index_q = len(st.session_state.q10_history)

        if st.session_state.index_q >= 3:
            if "q10_final_reco" not in st.session_state:
                question = f"""
                voila mes réponses à différentes questions :

                {st.session_state.q10_history}
                je veux que tu me proposes les métiers qui me correspondent le mieux
                """
                st.session_state.q10_final_reco = answer_question(question)
            st.session_state.q10_complete = True
            st.rerun()
        else:
            next_q = generate_next_question(st.session_state.q10_history)
            print(">>> Prochaine question :", next_q)
            if not next_q:
                st.session_state.q10_complete = True
            else:
                st.session_state.q10_current_question = next_q
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