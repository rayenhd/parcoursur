# Indique que "backend" est un module Python
from fastapi import FastAPI

app = FastAPI()

from backend.routes import chatbot, data

app.include_router(chatbot.router)
app.include_router(data.router)
