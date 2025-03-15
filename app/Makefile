# Nom du projet GCP existant
PROJECT_ID=keskia

# Buckets déjà créés
DATA_BUCKET=parcoursur-data
MODELS_BUCKET=parcoursur-models
SERVICE_ACCOUNT_NAME=parcoursur-sa
SERVICE_ACCOUNT_EMAIL=$(SERVICE_ACCOUNT_NAME)@$(PROJECT_ID).iam.gserviceaccount.com
SERVICE_ACCOUNT_KEY=parcoursur-sa-key.json

# 📌 Créer le Service Account
create-service-account:
	@echo "🔹 Création du Service Account: $(SERVICE_ACCOUNT_NAME)"
	gcloud iam service-accounts create $(SERVICE_ACCOUNT_NAME) \
		--description="Service Account pour gérer $(PROJECT_ID)" \
		--display-name="parcoursur-service-account"

# 📌 Ajouter les rôles nécessaires
assign-roles:
	@echo "🔹 Attribution des rôles au Service Account..."
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SERVICE_ACCOUNT_EMAIL)" \
		--role="roles/editor"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SERVICE_ACCOUNT_EMAIL)" \
		--role="roles/storage.admin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SERVICE_ACCOUNT_EMAIL)" \
		--role="roles/logging.admin"

# 📌 Générer une clé JSON pour l’authentification
generate-key:
	@echo "🔹 Génération de la clé JSON pour $(SERVICE_ACCOUNT_NAME)..."
	gcloud iam service-accounts keys create $(SERVICE_ACCOUNT_KEY) \
		--iam-account=$(SERVICE_ACCOUNT_EMAIL)

# 📌 Configurer l’authentification avec le Service Account
auth-service-account:
	@echo "🔹 Authentification avec le Service Account..."
	export GOOGLE_APPLICATION_CREDENTIALS=$(SERVICE_ACCOUNT_KEY)
	gcloud auth activate-service-account --key-file=$(SERVICE_ACCOUNT_KEY)

# 📌 Vérifier l'authentification
check-auth:
	@echo "🔹 Vérification de l'authentification..."
	gcloud auth list

# 📌 Lister les buckets du projet
list-buckets:
	@echo "🔹 Listing des buckets sur GCP..."
	gcloud storage buckets list

# 📌 Supprimer le Service Account (⚠️ Attention !)
delete-service-account:
	@echo "⚠️ Suppression du Service Account: $(SERVICE_ACCOUNT_NAME)..."
	gcloud iam service-accounts delete $(SERVICE_ACCOUNT_EMAIL) --quiet

# 📌 Supprimer la clé d’authentification
delete-key:
	@echo "⚠️ Suppression de la clé JSON..."
	rm -f $(SERVICE_ACCOUNT_KEY)

# 📌 Commande pour tout configurer d'un coup
setup-service-account: create-service-account assign-roles generate-key auth-service-account check-auth list-buckets









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

# 📌 3️⃣ Gestion des données et modèles
upload-data:
	gcloud storage cp -r ./data gs://$(DATA_BUCKET)/

download-data:
	gcloud storage cp -r gs://$(DATA_BUCKET)/* ./data/

upload-models:
	gcloud storage cp -r ./backend/models gs://$(MODELS_BUCKET)/

download-models:
	gcloud storage cp -r gs://$(MODELS_BUCKET)/* ./backend/models/

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

upload-data:
	python infrastructure/upload_to_gcs.py

download-models:
	python infrastructure/download_from_gcs.py


