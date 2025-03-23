import os
import faiss
import pickle
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.tools import DuckDuckGoSearchRun
from langchain_huggingface import HuggingFaceEndpoint

# === Chargement des variables d'environnement ===
load_dotenv()

# === Configuration ===
VECTORSTORE_DIR = "vectorstore/chunks/"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
HUGGINGFACE_REPO = "meta-llama/Meta-Llama-3-8B-Instruct"
USE_WEB_SEARCH = False  # Active la recherche Web si besoin

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
            print(f"❌ Erreur dans {name}: {e}")
    return stores

# === Recherche interne ===
def get_relevant_documents(query: str, k=5) -> List[Document]:
    docs = []
    for store in load_all_vectorstores():
        try:
            docs += store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erreur dans un chunk : {e}")
    return docs[:k]

# === Recherche Web ===
def get_web_documents(query: str) -> List[Document]:
    results = web_search_tool.run(query)
    return [Document(page_content=results, metadata={"source": "web"})]

# === Prompt conversationnel structuré ===
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("system", "Tu es un assistant expert en orientation. Réponds uniquement à kla question sans ajouter d'autres éléments à la question. Tu aides les élèves à répondre à toutes leurs questions concernant les études, les filières, les écoles, les métiers, etc.Ne déforme jamais la question de l'utilisateur.\n\nVoici des extraits de documents internes ou issus du web :\n{context}\n\nVoici les derniers résultats que tu as donnés :\n{recent_results}\n\nSi les documents sont insuffisants, donne quand même une réponse utile basée sur tes connaissances et en français."),
    ("human", "{input}")
])

# === LLM Hugging Face ===
llm = HuggingFaceEndpoint(
    repo_id=HUGGINGFACE_REPO,
    temperature=0.5,
    max_new_tokens=512,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True,
    input_key="input",
    output_key="answer"  # Très important ici
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    output_key="answer"  # Et ici aussi
)

# === Fonction principale ===
def answer_question(question: str, use_web: bool = False) -> str:
    print(f"\n❓ Question : {question}")

    # Recherche dans les chunks vectorisés
    internal_docs = get_relevant_documents(question)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    # Recherche web si activée
    web_docs = []
    if use_web:
        print("🌐 Recherche Web activée")
        web_docs = get_web_documents(question)
        for doc in web_docs:
            doc.page_content = "[Web] " + doc.page_content

    # Fusion et formatage du contexte
    all_docs = internal_docs + web_docs
    context = "\n\n".join(set(doc.page_content for doc in all_docs))
    recent_results = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(all_docs)])

    # Appel à la chaîne avec les entrées attendues
    response = chain.invoke({
        "input": question,
        "context": context,
        "recent_results": recent_results
    })

    # Retourne la réponse textuelle du modèle
    return response.get("answer", "[Aucune réponse]")


# === CLI ===
if __name__ == "__main__":
    print("💬 Chatbot RAG conversationnel avec mémoire locale")
    while True:
        user_input = input("\nToi : ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Fin de la conversation.")
            break
        response = answer_question(user_input, use_web=USE_WEB_SEARCH)
        print("\n🤖 IA :", response)
