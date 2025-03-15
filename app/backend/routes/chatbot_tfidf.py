# from fastapi import APIRouter, HTTPException
# from app.services.chatbot_tfidf_service import repondre_question_tfidf

# router = APIRouter()

# @router.get("/tfidf")
# async def chatbot_tfidf(question: str):
#     """
#     Route qui répond à une question en utilisant le modèle TF-IDF enregistré.
#     """
#     if not question:
#         raise HTTPException(status_code=400, detail="Veuillez fournir une question.")
    
#     reponse = repondre_question_tfidf(question)
#     return {"reponse": reponse}
