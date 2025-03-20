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
df_formations.drop_duplicates(inplace=True)


# ❓ QUESTIONS-RÉPONSES
df_questions_reponses = df_questions_reponses.rename(columns={"Question": "question", "Réponse": "reponse"})
# print(df_questions_reponses.columns)

df_questions_reponses.dropna(subset=["question", "reponse"], inplace=True)

# 📚 FORMATIONS
df_formations = df_formations.rename(columns={
    "libelle_formation_principal": "nom_formation",
    "sigle_type_formation": "sigle_formation",
    "niveau_de_sortie_indicatif": "niveau_sortie",
    "code_rncp": "code_RNCP",
    "duree": "duree_formation",
    "tutelle": "tutelle_formation"
})

# print("formations valeurs nulles : ", df_formations.isnull().sum())
# print("diplome valeurs nulles : ", df_diplomes.isnull().sum())

df_formations = df_formations[["nom_formation", "sigle_formation", "niveau_sortie", "duree_formation", "code_RNCP", "tutelle_formation"]]
df_formations.dropna(subset=["nom_formation"], inplace=True)


# 📌 FUSION DES DONNÉES

# 🔄 Correction des types pour fusion
df_formations["code_RNCP"] = df_formations["code_RNCP"].astype(str)
df_diplomes["code_RNCP"] = df_diplomes["code_RNCP"].astype(str)
df_metiers["code_ROME"] = df_metiers["code_ROME"].astype(str)

# Vérifier si les codes RNCP existent dans les deux datasets
common_rncp = set(df_formations["code_RNCP"]) & set(df_diplomes["code_RNCP"])
# print(f"Nombre de codes RNCP communs : {len(common_rncp)}")
# print("Exemple de codes RNCP dans df_formations :", df_formations["code_RNCP"].unique()[:10])
# print("Exemple de codes RNCP dans df_diplomes :", df_diplomes["code_RNCP"].unique()[:10])


# print("infos   diplome ", df_diplomes.info())
# print("infos   metiers ", df_metiers.info())
# print("infos   etablissements ", df_etablissements.info())
# print("infos   questions_reponses ", df_questions_reponses.info())
# print("infos   formations ", df_formations.info())
# print(f"- Valeurs uniques dans df_formations : {df_formations['code_RNCP'].nunique()}")
# print(f"- Valeurs uniques dans df_diplomes : {df_diplomes['code_RNCP'].nunique()}")

# # 📂 Sauvegarde du fichier nettoyé
# df_formations_diplomes.to_csv("/mnt/data/cleaned_formation_diplome_fixed.csv", index=False, encoding="utf-8")

# 🛠 Convertir en string et supprimer le ".0" à la fin
df_formations["code_RNCP"] = df_formations["code_RNCP"].astype(str).str.replace(".0", "", regex=False)
df_diplomes["code_RNCP"] = df_diplomes["code_RNCP"].astype(str).str.replace(".0", "", regex=False)


df_rncp_formation = df_formations["code_RNCP"].dropna()
print("df_rncp_formation : ", df_rncp_formation.head())


common_rncp = set(df_formations["code_RNCP"]) & set(df_diplomes["code_RNCP"])
# print(f"Nombre de codes RNCP communs : {len(common_rncp)}")

# 🛠 Supprimer les valeurs "nan" générées par la conversion
df_formations["code_RNCP"] = df_formations["code_RNCP"].replace("nan", pd.NA)
df_diplomes["code_RNCP"] = df_diplomes["code_RNCP"].replace("nan", pd.NA)




# print("head df :     ", df_formations_diplomes.head())
# df_formations_diplomes.to_csv("data/cleaned/cleaned_formation_diplome.csv", index=False, encoding="utf-8")
# 🛠 Suppression de la colonne en double
# df_formations_diplomes.drop(columns=["sigle_formation.1"], inplace=True)


# 🔗 Fusion formations ⇄ métiers via domaine simplifié
# df_metiers["domaine_simplifie"] = df_metiers["domaine"].str.split("/").str[0]
# df_formations_diplomes["domaine_simplifie"] = df_formations_diplomes["nom_formation"].str.split().str[0]
# df_formations_metiers = df_formations_diplomes.merge(df_metiers, how="left", on="domaine_simplifie")

# 📍 Association formations ⇄ établissements via académie
# df_etablissements["academie"] = df_etablissements["academie"].astype(str)
# df_formations_metiers["academie"] = df_formations_metiers["tutelle_formation"].astype(str)
# df_etablissements_formations = df_formations_metiers.merge(df_etablissements, how="left", on="academie")

# 📌 Sélection des colonnes essentielles après fusion
# df_final = df_etablissements_formations[[
#     "nom_formation", "sigle_formation", "niveau_sortie", "duree_formation",
#     "nom_diplome", "niveau_diplome", "nom_metier", "libelle_ROME", "domaine",
#     "nom_etablissement", "type_etablissement", "statut_etablissement", "departement", "academie", "region"
# ]]

# Suppression des doublons et valeurs manquantes après correction
# print("Nombre de lignes dans df_final :", len(df_final))

# df_final.drop_duplicates(inplace=True)
# df_final.dropna(subset=["nom_formation", "nom_etablissement"], inplace=True)


# ✅ EXPORT DU FICHIER PRÉTRAITÉ
# df_final.to_csv("data/cleaned/cleaned_fusion.csv", index=False, encoding="utf-8")


# ✅ FIN DU PREPROCESSING
# print("✅ Preprocessing terminé, fichier prêt : cleaned_fusion.csv")
