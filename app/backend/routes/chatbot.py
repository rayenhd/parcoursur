from fastapi import APIRouter
from backend.services.chatbot_service import generate_response

router = APIRouter()

@router.get("/ask")
def ask_chatbot(question: str):
    """Endpoint qui génère une réponse du chatbot"""
    return {"response": generate_response(question)}
