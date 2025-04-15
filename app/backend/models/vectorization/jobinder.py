# vectorizer.py

import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class MetierVectorizer:

    def __init__(self, csv_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.csv_path = csv_path
        self.model = SentenceTransformer(model_name)

    def load_data(self):
        self.df = pd.read_csv(self.csv_path)
        print(f"✅ {len(self.df)} métiers chargés depuis {self.csv_path}")

    def vectorize_metiers(self):
        print("🔄 Vectorisation en cours...")
        textes = (
            self.df["nom"].fillna('').astype(str) + " " +
            self.df["description_detaillee"].fillna('').astype(str) + " " +
            self.df["salaire_moyen"].fillna('').astype(str) + " " +
            self.df["niveau_etude"].fillna('').astype(str)
        )
    
        self.df["vector"] = list(tqdm(self.model.encode(textes.tolist(), show_progress_bar=True)))
        print("✅ Vectorisation terminée")

    def save_vectors(self, output_path: str):
        self.df.to_pickle(output_path)
        print(f"💾 Vecteurs sauvegardés dans {output_path}")

# Exemple d'utilisation
if __name__ == "__main__":
    vectorizer = MetierVectorizer(csv_path="data/cleaned/cleaned_metiers_jobinder.csv")
    vectorizer.load_data()
    vectorizer.vectorize_metiers()
    vectorizer.save_vectors("vectorstore/jobinder/metiers_vect.pkl")

