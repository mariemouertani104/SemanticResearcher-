# SemanticResearcher
### GenAI + Agentic AI + Human-in-the-Loop

> Système multi-agents de recherche autonome combinant la puissance des LLMs  
> (raisonnement sémantique) et des agents IA (prise de décision + action),  
> avec validation humaine et génération de rapports PDF professionnels.

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Pourquoi ce projet est important](#pourquoi-ce-projet-est-important)
3. [Architecture du système](#architecture-du-système)
4. [Les 4 agents spécialisés](#les-4-agents-spécialisés)
5. [Fonctionnalités clés](#fonctionnalités-clés)
6. [Structure du projet](#structure-du-projet)
7. [Installation](#installation)
8. [Utilisation](#utilisation)
9. [Démonstration](#démonstration)
10. [Observabilité](#observabilité)
11. [Références académiques](#références-académiques)

---

## Vue d'ensemble

SemanticResearcher est un système multi-agents autonome qui répond à une question fondamentale posée par le cours NVIDIA Deep Learning Institute :

> *"When Generative AI (which creates content) and Agentic AI (which makes decisions and takes action) work together, the result is on-demand semantic reasoning."*

Ce projet incarne exactement cette synergie :

- **GenAI** comprend le sujet en langage naturel, génère des requêtes de recherche optimales, synthétise sémantiquement les résultats, et rédige un rapport professionnel.
- **Agentic AI** prend des décisions autonomes — relancer la recherche, évaluer la qualité, décider si le résultat est suffisant, orchestrer le pipeline.
- **Human-in-the-Loop** garantit que l'humain reste dans la boucle avant la production finale.

---

## Pourquoi ce projet est important

Ce système illustre concrètement les 5 capacités clés des systèmes GenAI + Agentic AI :

| Capacité | Comment c'est implémenté |
|----------|--------------------------|
| Raisonnement sémantique à la demande | Le LLM comprend "INSAT école Tunis" et génère les bonnes requêtes |
| Pont entre langage naturel et logiciel | L'utilisateur écrit en français, l'agent traduit en actions concrètes |
| Traitement parallèle | Rechercher + Analyser + Évaluer de façon enchaînée et optimisée |
| Observabilité | Chaque décision de chaque agent tracée dans `research_log.txt` |
| Human-in-the-Loop | Validation humaine avant génération du rapport final |

---

## Architecture du système

```
Utilisateur (langage naturel)
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│                    PIPELINE PRINCIPAL                    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Researcher Agent                      │    │
│  │  1. LLM génère 2 requêtes de recherche optimales│    │
│  │  2. Recherche web réelle (DuckDuckGo)            │    │
│  │  3. LLM extrait les faits sémantiquement        │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │ faits + sources               │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Analyzer Agent                        │    │
│  │  Raisonnement sémantique profond                │    │
│  │  → résumé, insights, tendances, limitations     │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │ analyse structurée            │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Critic Agent                          │    │
│  │  Évalue la qualité (score 1-10)                 │    │
│  │  Score < 6 → retry automatique (max 2 fois)     │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │ approuvé ?                    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │        Human-in-the-Loop                        │    │
│  │  Affiche résumé + insights à l'utilisateur      │    │
│  │  → Approuver / Refuser avec feedback / Abandon  │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │ approuvé                      │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Writer Agent                          │    │
│  │  Génère rapport PDF professionnel               │    │
│  │  Page de garde + 8 sections + score fiabilité   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Log Observabilité — research_log.txt            │    │
│  │  Chaque décision tracée en temps réel           │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
           │
           ▼
    Rapport PDF professionnel
    dans RAPPORTS_PDF/
```

---

## Les 4 agents spécialisés

### Researcher Agent — `agents/researcher.py`

Le collecteur. Il comprend sémantiquement le sujet et génère des requêtes de recherche optimales grâce au LLM, puis effectue des recherches web réelles et extrait les faits importants.

**Exemple concret :**
```
Sujet : "INSAT école d'ingénieurs Tunis"
→ Requête 1 : "INSAT Tunis présentation programmes spécialités admission"
→ Requête 2 : "INSAT Tunis débouchés professionnels réputation classement"
→ 8 faits extraits sémantiquement
```

### Analyzer Agent — `agents/analyzer.py`

Le penseur. Il transforme des faits bruts en connaissance structurée via le raisonnement sémantique du LLM. Produit résumé, insights, tendances et limitations.

### Critic Agent — `agents/critic.py`

Le contrôleur qualité. Il évalue l'analyse sur 10 points et décide si on peut avancer ou s'il faut relancer. Retry automatique avec feedback enrichi si score insuffisant.

**Le Critic a détecté et corrigé :**
- Score 5/10 → Retry avec focus sur les données concrètes
- Score 6/10 → Retry avec focus sur les sources vérifiables
- Score 9/10 → Validation et passage au Human-in-the-Loop

### Writer Agent — `agents/writer.py`

Le rédacteur. Il génère un rapport PDF professionnel complet avec page de garde colorée, résumé exécutif, 8 sections structurées, tableau des insights, score de fiabilité et liste des sources.

---

## Fonctionnalités clés

### Human-in-the-Loop

Avant de générer le rapport final, le système pause et affiche à l'utilisateur :
- Le résumé de l'analyse
- Les 3 insights principaux
- 3 options : Approuver / Refuser avec feedback / Abandonner

Si l'utilisateur refuse, il peut donner un feedback précis qui enrichit le sujet pour la relance. Exemple réel :

```
Utilisateur : "INSAT" → Agent cherche le satellite indien
Human feedback : "l'INSAT est une école d'ingénieurs à Tunis"
→ Agent relance avec le bon contexte → Score 9/10
```

### Rapport PDF professionnel

Le rapport généré contient :
- Page de garde avec bannière colorée et métadonnées
- Résumé exécutif en encadré vert
- 8 sections numérotées et structurées
- Tableau des insights avec alternance de couleurs
- Score de fiabilité coloré (vert/orange/rouge selon le score)
- Liste des sources consultées

### Observabilité complète

Chaque action est tracée dans `research_log.txt` :
```
[15:23:03] [INFO]     [Researcher] Analyse du sujet : ...
[15:23:03] [DECISION] [Researcher] Génération des requêtes via LLM
[15:23:57] [INFO]     [Researcher] 8 faits extraits
[15:24:45] [SCORE]    [Critic]     5/10 — manque de données concrètes
[15:34:02] [HUMAN]    [utilisateur] Analyse approuvée
[15:34:47] [END]      [system]      Rapport sauvegardé : rapport_*.pdf
```

### Retry automatique intelligent

Le Critic enrichit le sujet avec son feedback avant chaque retry :
```
Sujet original → Sujet + "Focus sur : [feedback du Critic]"
```
Maximum 2 retries automatiques, puis passage au Human-in-the-Loop quoi qu'il arrive.

---

## Structure du projet

```
SemanticResearcher/
├── semantic_researcher/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── researcher.py    # Collecte sémantique des faits
│   │   ├── analyzer.py      # Raisonnement et synthèse
│   │   ├── critic.py        # Évaluation qualité + retry
│   │   └── writer.py        # Génération PDF professionnel
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── tools.py         # Recherche web DuckDuckGo
│   │   └── logger.py        # Observabilité — trace tout
│   └── main.py              # Orchestrateur + Human-in-the-Loop
├── RAPPORTS_PDF/            # Rapports générés (téléchargeables)
├── research_log.txt         # Log complet de chaque session
└── README.md
```

---

## Installation

### Prérequis

- Python 3.12+
- Clé API Google Gemini gratuite : [aistudio.google.com](https://aistudio.google.com)
- GitHub Codespaces ou environnement local

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/mariemouertani104/SemanticResearcher-.git
cd SemanticResearcher-

# 2. Installer les dépendances
pip install google-genai ddgs reportlab

# 3. Configurer la clé API
export GOOGLE_API_KEY="votre_clé_api_google"

# 4. Lancer le système
cd semantic_researcher
python main.py
```

---

## Utilisation

```
============================================================
   SEMANTIC RESEARCHER
   GenAI + Agentic AI + Human-in-the-Loop
============================================================
1. Lancer une recherche
2. Quitter
```

Entre un sujet de recherche en langage naturel au choix **1**. Le système fait tout le reste.

### Sujets testés avec succès

- `Les applications de l'intelligence artificielle dans la médecine en 2025`
- `INSAT Institut National des Sciences Appliquées et de Technologie Tunis`
- `Les tendances du marché de l'énergie solaire en Afrique du Nord`

### Télécharger le rapport PDF

Les rapports sont sauvegardés dans `RAPPORTS_PDF/`. Dans VS Code :
- Clic droit sur le fichier PDF → **Download...**

---

## Démonstration

### Exemple complet — INSAT Tunis

```
Sujet : "donnez ce que vous savez à propos l'INSAT"

[Researcher] Requêtes générées : INSAT Indian National Satellite...
→ Mauvais résultat (satellite indien)

[Human-in-the-Loop] Score 9/10
→ Utilisateur : REFUS
→ Feedback : "l'INSAT est une école d'ingénieurs à Tunis"

[Researcher] Nouvelles requêtes :
  - "INSAT Tunis présentation programmes spécialités admission"
  - "INSAT Tunis débouchés professionnels réputation classement"
→ 8 faits extraits

[Analyzer] 4 insights produits

[Critic] Score : 9/10 — Satisfaisant

[Human-in-the-Loop]
→ Utilisateur : APPROUVE

[Writer] Rapport PDF généré : rapport_INSAT_20260405.pdf
```

---

## Observabilité

Chaque session génère un fichier `research_log.txt` complet :

```
=== SEMANTIC RESEARCHER — 2026-04-05 15:42 ===
Sujet : INSAT Institut National des Sciences Appliquées et de Technologie, Tunis

[15:42:50] [INFO]     [Researcher] Analyse du sujet : ...
[15:43:13] [DECISION] [Researcher] Génération des requêtes de recherche via LLM
[15:43:42] [INFO]     [Researcher] 9 faits extraits
[15:44:06] [INFO]     [Analyzer]   Analyse produite : 4 insights
[15:44:26] [SCORE]    [Critic]     9/10 — Satisfaisant
[15:47:25] [HUMAN]    [utilisateur] Analyse approuvée
[15:49:33] [END]      [system]      Rapport sauvegardé : rapport_INSAT_*.pdf
```

Ce log est la preuve de l'observabilité complète du système — chaque décision est traçable, auditée et reproductible.

---

## Références académiques

### Papiers de recherche

1. **Russell, S. & Norvig, P.** (1995). *Artificial Intelligence: A Modern Approach*. Prentice Hall.
   - Fondation théorique : définition formelle des agents percevant leur environnement et agissant sur lui.

2. **Wei, J. et al.** (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022.
   - [arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
   - Utilisé dans : Researcher et Analyzer — raisonnement en chaîne avant d'agir.

3. **Yao, S. et al.** (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.
   - [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
   - Utilisé dans : Researcher — boucle Thought → Action → Observation.

4. **Park, J. S. et al.** (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. UIST 2023.
   - [arxiv.org/abs/2304.03442](https://arxiv.org/abs/2304.03442)
   - Utilisé dans : architecture multi-agents et planification.

### Cours

5. **NVIDIA Deep Learning Institute** (2025). *Building AI Agents*.
   - Concepts implémentés : synergie GenAI + Agentic AI, Human-in-the-Loop, observabilité, Reflection Pattern, Tool Use Pattern, Hierarchical Pattern, Workflow Design.
   - Citation directe : *"When Generative AI and Agentic AI work together, the result is on-demand semantic reasoning."*
   - [learn.nvidia.com](https://learn.nvidia.com)

### Outils utilisés

| Outil | Version | Rôle |
|-------|---------|------|
| Google Gemini API | gemini-2.5-flash | LLM principal pour tous les agents |
| ddgs | latest | Recherche web DuckDuckGo (gratuit) |
| reportlab | 4.4.10 | Génération PDF professionnelle |
| GitHub Codespaces | — | Environnement de développement cloud |

---

## Lien avec les projets précédents

Ce projet est le 3ème d'une série progressive :

| Projet | Description | Nouveauté |
|--------|-------------|-----------|
| [ai-agent-from-scratch](https://github.com/mariemouertani104/ai-agent-from-scratch) | Agent unique ReAct + mémoire longue | Boucle ReAct, ChromaDB |
| [multi-agent-system](https://github.com/mariemouertani104/multi-agent-system) | 4 agents spécialisés collaborants | Architecture hiérarchique |
| **SemanticResearcher** | **GenAI + Agentic AI + HITL + PDF** | **Synergie complète, sortie professionnelle** |

Chaque projet ajoute une couche de sophistication, culminant avec SemanticResearcher qui combine toutes les briques en un système production-ready.

---

*Projet développé avec GitHub Codespaces — Avril 2026*
