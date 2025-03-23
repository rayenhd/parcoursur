import faiss
import numpy as np
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
import pickle

# Chemin vers l'index FAISS
VECTOR_DB_PATH = "backend/models/vectorization/vectorstore/faiss_index.bin"

VECTOR_DB_PATH = "backend/models/vectorization/vectorstore/faiss_index.bin"
DOCSTORE_PATH = "backend/models/vectorization/vectorstore/docstore.pkl"
ID_MAPPING_PATH = "backend/models/vectorization/vectorstore/id_mapping.pkl"

def load_vectorstore():
    """Charge FAISS et le docstore associé."""
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Charger l'index FAISS
    index = faiss.read_index(VECTOR_DB_PATH)

    # Charger le docstore et l'index_to_docstore_id
    with open(DOCSTORE_PATH, "rb") as f:
        docstore = pickle.load(f)

    with open(ID_MAPPING_PATH, "rb") as f:
        index_to_docstore_id = pickle.load(f)

    vectorstore = FAISS(
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
        embedding_function=embedding_model
    )

    return vectorstore

def ask_faiss(question):
    """Recherche dans FAISS et affiche les documents trouvés."""
    vectorstore = load_vectorstore()
    
    # Encoder la question
    query_embedding = vectorstore.embedding_function.embed_query(question)
    
    # Recherche des 5 documents les plus proches
    k = 5
    distances, indices = vectorstore.index.search(np.array([query_embedding], dtype=np.float32), k)

    print("🔍 Documents les plus pertinents :")
    for i, idx in enumerate(indices[0]):
        print(f"{i+1}. Document {idx} - Distance: {distances[0][i]}")

    # Récupération des documents
    retrieved_docs = [vectorstore.docstore.search(str(idx)) for idx in indices[0]]

    print("\n📜 Contenu des documents récupérés :")
    for i, doc in enumerate(retrieved_docs):
        if doc:
            print(f"{i+1}. {doc}\n")
        else:
            print(f"{i+1}. Document {indices[0][i]} introuvable ❌\n")

    return retrieved_docs

if __name__ == "__main__":
    query = input("Pose ta question : ")
    response = ask_faiss(query)