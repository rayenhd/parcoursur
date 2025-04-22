# backend/models/rag/generate_question.py

from typing import List, Tuple
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from backend.models.rag.query_rag import answer_question
from openai import AzureOpenAI

AZURE_API_KEY = "70vwwlq5J8a2CrqnMZVfxY83ztdx6Ahgor5y2WbUHtTBgOhuROIdJQQJ99BDAC5T7U2XJ3w3AAABACOGrF5i"
AZURE_ENDPOINT = "https://oai-test-rg-test.openai.azure.com/"
AZURE_DEPLOYMENT = "gpt-4o"  # ou ton nom de déploiement
AZURE_API_VERSION = "2025-01-01-preview"


"""""
# === Configuration LLM
llm = HuggingFaceEndpoint(
    repo_id="tiiuae/falcon-7b-instruct",
    temperature=0.4,
    max_new_tokens=256,
    task="text-generation",
    huggingfacehub_api_token="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"
)
"""

client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY
)


# === Prompt Template pour générer la prochaine question
prompt_template = PromptTemplate.from_template("""
Tu es un conseiller en orientation scolaire et professionnelle.
Tu dois poser une série de 7 questions personnalisées pour aider un jeune à découvrir les secteurs d'activités et les métiers qui pourraient lui correspondre.

Voici l'historique des questions déjà posées et des réponses fournies :
{history}

Propose maintenant une nouvelle question simple, claire et fermée (avec des choix). Ne pose pas une question déjà posée.
Ta réponse doit être au format :
Question: <texte de la question>
Choix: <choix1>, <choix2>, <choix3>, <choix4>
""")


def generate_next_question(history_pairs: list[tuple[str, str]]) -> str:
    # Reformatage de l'historique
    history_text = "\n".join([f"Q: {q}\nR: {r}" for q, r in history_pairs]) or "(aucune question posée)"

    prompt = f"""
Tu joues le rôle d’un conseiller d’orientation expert. Tu vas poser 7 questions à un utilisateur pour cerner son profil.

Voici les échanges précédents :
{history_text}

Pose-moi une nouvelle question (courte, claire, adaptée à un jeune) pour continuer à mieux cerner ma personnalité et mes préférences professionnelles.

Réponds uniquement par la question, sans explication ni commentaire. Il ne faut pas que ça soit trop long et ça doit tenir sur une ligne.
""".strip()

    # Appel au LLM
    response = answer_question(prompt)

    # Debug
    print("🧠 Réponse du LLM pour la question suivante :")
    print(response)

    # Nettoyage de la réponse : on garde la première ligne non vide
    lines = [line.strip() for line in response.split("\n") if line.strip()]
    if not lines:
        raise ValueError("Format de la réponse du LLM incorrect.")
    
    return response

def generate_final_recommendation(history_pairs: List[Tuple[str, str]]) -> str:
    history_text = "\n".join([f"Q: {q}\nR: {r}" for q, r in history_pairs])
    prompt = f"""
Tu es un conseiller d’orientation scolaire et professionnelle. Voici le profil d’un utilisateur basé sur ses réponses à 7 questions :

{history_text}

À partir de ces réponses, propose 3 secteurs d’activité dans lesquels il pourrait s’épanouir.
Pour chaque secteur, donne 2 métiers pertinents (un très connu, un moins connu).
Explique brièvement pourquoi ces suggestions sont adaptées à la personne.
Donne une réponse claire, bienveillante, professionnelle et directement exploitable.
"""

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Tu es un assistant d’orientation scolaire bienveillant, drôle et clair."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    return response