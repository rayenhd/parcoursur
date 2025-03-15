import os

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "mon-projet-gcp")
DATA_BUCKET_NAME = os.getenv("DATA_BUCKET_NAME", "parcoursur-data")
MODEL_BUCKET_NAME = os.getenv("MODEL_BUCKET_NAME", "parcoursur-models")
