import os
import re
import faiss
import pickle
from typing import List
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.tools import DuckDuckGoSearchRun
import openai
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential


# === Chargement des variables d'environnement
load_dotenv()
HUGGINGFACE_TOKEN = "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"

# === Configuration
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
HUGGINGFACE_REPO = "OpenAssistant/oasst-sft-1-pythia-12b"  # ou HuggingFaceH4/zephyr-7b-beta
USE_WEB_SEARCH = True
AZURE_API_KEY = "70vwwlq5J8a2CrqnMZVfxY83ztdx6Ahgor5y2WbUHtTBgOhuROIdJQQJ99BDAC5T7U2XJ3w3AAABACOGrF5i"
AZURE_ENDPOINT = "https://oai-test-rg-test.openai.azure.com/"
AZURE_DEPLOYMENT = "gpt-4o"  # ou ton nom de déploiement
AZURE_API_VERSION = "2025-01-01-preview"

client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY
)

"""""
openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT
openai.api_version = AZURE_API_VERSION
openai.api_key = AZURE_API_KEY
"""

# === Initialisation des composants
embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
web_search_tool = DuckDuckGoSearchRun()

# === Chargement des FAISS vectorstores
# === Chargement des FAISS vectorstores
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

# === Recherche vectorielle
def get_relevant_documents(query: str, k=5) -> List[Document]:
    docs = []
    for store in load_all_vectorstores():
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
- Donner des exemples concrets, des statistiques ou des témoignages quand c’est pertinent
Tu dois proposer 3 secteurs d'activités dans lequel pourrait se retrouver l'utilisateur, et 2 métiers par secteur.
Base toi uniquement sur les index fournis, si tu ne trouves pas la réponse, pose une question pour orienter l'utilisateur.

Voici l'historique de la conversation :
{history}

Nouvelle question de l'utilisateur :
{input}

Voici des documents pertinents :
{context}

Donne une réponse claire, bienveillante et adaptée à la situation.
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
        max_tokens=800
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
