# reco.py (matching_engine.py corrigé)

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MatchingEngine:

    def __init__(self, vectorized_dataset_path: str):
        self.df = pd.read_pickle(vectorized_dataset_path)
        self.profil_vector = None
        self.liked_metier = set()
        self.disliked_metier = set()
        self.current_mode = "recommandation"  # par défaut
        

    def reset_profil(self):
        self.profil_vector = None
        self.liked_metier.clear()
        self.disliked_metier.clear()
        print("🔄 Profil utilisateur réinitialisé")
        self.current_mode = "recommandation"
 
    def dislike_metier(self, metier_id: int):
        print("idddddddd    ", metier_id)
        self.disliked_metier.add(metier_id)
        nom = self.df[self.df["id"] == metier_id]['nom'].values[0]
        print(f"👎 Métier '{nom}' rejeté")

    def like_metier(self, metier_id: int):
        vecteur = np.array(self.df[self.df["id"] == metier_id]['vector'].values[0]).reshape(1, -1)
        if self.profil_vector is None:
            self.profil_vector = vecteur
        else:
            total_likes = len(self.liked_metier)
            self.profil_vector = (self.profil_vector * total_likes + vecteur) / (total_likes + 1)
        #self.liked_metier.add(metier_id)
        nom = self.df[self.df["id"] == metier_id]['nom'].values[0]
        print(f"👍 Métier '{nom}' ajouté au profil")

    def get_recommendations(self, top_k=5, exploration_prob=0.1, liked=[]):
        print("###################################")
        liked_ids = list({m['id'] if isinstance(m, dict) else m.id for m in liked})
        print("Métier déjà likés :", liked)

        # Exclure les métiers likés (et potentiellement d'autres)
        excluded_metiers = liked_ids
        non_seen_df = self.df[~self.df['id'].isin(excluded_metiers)].copy()

        # Réinitialisation de l'index pour éviter les erreurs avec iloc
        non_seen_df = non_seen_df.reset_index(drop=True)

        # Cas où on n’a plus rien à recommander
        if self.profil_vector is None or len(non_seen_df) == 0:
            return non_seen_df.sample(n=min(top_k, len(non_seen_df)))

        # Calcul des similarités
        vectors = np.stack(non_seen_df['vector'].values)
        sims = cosine_similarity(self.profil_vector, vectors)[0]

        if np.random.rand() < exploration_prob:
            print("🎲 Mode Exploration activé")
            return non_seen_df.sample(n=min(top_k, len(non_seen_df)))
        else:
            print("💡 Mode Recommandation activé")
            top_indices = sims.argsort()[::-1][:top_k]
            return non_seen_df.iloc[top_indices]

# Exemple
if __name__ == "__main__":
    engine = MatchingEngine("vectorstore/jobinder/metiers_vect.pkl")
    engine.reset_profil()
    recommandations = engine.get_recommendations()
    print(recommandations[['id', 'nom', 'description_detaillee']])
