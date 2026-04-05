# semantic_researcher/agents/researcher.py
# Rôle : comprend le sujet sémantiquement et collecte les faits
# GenAI : traduit le langage naturel en requêtes de recherche précises

import os
import time
from google import genai
from google.genai import types
from shared.tools import web_search, format_results
from shared.logger import log_info, log_decision

SYSTEM_PROMPT = """Tu es un agent chercheur expert. Tu reçois un sujet de recherche
en langage naturel et tu dois :
1. Générer 2 requêtes de recherche précises et complémentaires
2. Analyser les résultats et extraire les faits importants
3. Identifier les points clés à approfondir

Réponds en JSON strict :
{
  "requetes": ["requête 1", "requête 2"],
  "faits": ["fait 1", "fait 2", "fait 3", "..."],
  "points_cles": ["point 1", "point 2", "point 3"],
  "sources": ["url 1", "url 2"]
}"""


def run(sujet: str) -> dict:
    log_info("Researcher", f"Analyse du sujet : {sujet}")

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Étape 1 : GenAI génère les requêtes de recherche
    log_decision("Researcher", "Génération des requêtes de recherche via LLM")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=[{
            "role": "user",
            "parts": [{"text": f"Sujet de recherche : {sujet}\n\nGénère d'abord les requêtes de recherche optimales."}]
        }]
    )
    time.sleep(13)

    import json, re
    raw = re.sub(r"```json|```", "", response.text.strip()).strip()
    try:
        plan = json.loads(raw)
        requetes = plan.get("requetes", [sujet])
    except:
        requetes = [sujet, f"{sujet} recent research"]

    log_info("Researcher", f"Requêtes générées : {requetes}")

    # Étape 2 : Recherche web réelle
    tous_resultats = []
    for requete in requetes[:2]:
        log_info("Researcher", f"Recherche : {requete}")
        resultats = web_search(requete, max_results=3)
        tous_resultats.extend(resultats)
        time.sleep(2)

    sources_text = format_results(tous_resultats)

    # Étape 3 : GenAI extrait les faits des résultats
    log_decision("Researcher", "Extraction sémantique des faits depuis les sources")
    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=[{
            "role": "user",
            "parts": [{"text": f"Sujet : {sujet}\n\nSources trouvées :\n{sources_text}\n\nExtrait les faits importants."}]
        }]
    )
    time.sleep(13)

    raw2 = re.sub(r"```json|```", "", response2.text.strip()).strip()
    try:
        resultat = json.loads(raw2)
        log_info("Researcher", f"{len(resultat.get('faits', []))} faits extraits")
        return resultat
    except:
        return {
            "requetes": requetes,
            "faits": [sources_text[:500]],
            "points_cles": [sujet],
            "sources": [r.get("href", "") for r in tous_resultats[:3]]
        }