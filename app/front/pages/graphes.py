import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Métiers & Formations", layout="wide")

# Chargement des données avec cache
@st.cache_data
def load_data():
    metiers = pd.read_csv('data/cleaned/cleaned_metiers.csv')
    formations = pd.read_csv('data/cleaned/cleaned_formations.csv')
    return metiers, formations

metiers, formations = load_data()

st.title("📊 Taux de Redoublement et de Réorientation en Bac +1")

# Données
data = {
    "Filière": ["Licence", "BTS", "CPGE"],
    "Redoublement (%)": [30, 20, 5],
    "Réorientation (%)": [15, 10, 5]
}
df = pd.DataFrame(data)

# Graphique en barres pour le redoublement
fig_redoublement = px.bar(
    df,
    x="Filière",
    y="Redoublement (%)",
    title="Taux de Redoublement en Première Année",
    labels={"Redoublement (%)": "Taux de Redoublement (%)"},
    color="Filière"
)
st.plotly_chart(fig_redoublement, use_container_width=True)

# Graphique en barres pour la réorientation
fig_reorientation = px.bar(
    df,
    x="Filière",
    y="Réorientation (%)",
    title="Taux de Réorientation après la Première Année",
    labels={"Réorientation (%)": "Taux de Réorientation (%)"},
    color="Filière"
)
st.plotly_chart(fig_reorientation, use_container_width=True)

st.title("🎓 Dashboard Métiers & Formations")

# Section Métiers
st.header("🔨 Métiers")

# Graphique : Nombre de métiers par domaine
metiers['domaine_principal'] = metiers['domaine'].apply(lambda x: x.split('/')[0].strip())
metiers_domaine_counts = metiers['domaine_principal'].value_counts().reset_index()
metiers_domaine_counts.columns = ['domaine_principal', 'count']

fig_metiers_domaine = px.bar(
    metiers_domaine_counts,
    x='domaine_principal',
    y='count',
    labels={'domaine_principal': 'Domaine', 'count': 'Nombre de métiers'},
    title='Nombre de métiers par domaine'
)
st.plotly_chart(fig_metiers_domaine, use_container_width=True)

# Tableau interactif des métiers
domaine_selectionne = st.selectbox("Filtrer par domaine principal :", metiers['domaine_principal'].unique())
filtered_metiers = metiers[metiers['domaine_principal'] == domaine_selectionne]
st.dataframe(filtered_metiers[['nom_metier', 'libelle_ROME', 'domaine']])

# Section Formations
st.header("📖 Formations")

# Pie chart : Niveau des formations inscrites au RNCP
formations_rncp = formations[formations['niveau_certification'] != 'non inscrit au RNCP']
fig_formations_rncp = px.pie(
    formations_rncp,
    names='niveau_certification',
    title='Répartition des formations par niveau RNCP'
)
st.plotly_chart(fig_formations_rncp, use_container_width=True)

# Tableau interactif des formations
niveau_etude_selectionne = st.selectbox("Filtrer par niveau d'étude :", formations['niveau_etude'].unique())
filtered_formations = formations[formations['niveau_etude'] == niveau_etude_selectionne]
st.dataframe(filtered_formations[['nom_formation', 'type_formation', 'niveau_etude', 'ministere_tutelle']])
