import streamlit as st
import pandas as pd
import sys
import os
import base64

# Import du moteur de matching
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from backend.models.jobinder.reco import MatchingEngine

st.set_page_config(page_title="Tinder des Métiers", page_icon="🎯")

# CSS custom
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
            font-family: 'Segoe UI', sans-serif;
        }
        .st-emotion-cache-mtjnbi {
            width: 100%;
            padding: 2rem 1rem 1rem;
            max-width: 736px;
        }
        h1.title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            text-align: center;
            margin-top: 20px;
        }
        .subtitle {
            font-size: 18px;
            color: #3B82F6;
            text-align: center;
            margin-bottom: 20px;
        }
        .swipe-buttons{
            background-color: red;
        }
            
        button {
            background-color: #3B82F6 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 24px !important;
            font-size: 16px !important;
        }
        @media screen and (max-width: 400px) {
            h4{
                font-size: 5px;
            }
        }

        
    </style>
""", unsafe_allow_html=True)

# Initialisation du moteur et des variables d'état
if "engine" not in st.session_state:
    st.session_state.engine = MatchingEngine()
    st.session_state.engine.reset_profil()
if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "liked_metiers" not in st.session_state:
    st.session_state.liked_metiers = []
if "temp" not in st.session_state:
    st.session_state.temp = []
if "current_metier" not in st.session_state:
    st.session_state.current_metier = None
if "disliked_metiers" not in st.session_state:
    st.session_state.disliked_metiers = []

engine = st.session_state.engine

# Titre
st.markdown("<h1 class='title'>🎯 JobFinder</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Découvre ton futur métier !</p>", unsafe_allow_html=True)

# Recommandation
metiers = engine.get_recommendations(top_k=1, liked=st.session_state.liked_metiers, disliked=st.session_state.disliked_metiers)

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

    print("éééééééééééééééééééééééééééééééééééé")
    print("le nouveau métier est : ", st.session_state.temp)
    print("éééééééééééééééééééééééééééééééééééé")
    if len(st.session_state.temp) >= 2:
        if st.session_state.temp[-1]['id'] == st.session_state.temp[-2]['id']:
            st.rerun()
    # Chargement illustration
    image_path = "app/assets/jobinder_illu.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()

        st.markdown(f"""
            <div style="position: relative; width: 100%; margin: auto;">
                <img src="data:image/png;base64,{encoded_image}" style="width: 1200px; height: 70vh; border-radius: 12px; opacity:0.7">
                <div class='fiche' style="position: absolute; overflow:auto; width: 40%; height:70%; overflow:auto; top: 15%; left: 12%; right: 12%; background: none; padding: 12px;">
                    <h4 class='titre' style="color:#1E3A8A; background-color: #ffffff">{metier['nom']}</h3>
                    <p style="margin: 0; background-color: #ffffff">{metier['description_detaillee']}</p>
                    <p style="margin: 0; background-color: #ffffff"><strong>Salaire :</strong> {metier['salaire_moyen']} €</p>
                    <p style="margin: 0; background-color: #ffffff"><strong>Niveau :</strong> {metier['niveau_etude']}</p>
                    <div style="margin-top: 0;">
                        <a href="{metier['lien_fiche_metier']}" target="_blank" style=" background-color: #ffffff; text-decoration: none; color: #2563eb;"><strong>🔗 En savoir plus</strong></a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Boutons like/dislike
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="swipe-buttons dislike">', unsafe_allow_html=True)
        if st.button("👎 Je passe"):
            print("hello")
            dislike = st.session_state.temp[-2]
            #del st.session_state.temp[-2]
            st.session_state.disliked_metiers.append(dislike)
            #engine.dislike_metier(dislike['id'])
            st.session_state.last_action = "pass"
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="swipe-buttons like">', unsafe_allow_html=True)
        if st.button("👍 J'aime"):
            temp = st.session_state.temp[-2]
            st.session_state.liked_metiers.append(temp)
            engine.like_metier(temp['id'], liked_metier=st.session_state.liked_metiers)
            st.session_state.last_action = "like"
        st.markdown('</div>', unsafe_allow_html=True)

# Métiers aimés
# Métiers aimés
st.subheader("Métiers que vous aimez déjà")
if st.session_state.liked_metiers:
    temps = st.session_state.liked_metiers
    for elem in temps:
        metier = engine.df[engine.df["id"] == elem["id"]].iloc[0]
        st.markdown(f"""
        <div style='display: inline-block; background-color: #36f0ba; color: white; padding: 8px 12px; border-radius: 8px; margin: 6px 4px;'>
            <a href='{metier['lien_fiche_metier']}' target='_blank' style='color: white; text-decoration: none;'>⭐ {metier['nom']}</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("Aucun métier liké pour le moment.")



# ajouter une div pour la liste avec un overflow auto