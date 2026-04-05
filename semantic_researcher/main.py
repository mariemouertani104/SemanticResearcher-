# semantic_researcher/main.py
# Orchestrateur principal avec Human-in-the-Loop
# Synergie GenAI + Agentic AI — NVIDIA DLI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import researcher, analyzer, critic, writer
from shared.logger import log_start, log_human

MAX_RETRIES = 2


def human_checkpoint(sujet: str, analyse: dict) -> tuple[bool, str]:
    """
    Point de contrôle humain — affiche le résumé et attend validation.
    Retourne (approuvé, feedback).
    """
    print("\n" + "="*60)
    print("  VALIDATION HUMAINE REQUISE")
    print("="*60)
    print(f"\nRésumé de l'analyse sur : {sujet}")
    print(f"\n{analyse.get('resume', '')}\n")
    print("Insights principaux :")
    for ins in analyse.get("insights", [])[:3]:
        print(f"  - {ins}")
    print("\n" + "-"*60)
    print("1. Approuver — générer le rapport final")
    print("2. Refuser   — relancer avec feedback")
    print("3. Abandonner")

    choix = input("\nTon choix (1/2/3) : ").strip()

    if choix == "1":
        log_human("Analyse approuvée")
        return True, ""
    elif choix == "2":
        feedback = input("Ton feedback (ex: 'manque de données récentes') : ").strip()
        log_human(f"Refus avec feedback : {feedback}")
        return False, feedback
    else:
        log_human("Abandon")
        return False, "abandon"


def run(sujet: str):
    log_start(sujet)

    donnees = None
    analyse = None

    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            print(f"\n  [Retry {attempt}] Relance de la recherche...")

        # 1. Researcher collecte les faits
        donnees = researcher.run(sujet)

        # 2. Analyzer produit l'analyse sémantique
        analyse = analyzer.run(sujet, donnees)

        # 3. Critic évalue la qualité
        evaluation = critic.evaluate(sujet, analyse)

        if not evaluation.get("approuve", True) and evaluation.get("score", 7) < 6:
            feedback = evaluation.get("feedback", "")
            print(f"\n  [Critic] Score insuffisant — {feedback}")
            if attempt < MAX_RETRIES:
                sujet_enrichi = f"{sujet}. Focus sur : {feedback}"
                sujet = sujet_enrichi
                continue

        # 4. Human-in-the-Loop
        approuve, feedback_humain = human_checkpoint(sujet, analyse)

        if approuve:
            # 5. Writer génère le rapport final
            rapport_path = writer.generate(sujet, donnees, analyse, evaluation)
            print(f"\nRapport généré : {rapport_path}")
            print(f"Log complet    : research_log.txt")
            return

        elif feedback_humain == "abandon":
            print("\nRecherche abandonnée.")
            return
        else:
            # Relance avec feedback humain
            sujet = f"{sujet}. {feedback_humain}"
            print(f"\n  Relance avec : {sujet}")

    print("\nNombre maximum de tentatives atteint.")


def menu():
    print("\n" + "="*60)
    print("   SEMANTIC RESEARCHER")
    print("   GenAI + Agentic AI + Human-in-the-Loop")
    print("="*60)
    print("1. Lancer une recherche")
    print("2. Quitter")
    return input("Ton choix : ").strip()


if __name__ == "__main__":
    while True:
        choix = menu()
        if choix == "1":
            sujet = input("\nSujet de recherche : ").strip()
            if sujet:
                run(sujet)
        elif choix == "2":
            print("Au revoir !")
            break