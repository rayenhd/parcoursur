import streamlit as st
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Parcoursur - Accueil",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Couleurs personnalisées en CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
        }
        .title {
            font-size: 42px;
            font-weight: bold;
            color: #150e60;
            margin-top: 40px;
        }
        .subtitle {
            font-size: 20px;
            color: #150e60;
            margin-bottom: 20px;
        }
        .cta-button {
            background-color: #3B82F6;
            color: white;
            padding: 0.75rem 2rem;
            font-size: 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .test-card {
            background-color: #f9f9f9;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .test-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Layout principal
titre, illustration = st.columns([1, 1])

with titre:
    st.markdown("<div class='title'>DIRECTION LA <strong style='color: #f2ae19'>RÉUSSITE !</strong></div>", unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Une IA bienveillante pour guider ton avenir scolaire et professionnel.</div>', unsafe_allow_html=True)
    st.markdown('<a href="https://parcoursur.fr/"><button class="cta-button">Découvre nous</button></a>', unsafe_allow_html=True)

    # Logo
    logo = Image.open("assets/logo_complet.png")
    st.image(logo, width=400)

with illustration:
    st.image("assets/illustration.png", use_container_width=True)

# Section de sélection de tests
st.markdown("""
<hr>
<h3 id="tests">Choisis ton test :</h3>
""", unsafe_allow_html=True)

test1, test2, test3 = st.columns(3)

with test1:
    st.markdown("""
    <div class="test-card">
        <div class="test-icon">⏱️</div>
        <h4>Tu sais déjà ce que tu veux ?</h4>
        <p>Utilise notre chatbot afin de t'aiguiller au mieux</p>
        <a href="/chatbot"><button class="cta-button" style="background-color:#3B82F6;">Commencer</button></a>
    </div>
    """, unsafe_allow_html=True)

with test2:
    st.markdown("""
    <div class="test-card">
        <div class="test-icon">💻</div>
        <h4>Tu ne pas par où commencer ?</h4>
        <p>Nous allons te guider pas à pas en posant différentes questions.</p>
        <a href="/choix"><button class="cta-button" style="background-color:#60A5FA;">Commencer</button></a>
    </div>
    """, unsafe_allow_html=True)

with test3:
    st.markdown("""
    <div class="test-card">
        <div class="test-icon">🧠</div>
        <h4>Tu veux découvrir de nouveaux métiers ?</h4>
        <p>Découvre notre plateforme qui t'aidera à trouver ton futur métier !</p>
        <a href="/jobfinder"><button class="cta-button" style="background-color:#FBBF24; color:black;">Commencer</button></a>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
---
<center>© 2025 Parcoursur - Inspiré par vos rêves, guidé par l'IA 🎓</center>
""", unsafe_allow_html=True)
