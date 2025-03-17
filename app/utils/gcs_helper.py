from google.cloud import storage
import pickle

def connect_client():
    return storage.Client()

def upload_to_gcs(bucket_name, file_path):
    client = connect_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)

def download_from_gcs(bucket_name, file_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.download_to_filename(file_path)


def save_model_local(vectorizer, model, model_path=f"backend/models/generated_models/model.pkl"):
    """Sauvegarde le modèle et le vectorizer localement."""
    with open(model_path, "wb") as f:
        pickle.dump((vectorizer, model), f)
    print(f"Modèle sauvegardé localement à {model_path}")


def get_models_from_gcs(bucket_name, model_path):
    """Télécharge un modèle depuis GCS."""
    client = storage.Client()
    bucket_name = "your-bucket-name"
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="models/")  # Assuming your models are stored in a 'models/' directory
    models = [blob.name for blob in blobs if blob.name.endswith(".pkl")]
    return {"models": models}