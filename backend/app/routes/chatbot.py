from fastapi import APIRouter
from app.services.chatbot_service import generer_reponse

router = APIRouter()

@router.post("/chatbot")
def chatbot_endpoint(question: str):
    """Endpoint pour interagir avec l'IA"""
    try:
        reponse = generer_reponse(question)
        return {"reponse": reponse}
    except Exception as e:
        return {"erreur": str(e)}
