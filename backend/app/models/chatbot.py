# 📝 Chatbot d'Orientation Scolaire avec NLTK et Transformers

# 📌 1. Importation des bibliothèques
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import pickle
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Télécharger les ressources NLTK nécessaires
nltk.download('punkt')
nltk.download('stopwords')

# 📌 2. Chargement du dataset
# Vous devez ajuster le chemin du dataset en fonction de votre structure de répertoires.
df = pd.read_csv("./data/dataset_orientation_scolaire.csv")

# Afficher les premières lignes du dataset
print(df.head())

# 📌 3. Nettoyage et Pré-traitement des questions

# Charger les stopwords français
stop_words = set(stopwords.words('french'))

# Fonction de nettoyage avec gestion d'erreur
def nettoyer_texte(texte):
    try:
        tokens = word_tokenize(texte.lower())  # Tokenisation avec NLTK
    except LookupError:
        tokens = texte.lower().split()  # Mode de secours en cas d'erreur

    tokens = [mot for mot in tokens if mot.isalnum() and mot not in stop_words]  # Suppression des stopwords et caractères spéciaux
    return " ".join(tokens)

# Test du nettoyage
texte_test = "Quels sont les débouchés après le Bac ?"
print(nettoyer_texte(texte_test))

# Appliquer le nettoyage sur l'ensemble du dataset
df["Question_clean"] = df["Question"].apply(nettoyer_texte)

# 🎯 Objectif : Trouver une Réponse à une Question avec TF-IDF
# Vectorisation TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df["Question_clean"])

def trouver_reponse(question):
    question_clean = nettoyer_texte(question)
    question_tfidf = vectorizer.transform([question_clean])
    similarites = cosine_similarity(question_tfidf, tfidf_matrix)
    index_meilleure = similarites.argmax()
    return df.iloc[index_meilleure]["Réponse"]

# Test du chatbot
question_utilisateur = "Comment devenir architect?"
print("Edu Pilot:", trouver_reponse(question_utilisateur))

question_utilisateur = "Qu'est ce que le métier d'orthophoniste?"
print("Edu Pilot:", trouver_reponse(question_utilisateur))

# 💾 Sauvegarde du Modèle Chatbot
with open("./app/models/generated_models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Modèle vectorizer enregistré dans 'vectorizer.pkl'")

# 7. Initialisation du modèle Transformer pré-entraîné
model_name = "microsoft/DialoGPT-small"  # Mets le nom du modèle que tu veux utiliser (ex : Mistral ou DialoGPT-small)

# Téléchargement et sauvegarde locale
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Sauvegarde en local
model.save_pretrained("./app/models/generated_models/chatbot_transformer_model")
tokenizer.save_pretrained("./app/models/generated_models/chatbot_transformer_model")

print("✅ Modèle et tokenizer sauvegardés en local dans 'chatbot_transformer_model/'")