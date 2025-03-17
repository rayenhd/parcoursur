from fastapi import APIRouter, HTTPException
from backend.services.model_loader import load_model, get_models_from_gcs
from typing import List, Dict
import pickle
from backend.models.chatbot import nettoyer_texte, trouver_reponse

router = APIRouter()

with open("backend/models/generated_models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Endpoint pour tester si l'API fonctionne
@router.get("/health")
def health_check():
    return {"status": "API is running"}

# Endpoint pour récupérer la liste des modèles disponibles
@router.get("/models")
def list_models():
    return get_models_from_gcs()  # À remplacer par un fetch depuis GCS


@router.post("/chatbot/vectorize")
def vectorize_question(question: str):
    # Transformer la question en vecteur TF-IDF
    cleaned_question = nettoyer_texte(question)
    question_tfidf = vectorizer.transform([cleaned_question]).toarray().tolist()

    return {"vector": question_tfidf}


# Endpoint pour poser une question à l'IA
@router.post("/chatbot/ask")
def ask_question(question : str):
    return trouver_reponse(question)




# Endpoint pour continuer une conversation
# @router.post("/chatbot/conversation")
# def continue_conversation(payload: Dict[str, List[Dict[str, str]]]):
#     conversation = payload.get("conversation")
#     model_name = payload.get("model_name")
#     if not conversation or not model_name:
#         raise HTTPException(status_code=400, detail="Missing conversation history or model_name")
    
#     model = load_model(model_name)
#     response = predict(model, conversation)
#     return {"response": response}
