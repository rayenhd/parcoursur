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

# === Chargement des variables d'environnement
load_dotenv()
HUGGINGFACE_TOKEN = "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"

# === Configuration
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
HUGGINGFACE_REPO = "meta-llama/Meta-Llama-3-8B-Instruct"  # ou HuggingFaceH4/zephyr-7b-beta
USE_WEB_SEARCH = True

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
Tu es un conseiller expert en orientation scolaire et professionnelle.
Voici l'historique de la conversation :
{history}

Nouvelle question de l'utilisateur :
{input}

Voici des documents pertinents :
{context}

Donne une réponse claire, bienveillante et adaptée à la situation.
""")

# === Modèle Hugging Face
llm = HuggingFaceEndpoint(
    repo_id=HUGGINGFACE_REPO,
    temperature=0.5,
    max_new_tokens=512,
    huggingfacehub_api_token=HUGGINGFACE_TOKEN
)

# === Historique custom
history = []

# === Fonction principale
def answer_question(question: str, use_web: bool = False) -> str:
    history.append(f"Human: {question}")

    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    web_docs = []
    if use_web:
        web_docs = [Document(page_content="[Web] " + web_search_tool.run(question))]

    context = "\n\n".join(set(doc.page_content for doc in internal_docs + web_docs))

    response = llm.invoke(
        prompt_template.format(
            input=question,
            history="\n".join(history[-5:]),  # garder seulement les 5 derniers échanges
            context=context
        )
    )

    history.append(f"AI: {response}")

    return response.strip()

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
