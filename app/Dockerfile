FROM python:3.10

# Définir le répertoire de travail dans le conteneur
WORKDIR .

# Copier tous les fichiers du projet dans le répertoire de travail du conteneur
COPY . .

# Installer les dépendances à partir du fichier requirements.txt
RUN pip install -r requirements.txt

# Lancer Uvicorn avec l'option --reload pour le rechargement automatique lors des modifications de fichiers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
