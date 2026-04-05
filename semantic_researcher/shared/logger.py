# semantic_researcher/shared/logger.py
# Observabilité : trace chaque décision de chaque agent

import datetime
import os

LOG_FILE = "research_log.txt"


def _write(level: str, agent: str, message: str):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{level}] [{agent}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_start(sujet: str):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== SEMANTIC RESEARCHER — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
        f.write(f"Sujet : {sujet}\n\n")
    print(f"\n{'='*60}")
    print(f"  Sujet : {sujet}")
    print(f"{'='*60}")


def log_info(agent: str, message: str):
    _write("INFO", agent, message)


def log_decision(agent: str, decision: str):
    _write("DECISION", agent, decision)


def log_score(agent: str, score: int, feedback: str):
    _write("SCORE", agent, f"{score}/10 — {feedback}")


def log_human(message: str):
    _write("HUMAN", "utilisateur", message)


def log_end(rapport_path: str):
    _write("END", "system", f"Rapport sauvegarde : {rapport_path}")
    print(f"\n{'='*60}")
    print(f"  Rapport final : {rapport_path}")
    print(f"{'='*60}\n")