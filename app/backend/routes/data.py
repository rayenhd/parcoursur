from fastapi import APIRouter
from backend.services.data_services import upload_data, get_data

router = APIRouter()

@router.post("/upload")
def upload(file: str):
    """Upload un fichier vers Google Cloud Storage"""
    return upload_data(file)

@router.get("/download")
def download(file: str):
    """Télécharge un fichier depuis Google Cloud Storage"""
    return get_data(file)
