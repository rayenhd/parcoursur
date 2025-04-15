import pandas as pd
import re

df = pd.read_csv("data/source/metiers_enrichis_sample.csv")


print("head   :   ", df.info())


def print_missing_values(df):
    missing = df.isnull().sum()
    print("🔍 Valeurs nulles par colonne :")
    print(missing[missing > 0])

print_missing_values(df)

verbes = [
    "conçoit", "fabrique", "adapte", "entretient", "négocie", "effectue", "accompagne",
    "travaille", "répare", "organise", "réalise", "gère", "assure", "prépare",
    "développe", "participe", "aide", "analyse", "est", "supervise", "crée", "dirige",
    "veille", "propose", "contrôle", "étudie", "installe", "vend", "s'occupe", "informe",
    "anime", "rédige", "enseigne", "définit", "coordonne", "produit", "procède",
    "apporte", "intervient", "pilote", "se charge", "met en œuvre", "élabore",
    "encadre", "dispense", "vérifie", "maîtrise", "diagnostique", "se consacre",
    "s'investit", "évalue", "sélectionne", "programme", "traite", "assiste",
    "fournit", "offre", "reçoit", "exerce", "répond", "accomplit", "délivre",
    "pratique", "suit", "administre", "établit", "calcule", "présente", "prend",
    "consulte", "audite", "acquiert", "sollicite",
    # Ajoute ici d'autres verbes que tu rencontres
    "prévoit", "utilise", "transmet", "protège", "collecte", "seconde", "conseille", "pose",
    "transporte", "garde", "assemble", "prodigue", "décore", "usine", "décore", "imagine",
    "imagine", "applique", "aménage", "manœuvre", "découpe", "façonne", "capte", "stérilise",
    "sécurise", "teste", "monte", "optimise", "mesure", "ajuste", "sculpte", "restaure", "relie",
    "rééduque", "joue", "habille", "approvisionne", "conduit", "capture", "nettoie", "améliore",
    "confectionne", "corrige", "écrit", "patrouille", "traduit", "forme", "fixe", "met", "élève",
    "garantit", "filme", "interprète", "cultive", "régule", "soigne", "partage", "guide", "fait",
    "enregistre", "coupe", "taille", "construit", "écoute", "compose", "sensibilise", "taille",  "prospecte",
    "manipule", "accueille", "authentifie", "dépiste", "compose", "sensibilise", "écoute", "identifie", "construit",
    "taille", "garnit", "oriente"
]


#vérifier ligne 34, 2, 104, 114

# Fonction d'extraction robuste corrigée
def extraire_nom_metier(description):
    # Verbes séparés par des "|" (ou), échappés correctement
    pattern = fr"(?:[Ll][e']\s?)?(.*?)(?=\s(?:{'|'.join(map(re.escape, verbes))}))"
    match = re.match(pattern, description, re.IGNORECASE)
    if match:
        return match.group(1).strip(" ,.'\"")
    return None


# Application de la fonction à chaque description
df.insert(1, 'nom', df['description_detaillee'].apply(extraire_nom_metier))
df['salaire_moyen'] = df['salaire_moyen'].astype(str)
print(df.info())
# Affichage du résultat pour vérifier
#print(df[['id', 'nom']].head())

def analyse_doublons(df):
    # Compter le nombre d'occurrences de chaque nom
    counts = df['nom'].value_counts()
    
    # Sélectionner uniquement les noms qui apparaissent plus d'une fois
    doublons = counts[counts > 1]
    
    # Calculer le nombre total de doublons
    total_doublons = (counts[counts > 1] - 1).sum()
    
    # Remettre sous forme de DataFrame propre
    df_doublons = doublons.reset_index()
    df_doublons.columns = ['nom', 'nb_occurrences']

    


    return df_doublons, total_doublons

# Exemple d'utilisation :
# df = pd.read_csv("ton_fichier.csv")
df_doublons, total_doublons = analyse_doublons(df)

print("Détails des doublons :")
print(df_doublons)
print("\nNombre total de doublons :", total_doublons)

df = df.drop_duplicates(subset=['nom'], keep='first')
df.reset_index(drop=True, inplace=True)
df['nom'] = df['nom'].str.upper()
df['id'] = df.index


df.to_csv("data/cleaned/cleaned_metiers_jobinder.csv", index=False)
