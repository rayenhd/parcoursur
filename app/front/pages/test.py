# tinder_metiers.py (page streamlit du Tinder des métiers)

import streamlit as st
import pandas as pd
import sys
import os

# Import du moteur de matching
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from backend.models.jobinder.reco import MatchingEngine




# Initialisation
st.set_page_config(page_title="Tinder des Métiers", page_icon="🎯")
print("----------------- relance  ------------------")

# Initialisation du moteur et des variables d'état
if "engine" not in st.session_state:
    print("engin")
    st.session_state.engine = MatchingEngine("vectorstore/jobinder/metiers_vect.pkl")
    st.session_state.engine.reset_profil()
if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "liked_metiers" not in st.session_state:
    st.session_state.liked_metiers = set()
if "temp" not in st.session_state:
    st.session_state.temp = []


engine = st.session_state.engine

st.title("🎯 JobFinder")
st.markdown("Swipe à droite 👍 si tu aimes, à gauche 👎 si tu n'aimes pas")

# Affichage d'une recommandation
metiers = engine.get_recommendations(top_k=1, liked = st.session_state.temp[:-1])

if len(metiers) == 0:
    st.success("✅ Tu as parcouru tous les métiers ! Tu peux réinitialiser le profil.")
    if st.button("🔄 Recommencer"):
        engine.reset_profil()
        st.session_state.liked_metiers.clear()
        st.session_state.last_action = "reset"
        st.rerun()
else:
    metier = metiers.iloc[0]
    st.session_state.temp.append(metier)

    #print("le metier est     ,", st.session_state.temp)
    st.subheader(metier['nom'])
    st.markdown(f"**Description détaillée** : {metier['description_detaillee']}")
    st.markdown(f"**Salaire moyen** : {metier['salaire_moyen']} € brut/mois")
    st.markdown(f"**Niveau d'étude conseillé** : {metier['niveau_etude']}")
    st.markdown(f"[🔗 En savoir plus]({metier['lien_fiche_metier']})")

    col1, col2 = st.columns(2)
    with col1:
        metier = metier
        if st.button("👎 Je passe"):
            dislike = st.session_state.temp[-2]     
            del st.session_state.temp[-2]            
            engine.dislike_metier(dislike['id'])
            #st.session_state.last_action = "dislike"
            #st.rerun()

    with col2:
        if st.button("👍 J'aime"):
            #print("je passe en parametre : ", metier['id'])
            temp = st.session_state.temp[-2]
            engine.like_metier(temp['id'])
            st.session_state.liked_metiers.add(temp['id'])
            #st.session_state.last_action = "like"
            #st.rerun()

# Affichage de la liste de métiers aimés
st.subheader("⭐ Métiers que vous aimez déjà")
if st.session_state.liked_metiers:
    temps = st.session_state.temp[:-1]
    for elem in temps:
        metier = engine.df[engine.df["id"] == elem["id"]].iloc[0]
        st.markdown(f"- [{metier['nom']}]({metier['lien_fiche_metier']})")
else:
    st.markdown("Aucun métier liké pour le moment.")