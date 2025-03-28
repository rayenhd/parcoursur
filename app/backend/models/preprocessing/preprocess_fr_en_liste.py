import pandas as pd


df = pd.read_csv("data/source/fr-en-liste-diplomes-professionnels.csv", sep=";")

print("head : ", df.head())
df.drop_duplicates(inplace=True)

print("quelques infos sur le dataset : ", df.info())

print("nombre de valmeurs nulles : ", )

# 1. Renommer les colonnes
df.rename(columns={
    "Commission professionnelle consultative": "commission",
    "Secteur": "secteur",
    "Niveau": "niveau",
    "Code diplôme": "code_diplome",
    "Diplôme": "type_diplome",
    "Intitulé de la spécialité (et options)": "intitule",
    "Code RNCP": "code_rncp",
    "Date de l'arrêté de création": "date_creation",
    "Première session": "premiere_session",
    "Dernière session": "derniere_session",
    "Commentaire": "commentaire",
    "Famille de métiers": "famille_metier",
    "Session supplémentaire": "session_supplementaire"
}, inplace=True)

# 2. Fonction pour afficher les valeurs nulles
def print_missing_values(df):
    missing = df.isnull().sum()
    print("🔍 Valeurs nulles par colonne :")
    print(missing[missing > 0])

print_missing_values(df)

# 3. Traitement des colonnes avec valeurs nulles
df["famille_metier"].fillna("Non précisé", inplace=True)
df["commentaire"].fillna("", inplace=True)
df["session_supplementaire"].fillna("", inplace=True)
df["derniere_session"].fillna("", inplace=True)

# 4. Supprimer les lignes sans code RNCP
df.dropna(subset=["code_rncp"], inplace=True)

# 5. Créer une colonne texte pour la vectorisation RAG
df["texte"] = (
    "Type de diplôme : " + df["type_diplome"].astype(str) + "\n"
    + "Spécialité : " + df["intitule"].astype(str) + "\n"
    + "Niveau : " + df["niveau"].astype(str) + "\n"
    + "Commission : " + df["commission"].astype(str) + "\n"
    + "Secteur : " + df["secteur"].astype(str) + "\n"
    + "Famille de métier : " + df["famille_metier"]
)

# Aperçu final
print(df[["code_rncp", "texte"]].head())

# (optionnel) Export CSV
df[["code_rncp", "texte"]].to_csv("data/cleaned/fr-en-liste-diplomes-professionnels.csv", index=False)
