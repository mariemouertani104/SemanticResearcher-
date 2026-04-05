# semantic_researcher/shared/tools.py
# Outil de recherche web partagé entre tous les agents

def web_search(query: str, max_results: int = 4) -> list[dict]:
    """
    Recherche sur le web via DuckDuckGo.
    Retourne une liste de dicts avec title, body, href.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return [{"title": "Aucun résultat", "body": "", "href": ""}]
        return results
    except Exception as e:
        return [{"title": "Erreur", "body": str(e), "href": ""}]


def format_results(results: list[dict]) -> str:
    """Formate les résultats pour injection dans un prompt."""
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"Source {i}: {r.get('title', '')}")
        lines.append(f"  {r.get('body', '')[:200]}")
        lines.append(f"  URL: {r.get('href', '')}")
    return "\n".join(lines)