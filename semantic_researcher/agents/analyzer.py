# semantic_researcher/agents/analyzer.py
# Rôle : raisonnement sémantique profond sur les faits collectés
# GenAI : transforme des faits bruts en connaissance structurée

import os
import time
import json
import re
from google import genai
from google.genai import types
from shared.logger import log_info, log_decision

SYSTEM_PROMPT = """Tu es un agent analyste expert en raisonnement sémantique.
Tu reçois des faits bruts sur un sujet et tu dois produire une analyse profonde.

Réponds en JSON strict :
{
  "resume": "résumé clair en 3-4 phrases",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "tendances": ["tendance 1", "tendance 2"],
  "limitations": ["limite ou biais détecté 1", "limite 2"],
  "conclusion": "conclusion synthétique"
}"""


def run(sujet: str, donnees_researcher: dict) -> dict:
    log_info("Analyzer", "Début du raisonnement sémantique")
    log_decision("Analyzer", "Synthèse des faits en insights structurés")

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    faits = donnees_researcher.get("faits", [])
    points_cles = donnees_researcher.get("points_cles", [])

    prompt = f"""Sujet : {sujet}

Faits collectés :
{chr(10).join(f"- {f}" for f in faits)}

Points clés identifiés :
{chr(10).join(f"- {p}" for p in points_cles)}

Produis une analyse sémantique approfondie."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=[{"role": "user", "parts": [{"text": prompt}]}]
    )
    time.sleep(13)

    raw = re.sub(r"```json|```", "", response.text.strip()).strip()
    try:
        analyse = json.loads(raw)
        log_info("Analyzer", f"Analyse produite : {len(analyse.get('insights', []))} insights")
        return analyse
    except:
        return {
            "resume": response.text[:300],
            "insights": ["Analyse disponible dans le résumé"],
            "tendances": [],
            "limitations": [],
            "conclusion": response.text[:200]
        }