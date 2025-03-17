from fastapi import FastAPI
from backend.routes import chatbot

app = FastAPI()

app.include_router(chatbot.router, prefix="/api/chatbot")
# app.include_router(chatbot_tfidf.router, prefix="/api/data")

@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API Parcoursur"}
