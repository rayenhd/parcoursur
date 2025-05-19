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
st.set_page_config(page_title="🧠 Test de personnalité", page_icon="🧩")

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
            width: 60%;
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
            background-color: #150e60 !important;
            color: white !important;
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
        @media only screen and (max-width: 480px) {
            h1.title {
                font-size: 24px;
            }
            .question-container {
                padding: 16px;
                width: 100%;
                left:0%;
            
            }
            .stElementContainer button {
                font-size: 13px !important;
                padding: 10px 14px !important;
                width: 95% !important;
            }
            .response-options {
                gap: 8px !important;
            }
            .titreQ{
                text-align: center;
            }
            .quest{
                width:100% !important;
                text-align: center !important;
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
illu_path = "app/assets/questionnaire_illustration_30min.png"
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
st.markdown("<h1 class='title'>TEST DE <strong style='color:#f2ae19'>PERSONNALITÉ </strong></h1>", unsafe_allow_html=True)

questions = [
    # Dimension Réaliste (R)
    "J’aime construire ou réparer des objets.",
    "J’aime travailler avec des outils ou des machines.",
    "Je préfère résoudre des problèmes pratiques.",
#    "Je suis à l'aise dans les environnements extérieurs, par exemple en travaillant sur des installations industrielles.",
#    "Je trouve satisfaisant de participer à des activités manuelles.",
#    "Je préfère les tâches concrètes aux activités théoriques.",
#    
#    # Dimension Investigateur (I)
#    "J’aime analyser des problèmes complexes et trouver des solutions.",
#    "Je prends plaisir à comprendre comment fonctionnent les choses.",
#    "Je suis passionné(e) par la recherche scientifique.",
#    "J’aime résoudre des énigmes ou des puzzles.",
#    "Je préfère étudier les phénomènes naturels et les lois scientifiques.",
#    "J’aime explorer des idées à travers des expériences et des simulations.",
#    
#    # Dimension Artistique (A)
#    "J’aime exprimer ma créativité à travers l’art ou la musique.",
#    "J’apprécie créer ou imaginer des projets uniques.",
#    "Je préfère les activités qui me permettent d’exprimer mes émotions.",
#    "Je trouve gratifiant de travailler sur des projets artistiques.",
#    "Je suis à l’aise dans des environnements non conventionnels, riches en expression créative.",
#    "J’ai souvent des idées originales que j’aime partager avec les autres.",
#    
#    # Dimension Social (S)
#    "J’aime aider les autres à résoudre leurs problèmes.",
#    "Je suis à l’aise pour parler en public.",
#    "Je trouve gratifiant d’accompagner et de soutenir les personnes.",
#    "J’aime travailler en équipe et créer une dynamique collective.",
#    "J’aime écouter et comprendre les besoins des autres.",
#    "Je suis souvent sollicité(e) pour donner des conseils ou de l'assistance aux autres.",
#    
#    # Dimension Entreprenant (E)
#    "J’aime persuader les autres et mener des projets.",
#    "Je suis motivé(e) par des défis et des situations où je peux prendre des initiatives.",
#    "J’aime organiser et diriger des activités de groupe.",
#    "J’aime prendre des décisions rapides dans des situations de compétition.",
#    "Je trouve stimulant de négocier ou de vendre des idées.",
#    "Je suis à l’aise dans des environnements où l’autonomie et le leadership sont valorisés.",
#    
#    # Dimension Conventionnel (C)
#    "J’aime organiser mes tâches et suivre des procédures claires.",
#    "Je prends soin de respecter les règles et les normes établies.",
#    "Je préfère travailler dans un cadre structuré et méthodique.",
#    "J’aime les activités qui demandent rigueur et précision.",
#    "Je suis à l’aise avec la gestion de données et l’utilisation d’outils bureautiques.",
#    "J’apprécie travailler sur des tâches administratives ou logistiques."
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
if "q30_chat_history" not in st.session_state:
    st.session_state.q30_chat_history = []

index = st.session_state.q30_index

st.markdown("<div class='question-container'>", unsafe_allow_html=True)

if index < len(questions):
    st.markdown(f"<h3 class='titreQ'> Question {index + 1}/{len(questions)} </h3>", unsafe_allow_html=True)
    st.markdown(f"<p class='quest' style='width:58%;'>{questions[index]}</p>", unsafe_allow_html=True)
    st.markdown("<div class='response-options'>", unsafe_allow_html=True)
    for opt in options:
        if st.button(opt, key=f"btn_{opt}_{index}"):
            st.session_state.q30_answers.append((questions[index], opt))
            st.session_state.q30_index += 1
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.q30_response is None:
        question_pour_ia = "Voici les réponses de mon test de personnalité basé sur le modèle RIASEC :\n\n"
        for i, (q, r) in enumerate(st.session_state.q30_answers, 1):
            question_pour_ia += f"{i}. {q} : {r}\n"
        question_pour_ia += "\nJe veux avant tout que tu me donnes mon résultat au Test Riasec, ensuite, Peux-tu me proposer 3 secteurs d’activité dans lesquels je pourrais m’épanouir, avec 2 métiers par secteur (connus et moins connus) ? Donne la réponse directement sans me poser de questions."
        rag_response = answer_question(question_pour_ia)
        st.session_state.q30_chat_history = [("Bot", rag_response)]
        st.session_state.q30_response = rag_response
        st.session_state.q30_chat.append(("Bot", rag_response))
        st.rerun()

    st.success("###   Voila les meilleurs métiers proposés par l'IA")

    chat_html = ""
    if st.session_state.q30_chat_history:
        chat_html += "<div class='chatting' style='background:#E0F2FE; padding:20px; border-radius:16px; max-width:100%; margin-bottom:20px;'>"
        for speaker, message in st.session_state.q30_chat_history:
            if speaker == "Vous":
                chat_html += f"<div style='background:#3B82F6; color:white; padding:10px 16px; border-radius:12px; text-align:right; margin-left:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
            else:
                chat_html += f"<div style='background:#FBBF24; color:black; padding:10px 16px; border-radius:12px; text-align:left; margin-right:auto; margin-bottom:10px; max-width:90%;'>{message}</div>"
        chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)
    user_input = st.text_input("Ta question :", "")

    if st.button("Envoyer") and user_input.strip():
        st.session_state.q30_chat_history.append(("Vous", user_input))
        response = answer_question(user_input)
        st.session_state.q30_chat_history.append(("Bot", response))
        st.rerun()

st.markdown("---")
if st.button("🔄 Recommencer le test"):
    for key in ["q30_index", "q30_answers", "q30_response", "q30_chat"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()