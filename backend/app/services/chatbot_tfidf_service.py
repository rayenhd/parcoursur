import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Charger le modèle TF-IDF sauvegardé
with open("./app/models/generated_models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Charger le dataset
df = pd.read_csv("./data/dataset_orientation_scolaire.csv")

# Vectorisation des questions du dataset
tfidf_matrix = vectorizer.transform(df["Question"])

def repondre_question_tfidf(question):
    """
    Trouve la réponse la plus pertinente dans le dataset en utilisant TF-IDF.
    """
    question_tfidf = vectorizer.transform([question])  # Vectoriser la question
    similarites = cosine_similarity(question_tfidf, tfidf_matrix)  # Calculer la similarité
    index_meilleure = similarites.argmax()  # Trouver la question la plus proche
    return df.iloc[index_meilleure]["Réponse"]  # Retourner la réponse correspondante
