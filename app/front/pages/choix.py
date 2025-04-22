import streamlit as st
import base64
import os

# Configuration de la page
st.set_page_config(page_title="Choisis ton questionnaire", page_icon="🧭")

# CSS personnalisé
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            color: #1E3A8A;
        }
        h1.title {
            font-size: 32px;
            font-weight: bold;
            color: #1E3A8A;
            text-align: center;
            margin-top: 20px;
        }
        .card-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 40px;
        }
        .card {
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: center;
            width: 220px;
        }
        .card h2 {
            color: #1E3A8A;
            font-size: 20px;
        }
        .card p {
            font-size: 16px;
            margin: 10px 0 20px;
        }
        .card button {
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        .card button:hover {
            background-color: #2563eb;
        }
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }
        .background img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.15;
        }
        @media screen and (max-width: 400px) {
            .card-container {
                flex-direction: column !important;
                align-items: center;
                gap: 20px;
                margin-top: 20px;
            }

            .card {
                width: 85% !important;
                padding: 20px;
            }

            .card h2 {
                font-size: 18px !important;
            }

            .card p {
                font-size: 14px !important;
            }

            .card button {
                font-size: 14px !important;
                padding: 8px 16px !important;
                width: 100%;
            }

            h1.title {
                font-size: 24px !important;
                padding: 0 10px;
            }

            img {
                display: none !important;
            }
        }

    </style>
""", unsafe_allow_html=True)

# Affichage image de fond
illu_path = "app/assets/illu_first.png"  # illustration utilisée
if os.path.exists(illu_path):
    with open(illu_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style='position: absolute; width: 100%; height: 280px;'>
            <img src='data:image/png;base64,{encoded_string}' style='position: absolute; width: auto; height: auto; left: 32%; top:-10%; object-fit: cover; border-radius: 16px; opacity: 0.7;'>
            <div style='position: absolute; z-index: 2; padding: 20px;'>
            </div>
        </div>
    """, unsafe_allow_html=True)
# Titre
st.markdown("<h1 class='title'>Combien de temps as-tu devant toi ?</h1>", unsafe_allow_html=True)

# Bloc de sélection
st.markdown("""
<div class="card-container">
    <div class="card">
        <h2>⏱️ 5 minutes</h2>
        <p>Un test express en 5 questions.</p>
        <form action="/questionnaire_5_minutes" method="get">
            <button type="submit">C'est parti</button>
        </form>
    </div>
    <div class="card">
        <h2>🕙 10 minutes</h2>
        <p>Un échange interactif pour mieux cerner ton profil.</p>
        <form action="/questionnaire_10_minutes" method="get">
            <button type="submit">Je continue</button>
        </form>
    </div>
    <div class="card">
        <h2>🧩 30 minutes</h2>
        <p>Un test de personnalité complet basé sur le modèle RIASEC.</p>
        <form action="/questionnaire_personalite" method="get">
            <button type="submit">Je veux tout savoir</button>
        </form>
    </div>
</div>
""", unsafe_allow_html=True)
