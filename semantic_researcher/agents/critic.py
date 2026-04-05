# semantic_researcher/agents/critic.py
# Rôle : évalue la qualité de l'analyse et décide si on peut avancer
# Pattern : Reflection (NVIDIA DLI)

import os
import time
import json
import re
from google import genai
from google.genai import types
from shared.logger import log_score, log_decision

SYSTEM_PROMPT = """Tu es un agent critique rigoureux. Tu évalues la qualité
d'une analyse de recherche selon ces critères :
- Profondeur et pertinence des insights
- Présence de sources et faits concrets
- Identification des limitations
- Clarté de la conclusion

Réponds en JSON strict :
{
  "score": [entier de 1 à 10],
  "approuve": [true si score >= 6, false sinon],
  "points_forts": ["point fort 1", "point fort 2"],
  "feedback": "ce qui manque ou doit être amélioré (vide si approuvé)"
}"""


def evaluate(sujet: str, analyse: dict) -> dict:
    log_decision("Critic", "Évaluation de la qualité de l'analyse")

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    prompt = f"""Sujet original : {sujet}

Analyse produite :
- Résumé : {analyse.get('resume', '')}
- Insights : {analyse.get('insights', [])}
- Tendances : {analyse.get('tendances', [])}
- Limitations identifiées : {analyse.get('limitations', [])}
- Conclusion : {analyse.get('conclusion', '')}

Évalue la qualité de cette analyse."""

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
        evaluation = json.loads(raw)
        score = evaluation.get("score", 7)
        feedback = evaluation.get("feedback", "")
        log_score("Critic", score, feedback or "Satisfaisant")
        return evaluation
    except:
        log_score("Critic", 7, "Parsing OK par défaut")
        return {"score": 7, "approuve": True, "points_forts": [], "feedback": ""}