import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Télécharger les ressources NLTK nécessaires
nltk.download('punkt')
nltk.download('stopwords')

# Charger les stopwords français
stop_words = set(stopwords.words('french'))

# 📌 1. Chargement du modèle Transformer
model_path = "./app/models/generated_models/chatbot_transformer_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# 📌 2. Fonction de nettoyage des questions
def nettoyer_texte(texte):
    try:
        tokens = word_tokenize(texte.lower())  # Tokenisation avec NLTK
    except LookupError:
        tokens = texte.lower().split()  # Mode de secours en cas d'erreur

    tokens = [mot for mot in tokens if mot.isalnum() and mot not in stop_words]  # Suppression des stopwords et caractères spéciaux
    return " ".join(tokens)

# 📌 3. Génération de réponse avec l'IA
def generer_reponse(question):
    """Utilise le modèle Transformer pour générer une réponse"""
    question_clean = nettoyer_texte(question)  # Nettoyage de la question
    input_ids = tokenizer.encode(question_clean, return_tensors="pt")

    # Génération de réponse avec le modèle IA
    output = model.generate(input_ids, max_length=150, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    return response
