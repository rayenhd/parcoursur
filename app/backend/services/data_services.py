from utils.gcs_helper import upload_to_gcs, download_from_gcs

BUCKET_NAME = "mon-bucket-gcp"

def upload_data(file_path):
    return upload_to_gcs(BUCKET_NAME, file_path)

def get_data(file_path):
    return download_from_gcs(BUCKET_NAME, file_path)
