import streamlit as st
from openai import AzureOpenAI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
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

# === Configuration
load_dotenv()
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
USE_WEB_SEARCH = True
AZURE_DEPLOYMENT = "gpt-4o"
AZURE_API_VERSION = "2025-01-01-preview"

# === AzureOpenAI Client (clé en dur pour les tests)
client = AzureOpenAI(
    api_key="563i46EB2UGwXDYza3g29DjU3xH7ytdS7dSHmtWGpQBRNzVqkHHTJQQJ99BEACHYHv6XJ3w3AAAAACOGgErO",
    azure_endpoint="https://aissa-mapkatvd-eastus2.cognitiveservices.azure.com/",
    api_version=AZURE_API_VERSION
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

    print("Question posée :", question)
    history.append(f"Human: {question}")

    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    web_docs = []
    if use_web:
        web_docs = [Document(page_content="[Web] " + web_search_tool.run(question))]

    context = "\n\n".join(set(doc.page_content for doc in internal_docs + web_docs))

    prompt = prompt_template.format(
        input=question,
        history="\n".join(history[-5:]),
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
    history.append(f"AI: {answer}")
    return answer



# === Configuration Azure OpenAI ===
API_KEY = "563i46EB2UGwXDYza3g29DjU3xH7ytdS7dSHmtWGpQBRNzVqkHHTJQQJ99BEACHYHv6XJ3w3AAAAACOGgErO"
ENDPOINT = "https://aissa-mapkatvd-eastus2.cognitiveservices.azure.com/"
API_VERSION = "2025-01-01-preview"
DEPLOYMENT_NAME = "gpt-4o"  # ⚠️ Mets ici le nom exact de ton déploiement Azure

# === Création du client AzureOpenAI ===
client = AzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version=API_VERSION
)

# === Interface Streamlit ===
st.title("🔍 Test Azure OpenAI sur Streamlit Cloud")
st.write("Ce test vérifie si l’appel à Azure OpenAI fonctionne bien sur Streamlit Community Cloud.")

if st.button("📡 Tester Azure OpenAI"):
    try:
        response = response = answer_question("testttt")

    except Exception as e:
        st.error("❌ Erreur lors de l’appel à Azure OpenAI :")
        st.exception(e)

# Diagnostic supplémentaire
import os
#st.write("🔍 Variable OPENAI_API_KEY dans l’environnement :",st.secrets["OPENAI_API_KEY"])
#st.write("🔍 Variable OPENAI_API_BASE dans l’environnement :",st.secrets["OPENAI_API_KEY"])
