# Utiliser une image officielle Python
FROM python:3.10

# Définir le répertoire de travail
WORKDIR .

# Copier le fichier de dépendances et l’installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de l’application
COPY . .

# Exposer le port de Streamlit
EXPOSE 8501

# Démarrer l’application avec Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
