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
st.set_page_config(page_title="🧠 Questionnaire Express", page_icon="⏱️")

# === Configuration
load_dotenv()
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
USE_WEB_SEARCH = True
AZURE_DEPLOYMENT = "gpt-4o"

# === AzureOpenAI Client (clé en dur pour les tests)
client = AzureOpenAI(
    api_key=st.secrets["azure"]["AZURE_API_KEY"],
    azure_endpoint=st.secrets["azure"]["AZURE_ENDPOINT"],
    api_version=st.secrets["azure"]["AZURE_API_VERSION"]
)

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
            color: #150e60;
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
            background-color: #150e60;
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
            background-color: #150e60 !important;
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
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: auto; height: auto; left: 32%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.4;'>
            <div style='position: absolute; z-index: 2; padding: 20px;'>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>QUESTIONNAIRE - <strong style='color:#f2ae19'>5 MINUTES</strong></h1>", unsafe_allow_html=True)

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