# 📌 IMPORTS
import pandas as pd

# 📂 CHARGEMENT DES FICHIERS
files = {
    "etablissements": "data/source/data_info_ecoles.csv",
    "metiers": "data/source/data_metiers.csv",
    "diplomes": "data/source/data_diplomes.csv",
    "questions_reponses": "data/source/data_questions_reponses.csv",
    "formations": "data/source/data_formation.csv"
}

df_etablissements = pd.read_csv(files["etablissements"], sep=";", encoding="utf-8")
df_metiers = pd.read_csv(files["metiers"], sep=";", encoding="utf-8")
df_diplomes = pd.read_csv(files["diplomes"], sep=";", encoding="utf-8")
df_questions_reponses = pd.read_csv(files["questions_reponses"], sep=",", encoding="utf-8")
df_formations = pd.read_csv(files["formations"], sep=",", encoding="utf-8")
# print(df_formations.columns)


# 📌 NETTOYAGE DES DONNÉES

# 🏫 ÉTABLISSEMENTS
df_etablissements = df_etablissements.rename(columns={
    "code UAI": "code_UAI",
    "nom": "nom_etablissement",
    "type d'établissement": "type_etablissement",
    "statut": "statut_etablissement",
    "département": "departement",
    "académie": "academie",
    "région": "region"
})
df_etablissements = df_etablissements[["code_UAI", "nom_etablissement", "type_etablissement", 
                                       "statut_etablissement", "departement", "academie", "region"]]
df_etablissements.dropna(subset=["code_UAI", "nom_etablissement"], inplace=True)

# 👨‍💼 MÉTIERS
df_metiers = df_metiers.rename(columns={
    "libellé métier": "nom_metier",
    "code ROME": "code_ROME",
    "libellé ROME": "libelle_ROME",
    "domaine/sous-domaine": "domaine"
})
df_metiers = df_metiers[["nom_metier", "code_ROME", "libelle_ROME", "domaine"]]
df_metiers.dropna(subset=["nom_metier", "code_ROME"], inplace=True)

# 🎓 DIPLÔMES
df_diplomes = df_diplomes.rename(columns={
    "CI Intitulé type diplôme": "type_diplome",
    "CI Intitulé": "nom_diplome",
    "CI Niveau européen": "niveau_diplome",
    "CI Code RNCP": "code_RNCP"
})
df_diplomes = df_diplomes[["type_diplome", "nom_diplome", "niveau_diplome", "code_RNCP"]]
df_diplomes.dropna(subset=["nom_diplome"], inplace=True)
df_diplomes.drop_duplicates(inplace=True)


# ❓ QUESTIONS-RÉPONSES
df_questions_reponses = df_questions_reponses.rename(columns={"Question": "question", "Réponse": "reponse"})
# print(df_questions_reponses.columns)

df_questions_reponses.dropna(subset=["question", "reponse"], inplace=True)


# print("formations valeurs nulles : ", df_formations.isnull().sum())
# print("diplome valeurs nulles : ", df_diplomes.isnull().sum())

# df_formations = df_formations[["nom_formation", "sigle_formation", "niveau_sortie", "duree_formation", "code_RNCP", "tutelle_formation"]]
# df_formations.dropna(subset=["nom_formation"], inplace=True)


# 📌 FUSION DES DONNÉES

# 🔄 Correction des types pour fusion
# df_formations["code_RNCP"] = df_formations["code_RNCP"].astype(str)
df_diplomes["code_RNCP"] = df_diplomes["code_RNCP"].astype(str)
df_metiers["code_ROME"] = df_metiers["code_ROME"].astype(str)


print("nombre de valeurs nulles dans les formations : ", df_formations.isnull().sum())
print("nombre de valeurs nulles dans les diplomes : ", df_diplomes.isnull().sum())
print("nombre de valeurs nulles dans les metiers : ", df_metiers.isnull().sum())
print("nombre de valeurs nulles dans les etablissements : ", df_etablissements.isnull().sum())



# ----------------------- Formation -----------------------

# Sélectionner uniquement les colonnes pertinentes
columns_to_keep = [
    "libelle_type_formation", "libelle_formation_principal",
    "duree", "niveau_de_sortie_indicatif", "libelle_niveau_de_certification",
    "tutelle", "url_et_id_onisep", "domainesous-domaine", "code_rncp"
]
df_cleaned = df_formations[columns_to_keep].copy()

# Renommer les colonnes pour plus de clarté
df_cleaned.rename(columns={
    "libelle_type_formation": "type_formation",
    "libelle_formation_principal": "nom_formation",
    "duree": "duree",
    "niveau_de_sortie_indicatif": "niveau_etude",
    "libelle_niveau_de_certification": "niveau_certification",
    "tutelle": "ministere_tutelle",
    "url_et_id_onisep": "lien_onisep",
    "domainesous-domaine": "domaine",
    "code_rncp": "code_rncp"
}, inplace=True)

# Supprimer les doublons
df_cleaned.drop_duplicates(inplace=True)

# Remplacer les valeurs nulles ou manquantes
df_cleaned.fillna({
    "type_formation": "Non renseigné",
    "nom_formation": "Non renseigné",
    "duree": "Non renseigné",
    "niveau_etude": "Non renseigné",
    "niveau_certification": "Non renseigné",
    "ministere_tutelle": "Non renseigné",
    "lien_onisep": "Non renseigné",
    "domaine": "Non renseigné",
    "code_rncp": "Non renseigné"
}, inplace=True)

# Supprimer les espaces inutiles et uniformiser les valeurs textuelles
df_cleaned = df_cleaned.applymap(lambda x: x.strip() if isinstance(x, str) else x)

df_cleaned.to_csv("data/cleaned/cleaned_formations.csv", index=False, encoding="utf-8")
df_diplomes.to_csv("data/cleaned/cleaned_diplomes.csv", index=False, encoding="utf-8")
df_metiers.to_csv("data/cleaned/cleaned_metiers.csv", index=False, encoding="utf-8")
df_etablissements.to_csv("data/cleaned/cleaned_etablissements.csv", index=False, encoding="utf-8")

# # Ajouter une indication sur la reconnaissance de l'État en fonction du RNCP
# df_cleaned["reconnaissance_etat"] = df_cleaned["code_rncp"].apply(
#     lambda x: "Oui" if x != "Non renseigné" else "Non"
# )

# # Fusionner toutes les informations en un texte unique par ligne
# df_cleaned["texte"] = df_cleaned.apply(lambda row: f"{row['nom_formation']} est une formation de type {row['type_formation']} qui dure {row['duree']}. "
#                                                    f"Elle correspond au niveau d'étude {row['niveau_etude']} et au niveau de certification {row['niveau_certification']}. "
#                                                    f"Cette formation est sous la tutelle de {row['ministere_tutelle']} et appartient au domaine {row['domaine']}. "
#                                                    f"RNCP : {row['code_rncp']} (Reconnue par l'État : {row['reconnaissance_etat']}). "
#                                                    f"Plus d'informations disponibles ici : {row['lien_onisep']}.", axis=1)

# # Sauvegarde en format texte
# cleaned_text_file_rncp_fixed = "cleaned_formations_rncp_fixed.txt"
# df_cleaned[["texte"]].to_csv(cleaned_text_file_rncp_fixed, index=False, header=False, sep="\n")

# # Sauvegarde en format CSV
# cleaned_csv_file_rncp_fixed = "cleaned_formations_rncp_fixed.csv"
# df_cleaned.to_csv(cleaned_csv_file_rncp_fixed, index=False, encoding="utf-8")

# print(f"✅ Fichiers nettoyés enregistrés sous :\n📂 {cleaned_text_file_rncp_fixed}\n📂 {cleaned_csv_file_rncp_fixed}")
