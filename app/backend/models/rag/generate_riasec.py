# backend/models/rag/generate_riasec_reco.py
from typing import List
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from backend.models.rag.query_rag import get_relevant_documents, llm

# === Prompt pour l'analyse RIASEC
riasec_prompt_template = PromptTemplate.from_template("""
Tu es un conseiller expert en orientation professionnelle.
Tu vas recevoir un ensemble de réponses issues d'un test de personnalité basé sur le modèle RIASEC.

À partir de ces réponses, propose une analyse de la personnalité de l'utilisateur, puis recommande-lui 3 secteurs d'activité dans lesquels il pourrait s'épanouir.
Pour chaque secteur, donne 2 métiers pertinents (un connu, un moins connu).
Justifie chaque suggestion en lien avec la personnalité détectée. Sois clair, bienveillant et professionnel.

Voici les réponses de l'utilisateur :
{riasec_answers}

Voici des documents internes utiles :
{context}

Donne une réponse structurée et facile à comprendre.
""")

def generate_reco_from_riasec(riasec_responses: List[str]) -> str:
    answers_block = "\n".join(f"- {resp}" for resp in riasec_responses)

    internal_docs = get_relevant_documents(answers_block)
    for doc in internal_docs:
        doc.page_content = "[Interne] " + doc.page_content

    context = "\n\n".join(set(doc.page_content for doc in internal_docs))

    prompt = riasec_prompt_template.format(
        riasec_answers=answers_block,
        context=context
    )

    response = llm.invoke(prompt)
    return response.strip()
