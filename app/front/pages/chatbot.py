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
from langchain_openai import AzureOpenAIEmbeddings

st.set_page_config(page_title="Chatbot d'orientation", page_icon="🤖")


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



# pages/1_Chatbot_orientation.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from PIL import Image
import base64


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
            font-weight: 1000;
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
        /*
        .stElementContainer.element-container.st-emotion-cache-kj6hex.eu6p4el1{
            display: none;
        }
            
        .stElementContainer.element-container.st-emotion-cache-kj6hex.eu6p4el1:first-child{

            display:none;    
        }
        .stElementContainer.element-container.st-emotion-cache-kj6hex.eu6p4el1{
            height: 10vh;
        }
        
        */
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

            /*
            .st-emotion-cache-16tyu1:first-child{
                width: 30% !important;
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
#logo_path = os.path.abspath("assets/logo_complet.png")
#if os.path.exists(logo_path):
#    with open(logo_path, "rb") as image_file:
#        encoded_string = base64.b64encode(image_file.read()).decode()
#    st.markdown(f"""
#        <a href='.'>
#        <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: 30%; height: auto; left: -1%; top:-30%; object-fit: cover; border-radius: 16px; opacity: 0.8;'> </a>
#    """, unsafe_allow_html=True)

# Image de fond et titre par-dessus
illu_path = os.path.abspath("app/assets/chatbot_illu.png")
if os.path.exists(illu_path):
    with open(illu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style='position: relative; width: 100%; height: 280px;'>
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: 120%; height: auto; left: 23%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.3;'>
            <div style='position: relative; z-index: 2; padding: 20px;'>
                <h1 style='color:#1E3A8A;'>CHATBOT <strong style='color:#f2ae19'> D'ORIENTATION </strong></h1>
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
    chat_html += "<div class='chatting' style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:100%; margin-bottom:20px;'>"
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