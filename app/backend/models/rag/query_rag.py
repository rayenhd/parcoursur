import os
import re
import faiss
import pickle
from typing import List
from dotenv import load_dotenv
from google.cloud import storage
import tempfile
from google.oauth2 import service_account
import streamlit as st

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.embeddings import OpenAIEmbeddings
import openai
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential


# === Chargement des variables d'environnement
load_dotenv()

# === Configuration
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
HUGGINGFACE_REPO = "OpenAssistant/oasst-sft-1-pythia-12b"  # ou HuggingFaceH4/zephyr-7b-beta
USE_WEB_SEARCH = True
AZURE_DEPLOYMENT = "gpt-4o"  # ou ton nom de déploiement


"""""
client = AzureOpenAI(
    api_key=st.secrets["azure"]["AZURE_API_KEY"],
    azure_endpoint=st.secrets["azure"]["AZURE_ENDPOINT"],
    api_version=st.secrets["azure"]["AZURE_API_VERSION"]
)
"""
client = AzureOpenAI(
    api_key="563i46EB2UGwXDYza3g29DjU3xH7ytdS7dSHmtWGpQBRNzVqkHHTJQQJ99BEACHYHv6XJ3w3AAAAACOGgErO",
    azure_endpoint="https://aissa-mapkatvd-eastus2.cognitiveservices.azure.com/",
    api_version="2025-01-01-preview"
)


"""""
openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT
openai.api_version = AZURE_API_VERSION
openai.api_key = AZURE_API_KEY
"""

# === Initialisation des composants
embedding_model = OpenAIEmbeddings(openai_api_key=st.secrets["azure"]["AZURE_API_KEY"])
web_search_tool = DuckDuckGoSearchRun()

# === Chargement des FAISS vectorstores
# === Chargement des FAISS vectorstores

bucket_name = "parcoursur_vectorized_data"
prefix = "vectorstore/chunks"

"""""
def load_all_vectorstores() -> List[FAISS]:
    stores = []
    for name in os.listdir(VECTORSTORE_DIR):
        path = os.path.join(VECTORSTORE_DIR, name)
        if not os.path.isdir(path):
            continue
        try:
            index = faiss.read_index(os.path.join(path, "faiss_index.bin"))
            with open(os.path.join(path, "docstore.pkl"), "rb") as f:
                docstore = pickle.load(f)
            with open(os.path.join(path, "id_mapping.pkl"), "rb") as f:
                id_map = pickle.load(f)
            store = FAISS(index=index, docstore=docstore, index_to_docstore_id=id_map, embedding_function=embedding_model)
            stores.append(store)
        except Exception as e:
            print(f"❌ Erreur dans {name}: {e}")
    return stores
"""

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Télécharge un fichier depuis GCS."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def load_all_vectorstores(bucket_name, prefix):
    """Charge tous les vectorstores depuis un bucket GCS."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = storage.Client(credentials=credentials)
    #storage_client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    stores = []
    temp_dir = tempfile.mkdtemp()

    # Regrouper les fichiers par dossier
    vectorstore_dirs = {}
    for blob in blobs:
        parts = blob.name.split('/')
        if len(parts) >= 2:
            dir_name = parts[1]
            if dir_name not in vectorstore_dirs:
                vectorstore_dirs[dir_name] = []
            vectorstore_dirs[dir_name].append(blob)

    for dir_name, blob_list in vectorstore_dirs.items():
        local_dir = os.path.join(temp_dir, dir_name)
        os.makedirs(local_dir, exist_ok=True)

        # Télécharger les fichiers nécessaires
        required_files = ["faiss_index.bin", "docstore.pkl", "id_mapping.pkl"]
        for file_name in required_files:
            blob_path = f"{prefix}/{dir_name}/{file_name}"
            local_path = os.path.join(local_dir, file_name)
            download_blob(bucket_name, blob_path, local_path)

        # Charger le vectorstore
        try:
            index = faiss.read_index(os.path.join(local_dir, "faiss_index.bin"))
            with open(os.path.join(local_dir, "docstore.pkl"), "rb") as f:
                docstore = pickle.load(f)
            with open(os.path.join(local_dir, "id_mapping.pkl"), "rb") as f:
                id_map = pickle.load(f)
            store = FAISS(index=index, docstore=docstore, index_to_docstore_id=id_map, embedding_function=embedding_model)
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

# === Prompt
prompt_template = PromptTemplate.from_template("""
Tu es un conseiller expert en orientation scolaire et professionnelle qui doit :
- Répondre avec un ton simple et respectueux, compréhensible pour les jeunes
- Répondre également avec humour mais toujours dans le respect
- Utiliser un langage clair et facile à comprendre
- Prendre en compte les attentes de l'utilisateur
Tu dois proposer 3 secteurs d'activités dans lequel pourrait se retrouver l'utilisateur, et 2 métiers par secteur en expliquant brièvement chaque métier.
Pour chaque métier, tu dois proposer un parcours scolaire adapté à suivre après le bac.
Base toi uniquement sur les index fournis, si tu ne trouves pas la réponse, pose une question pour orienter l'utilisateur.

Voici l'historique de la conversation :
{history}

Nouvelle question de l'utilisateur :
{input}

Voici des documents pertinents :
{context}

""")

# === Modèle Hugging Face
#llm = HuggingFaceEndpoint(
 #   repo_id=HUGGINGFACE_REPO,
#    temperature=0.2,
#    task="text-generation",
#    max_new_tokens=1024,
#    huggingfacehub_api_token=HUGGINGFACE_TOKEN
#)

# === Historique custom
history = []

# === Fonction principale
def answer_question(question: str, use_web: bool = False) -> str:
    print("la question est :     ", question)
    history.append(f"Human: {question}")

    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    web_docs = []
    
    #if use_web:
     #   web_docs = [Document(page_content="[Web] " + web_search_tool.run(question))]

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

    #response = llm.invoke(
    #    prompt_template.format(
     #       input=question,
     #       history="\n".join(history[-5:]),  # garder seulement les 5 derniers échanges
     #       context=context
     #   )
   # )
    #clean_response = re.sub(r"(Répondre.*?)(?=Répondre|$)", "", response, flags=re.IGNORECASE | re.DOTALL).strip()
    #history.append(f"AI: {clean_response}")

    #return clean_response.strip()
    answer = response.choices[0].message.content.strip()
    history.append(f"AI: {answer}")

    return answer

# === Interface CLI
if __name__ == "__main__":
    print("💬 Chatbot RAG + Mémoire custom (inspiré de applied-ai-rag-assistant)")
    while True:
        user_input = input("\nToi : ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Fin de la conversation.")
            break
        elif user_input.lower() == "reset":
            history.clear()
            print("🧼 Mémoire effacée.")
            continue
        response = answer_question(user_input, use_web=USE_WEB_SEARCH)
        print("\n🤖 IA :", response)