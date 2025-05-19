import streamlit as st
from openai import AzureOpenAI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.rag.query_rag import answer_question


# === Configuration Azure OpenAI ===
API_KEY = "563i46EB2UGwXDYza3g29DjU3xH7ytdS7dSHmtWGpQBRNzVqkHHTJQQJ99BEACHYHv6XJ3w3AAAAACOGgErO"
ENDPOINT = "https://aissa-mapkatvd-eastus2.cognitiveservices.azure.com/"
API_VERSION = "2025-01-01-preview"
DEPLOYMENT_NAME = "gpt-4o"  # ⚠️ Mets ici le nom exact de ton déploiement Azure

# === Création du client AzureOpenAI ===
client = AzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version=API_VERSION
)

# === Interface Streamlit ===
st.title("🔍 Test Azure OpenAI sur Streamlit Cloud")
st.write("Ce test vérifie si l’appel à Azure OpenAI fonctionne bien sur Streamlit Community Cloud.")

if st.button("📡 Tester Azure OpenAI"):
    try:
        response = response = answer_question("testttt", client=client)

    except Exception as e:
        st.error("❌ Erreur lors de l’appel à Azure OpenAI :")
        st.exception(e)

# Diagnostic supplémentaire
import os
#st.write("🔍 Variable OPENAI_API_KEY dans l’environnement :",st.secrets["OPENAI_API_KEY"])
#st.write("🔍 Variable OPENAI_API_BASE dans l’environnement :",st.secrets["OPENAI_API_KEY"])
