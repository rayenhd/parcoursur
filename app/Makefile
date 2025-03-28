# Nom du projet GCP existant
PROJECT_ID=keskia

# Buckets déjà créés
DATA_BUCKET=parcoursur_data
VECTORSTORE_BUCKET=parcoursur_vectorized_data
MODELS_BUCKET=parcoursur_models

DATA_DIR=data/
MODELS_DIR=backend/models/generated_models/
VECTORSTORE_DIR=vectorstore/chunks/


HUGGING_FACE = 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


# 📌 Lister les buckets du projet
list-buckets:
	@echo "🔹 Listing des buckets sur GCP..."
	gcloud storage buckets list


# ---------------- Uploading data ----------------
# 📌 Uploader les données sur GCS

upload-data:
	gsutil -m cp -r $(DATA_DIR)* gs://$(DATA_BUCKET)/

upload-data-source:
	gsutil -m cp -r $(DATA_DIR)source/* gs://$(DATA_BUCKET)/source/

upload-data-source-file:
	gsutil -m cp -r $(DATA_DIR)source/$(file) gs://$(DATA_BUCKET)/source/$(file)

upload-data-cleaned-file:
	gsutil -m cp -r $(DATA_DIR)cleaned/$(file) gs://$(DATA_BUCKET)/cleaned/$(file)


upload-data-cleaned:
	gsutil -m cp -r $(DATA_DIR)cleaned/* gs://$(DATA_BUCKET)/cleaned/


override-data:
	gsutil -m rm -r gs://$(DATA_BUCKET)/**
	gsutil -m cp -r $(DATA_DIR)/* gs://$(DATA_BUCKET)/

override-data-source:
	gsutil -m rm -r gs://$(DATA_BUCKET)/source/**
	gsutil -m cp -r $(DATA_DIR)source/* gs://$(DATA_BUCKET)/source/

override-data-cleaned:
	gsutil -m rm -r gs://$(DATA_BUCKET)/cleaned/**
	gsutil -m cp -r $(DATA_DIR)cleaned/* gs://$(DATA_BUCKET)/cleaned/


download-data:
	gsutil -m cp -r gs://$(DATA_BUCKET)/* $(DATA_DIR)

download-data-source:	
	gsutil -m cp -r gs://$(DATA_BUCKET)/source/* $(DATA_DIR)source

download-data-cleaned:	
	gsutil -m cp -r gs://$(DATA_BUCKET)/cleaned/* $(DATA_DIR)cleaned


#-------------------- Vectorstore part ---------------------------
upload-vectorstore:
	gsutil rm gs://$(VECTORSTORE_BUCKET)/chunks/hash_log.json
	gsutil -m cp -r $(VECTORSTORE_DIR)* gs://$(VECTORSTORE_BUCKET)/vectorstore

upload-vectorstore-file:
	gsutil rm gs://$(VECTORSTORE_BUCKET)/chunks/hash_log.json
	gsutil -m cp -r vectorstore/chunks/hash_log.json gs://$(VECTORSTORE_BUCKET)/chunks/hash_log.json
	gsutil -m cp -r vectorstore/chunks/$(file) gs://$(VECTORSTORE_BUCKET)/chunks/$(file)

upload-vectorstore-logs:
	gsutil rm gs://$(VECTORSTORE_BUCKET)/chunks/hash_log.json
	gsutil -m cp -r vectorstore/chunks/hash_log.json gs://$(VECTORSTORE_BUCKET)/chunks/hash_log.json


download-vectorstore:
	gsutil -m cp -r gs://$(VECTORSTORE_BUCKET)/* $(VECTORSTORE_DIR)





# ---------------- Uploading models ----------------
upload-models:
	gsutil -m cp -r $(MODELS_DIR)* gs://$(MODELS_BUCKET)/



download-models:
	gsutil -m cp -r gs://$(MODELS_BUCKET)/* $(MODELS_DIR)

upload-models:
	gsutil -m cp -r $(MODELS_DIR)* gs://$(MODELS_BUCKET)/



exporting-hugging:
	export HUGGINGFACEHUB_API_TOKEN=$(HUGGING_FACE)



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


