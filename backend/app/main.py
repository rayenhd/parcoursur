from fastapi import FastAPI
from app.routes import predict, chatbot, chatbot_tfidf  # Import des routes

app = FastAPI(title="Parcoursur AI API", description="API pour l'orientation scolaire")

# Inclure les routes
app.include_router(predict.router)
app.include_router(chatbot.router)
app.include_router(chatbot_tfidf.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de Parcoursur-AI"}
