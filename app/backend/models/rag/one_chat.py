import os
import faiss
import pickle
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import LLMChain
from langchain.tools import DuckDuckGoSearchRun
from langchain_huggingface import HuggingFaceEndpoint

# === Chargement des variables d'environnement
load_dotenv()

# === Config
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
HUGGINGFACE_REPO = "mistralai/Mistral-7B-Instruct-v0.1"

embedding_model = SentenceTransformerEmbeddings(model_name=EMBED_MODEL_NAME)
web_search_tool = DuckDuckGoSearchRun()

# === Chargement de tous les vecteurs FAISS ===
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
            print(f"❌ Erreur lors du chargement de {name}: {e}")
    return stores

# === Recherche dans les données internes ===
def get_relevant_documents(query: str, k=5) -> List[Document]:
    docs = []
    for store in load_all_vectorstores():
        try:
            docs += store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erreur de recherche dans un chunk : {e}")
    return docs[:k]

# === Recherche Web
def get_web_documents(query: str) -> List[Document]:
    results = web_search_tool.run(query)
    return [Document(page_content=results, metadata={"source": "web"})]

# === Prompt système
def generate_prompt() -> PromptTemplate:
    return PromptTemplate.from_template("""
Tu es un assistant pédagogique expert. Tu dois répondre de manière claire, complète et accessible à des collégiens, lycéens ou étudiants.

Contexte : {context}

Question : {question}
Réponse :
""")

# === Fonction principale
def answer_question(question: str, use_web: bool = False) -> str:
    print(f"❓ Question : {question}")
    
    # Récupération des documents internes
    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    # Recherche web facultative
    web_docs = []
    if use_web:
        print("🌐 Recherche Web activée")
        web_docs = get_web_documents(question)
        for doc in web_docs:
            doc.page_content = "[Web] " + doc.page_content

    all_docs = internal_docs + web_docs

    if not all_docs:
        return "❌ Je n’ai trouvé aucune information pertinente."

    # Nettoyage et fusion du contexte
    unique_contents = list(set(doc.page_content for doc in all_docs))
    context = "\n\n".join(unique_contents)

    prompt = generate_prompt()
    llm = HuggingFaceEndpoint(
        repo_id=HUGGINGFACE_REPO,
        temperature=0.5,
        max_new_tokens=512,
        huggingfacehub_api_token="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"
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run({"question": question, "context": context})

# === CLI
if __name__ == "__main__":
    q = input("❓ Pose ta question : ")
    r = answer_question(q, use_web=False)
    print("\n🤖 Réponse générée :\n", r)
