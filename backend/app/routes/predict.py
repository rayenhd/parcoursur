from fastapi import APIRouter
import joblib
import numpy as np
import os

# Création du router pour les prédictions
router = APIRouter()

# Charger le modèle IA
model_path = os.path.join(os.path.dirname(__file__), "../models/vectorizer.pkl")
model = joblib.load(model_path)
@router.post("/predict/")
async def predict(data: dict):
    """
    Endpoint pour faire une prédiction avec l'IA.
    """
    try:
        input_data = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(input_data)
        return {"prediction": prediction.tolist()}
    
    except Exception as e:
        return {"error": str(e)}
