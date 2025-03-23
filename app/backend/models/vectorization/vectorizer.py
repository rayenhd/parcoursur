import os
import hashlib
import pickle
import pandas as pd
import numpy as np
import faiss
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
import json

# === Config ===
CLEANED_DIR = "data/cleaned/"
TESTING_DIR = "data/test/"
CHUNKS_DIR = "vectorstore/chunks/"
HASH_LOG_PATH = os.path.join(CHUNKS_DIR, "hash_log.json")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# Assure les dossiers existent
os.makedirs(TESTING_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)

# === Outils ===

def compute_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_hash_log():
    if os.path.exists(HASH_LOG_PATH):
        with open(HASH_LOG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_hash_log(log):
    with open(HASH_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

def read_texts_from_file(file_path):
    texts = []
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            texts = f.read().splitlines()
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        if "texte" in df.columns:
            texts = df["texte"].astype(str).tolist()
        else:
            for _, row in df.iterrows():
                texts.append(" ".join(row.astype(str)))
    return texts

def vectorize_file(filename, file_path, output_dir):
    print(f"🔁 Vectorisation de {filename}...")

    texts = read_texts_from_file(file_path)
    documents = [Document(page_content=text) for text in texts]

    embedding_model = SentenceTransformerEmbeddings(model_name=EMBED_MODEL_NAME)
    embeddings = embedding_model.embed_documents([doc.page_content for doc in documents])

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings).astype(np.float32))

    index_to_docstore_id = {i: str(i) for i in range(len(documents))}
    docstore = InMemoryDocstore({str(i): documents[i] for i in range(len(documents))})

    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(output_dir, "faiss_index.bin"))
    with open(os.path.join(output_dir, "docstore.pkl"), "wb") as f:
        pickle.dump(docstore, f)
    with open(os.path.join(output_dir, "id_mapping.pkl"), "wb") as f:
        pickle.dump(index_to_docstore_id, f)

    print(f"✅ Vectorisation de `{filename}` terminée et sauvegardée dans `{output_dir}`.")

# === Main ===

def vectorize_all():
    hash_log = load_hash_log()
    updated_log = {}

    for file in os.listdir(TESTING_DIR):
        if not file.endswith((".txt", ".csv")):
            continue

        file_path = os.path.join(TESTING_DIR, file)
        file_hash = compute_file_hash(file_path)

        if file in hash_log and hash_log[file] == file_hash:
            print(f"✅ `{file}` inchangé — ignoré.")
            updated_log[file] = file_hash
            continue

        # Nom du dossier de sortie = nom du fichier sans extension
        dataset_name = os.path.splitext(file)[0]
        output_dir = os.path.join(CHUNKS_DIR, dataset_name)
        vectorize_file(file, file_path, output_dir)

        updated_log[file] = file_hash

    save_hash_log(updated_log)

if __name__ == "__main__":
    vectorize_all()
