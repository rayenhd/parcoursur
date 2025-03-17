import os
import pickle
from google.cloud import storage

# from config.settings import get_settings

MODEL_DIR = "backend/models/generated_models"
BUCKET_MODELS = "nom-de-ton-bucket-gcs"
BUCKET_MODELS = "parcoursur_models"


def download_model(model_name: str):
    """Télécharge un modèle depuis GCS et le stocke localement."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_MODELS)
    blob = bucket.blob(f"{model_name}.pkl")
    
    local_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    blob.download_to_filename(local_path)
    print(f"✅ Modèle {model_name} téléchargé depuis GCS.")

def load_model(model_name: str):
    """Charge un modèle en mémoire."""
    full_path = MODEL_DIR + f"/{model_name}"
    model_path = os.path.join(full_path)
    print("medddleeeeeeeee", model_path)
    print("nameeeeeeee", model_name)

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    print(f"✅ Modèle {model_name} chargé en mémoire.")
    return model

def get_models_from_gcs():
    """Télécharge un modèle depuis GCS."""
    client = storage.Client()
    bucket_name = "your-bucket-name"
    bucket = client.bucket(BUCKET_MODELS)
    blobs = bucket.list_blobs()  # Assuming your models are stored in a 'models/' directory
    models = [blob.name for blob in blobs if blob.name.endswith(".pkl")]
    return {"models": models}