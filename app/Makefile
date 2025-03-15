# Nom du projet GCP existant
PROJECT_ID=keskia

# Buckets déjà créés
DATA_BUCKET=parcoursur_data
DATA_DIR=data/

MODELS_BUCKET=parcoursur_models
MODELS_DIR=backend/models/generated_models/
SERVICE_ACCOUNT_NAME=parcoursur-sa
SERVICE_ACCOUNT_EMAIL=$(SERVICE_ACCOUNT_NAME)@$(PROJECT_ID).iam.gserviceaccount.com
SERVICE_ACCOUNT_KEY=parcoursur-sa-key.json


# 📌 Lister les buckets du projet
list-buckets:
	@echo "🔹 Listing des buckets sur GCP..."
	gcloud storage buckets list


upload-data:
	gsutil -m cp -r $(DATA_DIR)* gs://$(DATA_BUCKET)/

upload-models:
	gsutil -m cp -r $(MODELS_DIR)* gs://$(MODELS_BUCKET)/

download-data:
	gsutil -m cp -r gs://$(DATA_BUCKET)/* $(DATA_DIR)

download-models:
	gsutil -m cp -r gs://$(MODELS_BUCKET)/* $(MODELS_DIR)


# 📌 1️⃣ Connexion au projet GCP
login:
	gcloud auth application-default login

set-project:
	gcloud config set project $(PROJECT_ID)


connect_project: login set-project


auth-check:
	gcloud auth list

# 📌 2️⃣ Vérifier les buckets existants
list-buckets:
	gcloud storage buckets list

# # 📌 3️⃣ Gestion des données et modèles
# upload-data:
# 	gcloud storage cp -r ./data gs://$(DATA_BUCKET)/

# download-data:
# 	gcloud storage cp -r gs://$(DATA_BUCKET)/* ./data/

# upload-models:
# 	gcloud storage cp -r ./backend/models gs://$(MODELS_BUCKET)/

# download-models:
# 	gcloud storage cp -r gs://$(MODELS_BUCKET)/* ./backend/models/

# 📌 4️⃣ Lancer l'application avec Docker
run:
	docker build -t parcoursur-app .
	docker run -p 8000:8000 -p 3000:3000 parcoursur-app

# 📌 5️⃣ Déploiement sur Cloud Run
deploy:
	docker build -t gcr.io/$(PROJECT_ID)/parcoursur-app .
	docker push gcr.io/$(PROJECT_ID)/parcoursur-app
	gcloud run deploy parcoursur-app \
		--image gcr.io/$(PROJECT_ID)/parcoursur-app \
		--platform managed \
		--region us-central1 \
		--allow-unauthenticated



run:
	docker-compose up --build

# upload-data:
# 	python infrastructure/upload_to_gcs.py

# download-models:
# 	python infrastructure/download_from_gcs.py


