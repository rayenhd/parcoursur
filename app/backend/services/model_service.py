from google.cloud import storage
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_BUCKET_NAME

client = storage.Client()

def download_model(model_name, local_dir):
    """Télécharge un modèle depuis GCP et le stocke localement"""
    bucket = client.bucket(MODEL_BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=f"{model_name}/"))
    
    for blob in blobs:
        blob.download_to_filename(f"{local_dir}/{blob.name.split('/')[-1]}")
        print(f"Téléchargé : {blob.name}")

def load_model(model_path):
    """Charge un modèle de Transformers depuis le stockage local"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    return tokenizer, model
