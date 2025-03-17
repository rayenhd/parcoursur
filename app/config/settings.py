import os
from dotenv import load_dotenv

load_dotenv()

GCP_BUCKET_NAME = os.getenv("parcoursur_models")
GCP_MODEL_BUCKET = os.getenv("GCP_MODEL_BUCKET")
BUCKET_MODELS = "parcoursur_models"
