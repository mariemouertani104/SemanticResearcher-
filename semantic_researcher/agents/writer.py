# semantic_researcher/agents/writer.py
# Génère un rapport PDF professionnel avec reportlab

import os
import time
import re
import datetime
from google import genai
from google.genai import types
from shared.logger import log_info, log_end

SYSTEM_PROMPT = """Tu es un agent rédacteur expert. Tu génères des rapports
de recherche clairs, structurés et professionnels en français.
Chaque section doit être riche, précise et directement utilisable."""


def _generate_text(sujet: str, donnees: dict, analyse: dict, evaluation: dict) -> dict:
    """Génère le contenu textuel du rapport via le LLM."""
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    prompt = f"""Génère un rapport de recherche structuré sur : {sujet}

Faits collectés : {donnees.get('faits', [])}
Sources : {donnees.get('sources', [])}
Résumé : {analyse.get('resume', '')}
Insights : {analyse.get('insights', [])}
Tendances : {analyse.get('tendances', [])}
Limitations : {analyse.get('limitations', [])}
Conclusion : {analyse.get('conclusion', '')}
Score de fiabilité : {evaluation.get('score', 7)}/10

Réponds en JSON strict :
{{
  "resume_executif": "résumé en 3 phrases maximum",
  "introduction": "paragraphe d'introduction (5-6 phrases)",
  "faits_cles": ["fait clé 1", "fait clé 2", "fait clé 3", "fait clé 4"],
  "analyse": "paragraphe d'analyse approfondie (6-8 phrases)",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "tendances": ["tendance 1", "tendance 2", "tendance 3"],
  "limitations": ["limitation 1", "limitation 2"],
  "conclusion": "paragraphe de conclusion (4-5 phrases)",
  "sources": ["source 1", "source 2", "source 3"]
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=[{"role": "user", "parts": [{"text": prompt}]}]
    )
    time.sleep(13)

    raw = re.sub(r"```json|```", "", response.text.strip()).strip()
    import json
    try:
        return json.loads(raw)
    except:
        return {
            "resume_executif": analyse.get("resume", ""),
            "introduction": analyse.get("resume", ""),
            "faits_cles": donnees.get("faits", [])[:4],
            "analyse": analyse.get("conclusion", ""),
            "insights": analyse.get("insights", []),
            "tendances": analyse.get("tendances", []),
            "limitations": analyse.get("limitations", []),
            "conclusion": analyse.get("conclusion", ""),
            "sources": donnees.get("sources", [])
        }


def _build_pdf(sujet: str, contenu: dict, evaluation: dict, filename: str):
    """Construit le PDF professionnel avec reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable, PageBreak
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

    # Couleurs
    PURPLE     = HexColor("#534AB7")
    PURPLE_LT  = HexColor("#EEEDFE")
    TEAL       = HexColor("#1D9E75")
    TEAL_LT    = HexColor("#E1F5EE")
    GRAY_DARK  = HexColor("#2C2C2A")
    GRAY_MID   = HexColor("#5F5E5A")
    GRAY_LT    = HexColor("#F1EFE8")
    CORAL      = HexColor("#D85A30")
    AMBER      = HexColor("#BA7517")

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # --- Styles personnalisés ---
    s_title = ParagraphStyle("title",
        fontSize=22, textColor=white, fontName="Helvetica-Bold",
        alignment=TA_CENTER, leading=28)
    s_subtitle = ParagraphStyle("subtitle",
        fontSize=11, textColor=HexColor("#CECBF6"),
        alignment=TA_CENTER, leading=16)
    s_h2 = ParagraphStyle("h2",
        fontSize=13, textColor=PURPLE, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=6, leading=18)
    s_body = ParagraphStyle("body",
        fontSize=10, textColor=GRAY_DARK,
        alignment=TA_JUSTIFY, leading=15, spaceAfter=6)
    s_bullet = ParagraphStyle("bullet",
        fontSize=10, textColor=GRAY_DARK,
        leftIndent=14, leading=14, spaceAfter=4)
    s_caption = ParagraphStyle("caption",
        fontSize=8, textColor=GRAY_MID,
        alignment=TA_CENTER, leading=12)
    s_exec = ParagraphStyle("exec",
        fontSize=10.5, textColor=HexColor("#085041"),
        alignment=TA_JUSTIFY, leading=16,
        leftIndent=10, rightIndent=10)

    # ========== PAGE DE GARDE ==========
    now = datetime.datetime.now()

    # Bannière titre (tableau coloré)
    titre_data = [[Paragraph(f"RAPPORT DE RECHERCHE", s_title)]]
    titre_table = Table(titre_data, colWidths=[15.5*cm])
    titre_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PURPLE),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [PURPLE]),
        ("TOPPADDING", (0,0), (-1,-1), 22),
        ("BOTTOMPADDING", (0,0), (-1,-1), 22),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 16),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(titre_table)
    story.append(Spacer(1, 0.4*cm))

    # Sujet
    sujet_data = [[Paragraph(sujet, s_subtitle)]]
    sujet_table = Table(sujet_data, colWidths=[15.5*cm])
    sujet_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HexColor("#3C3489")),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(sujet_table)
    story.append(Spacer(1, 0.5*cm))

    # Métadonnées
    score = evaluation.get("score", 7)
    score_color = TEAL if score >= 7 else CORAL if score >= 5 else HexColor("#A32D2D")
    meta_data = [
        ["Date", now.strftime("%d %B %Y — %H:%M")],
        ["Système", "SemanticResearcher — GenAI + Agentic AI"],
        ["Score fiabilité", f"{score}/10"],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 11.5*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), GRAY_MID),
        ("TEXTCOLOR", (1,0), (1,-2), GRAY_DARK),
        ("TEXTCOLOR", (1,2), (1,2), score_color),
        ("FONTNAME", (1,2), (1,2), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [GRAY_LT, white]),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.6*cm))

    # Résumé exécutif
    exec_data = [[
        Paragraph("RÉSUMÉ EXÉCUTIF", ParagraphStyle("exec_title",
            fontSize=9, textColor=TEAL, fontName="Helvetica-Bold")),
    ],[
        Paragraph(contenu.get("resume_executif", ""), s_exec),
    ]]
    exec_table = Table(exec_data, colWidths=[15.5*cm])
    exec_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), TEAL_LT),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(exec_table)
    story.append(PageBreak())

    # ========== CORPS DU RAPPORT ==========

    def section(titre, content_paragraphs):
        story.append(Paragraph(titre, s_h2))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=PURPLE_LT, spaceAfter=6))
        for p in content_paragraphs:
            story.append(p)
        story.append(Spacer(1, 0.3*cm))

    # 1. Introduction
    section("1. Introduction", [
        Paragraph(contenu.get("introduction", ""), s_body)
    ])

    # 2. Faits clés
    faits = contenu.get("faits_cles", [])
    faits_paragraphs = [
        Paragraph(f"• {f}", s_bullet) for f in faits
    ]
    section("2. Faits et données clés", faits_paragraphs)

    # 3. Analyse
    section("3. Analyse approfondie", [
        Paragraph(contenu.get("analyse", ""), s_body)
    ])

    # 4. Insights — tableau coloré
    story.append(Paragraph("4. Insights principaux", s_h2))
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=PURPLE_LT, spaceAfter=6))
    insights = contenu.get("insights", [])
    if insights:
        ins_data = [[Paragraph(f"Insight {i+1}", ParagraphStyle("ins_n",
                        fontSize=9, textColor=PURPLE, fontName="Helvetica-Bold")),
                     Paragraph(ins, s_body)]
                    for i, ins in enumerate(insights)]
        ins_table = Table(ins_data, colWidths=[2.5*cm, 13*cm])
        ins_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [PURPLE_LT, white]),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROUNDEDCORNERS", [4]),
        ]))
        story.append(ins_table)
    story.append(Spacer(1, 0.3*cm))

    # 5. Tendances
    tendances = contenu.get("tendances", [])
    tend_paragraphs = [Paragraph(f"→ {t}", s_bullet) for t in tendances]
    section("5. Tendances identifiées", tend_paragraphs)

    # 6. Limitations
    limitations = contenu.get("limitations", [])
    lim_paragraphs = [Paragraph(f"⚠ {l}", ParagraphStyle("lim",
        fontSize=10, textColor=CORAL, leftIndent=14,
        leading=14, spaceAfter=4)) for l in limitations]
    section("6. Limitations et biais", lim_paragraphs)

    # 7. Conclusion
    section("7. Conclusion", [
        Paragraph(contenu.get("conclusion", ""), s_body)
    ])

    # 8. Sources
    sources = contenu.get("sources", [])
    src_paragraphs = [Paragraph(f"[{i+1}] {s}", ParagraphStyle("src",
        fontSize=9, textColor=GRAY_MID, leftIndent=14,
        leading=13, spaceAfter=3)) for i, s in enumerate(sources) if s]
    if src_paragraphs:
        section("8. Sources consultées", src_paragraphs)

    # Score final
    story.append(Spacer(1, 0.5*cm))
    score_data = [[
        Paragraph(f"Score de fiabilité : {score}/10", ParagraphStyle("score",
            fontSize=11, fontName="Helvetica-Bold", textColor=score_color,
            alignment=TA_CENTER)),
        Paragraph(f"Points forts : {', '.join(evaluation.get('points_forts', []))}", 
            ParagraphStyle("pf", fontSize=9, textColor=GRAY_MID, alignment=TA_CENTER))
    ]]
    score_table = Table(score_data, colWidths=[15.5*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRAY_LT),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(score_table)

    doc.build(story)


def generate(sujet: str, donnees: dict, analyse: dict, evaluation: dict = None) -> str:
    log_info("Writer", "Génération du rapport PDF professionnel")

    if evaluation is None:
        evaluation = {"score": 7, "approuve": True, "points_forts": [], "feedback": ""}

    # Construit le contenu directement depuis les données existantes
    # SANS appel API supplémentaire — économise le quota
    contenu = {
        "resume_executif": analyse.get("resume", ""),
        "introduction": (
            f"Ce rapport présente une analyse approfondie sur le sujet suivant : {sujet}. "
            f"Les informations ont été collectées via des recherches web ciblées et analysées "
            f"sémantiquement par un système multi-agents. "
            f"{analyse.get('resume', '')}"
        ),
        "faits_cles": donnees.get("faits", [])[:6],
        "analyse": (
            f"{analyse.get('resume', '')} "
            f"{analyse.get('conclusion', '')}"
        ),
        "insights": analyse.get("insights", []),
        "tendances": analyse.get("tendances", []),
        "limitations": analyse.get("limitations", []),
        "conclusion": analyse.get("conclusion", ""),
        "sources": [s for s in donnees.get("sources", []) if s]
    }

    # Nom du fichier
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sujet_slug = re.sub(r"[^a-zA-Z0-9]", "_", sujet[:25])
    filename = f"rapport_{sujet_slug}_{timestamp}.pdf"

    # Construit le PDF
    # Construit le PDF
    _build_pdf(sujet, contenu, evaluation, filename)

    # Copie dans le dossier downloads pour téléchargement facile
    import shutil
    downloads_dir = "/workspaces/SemanticResearcher-/RAPPORTS_PDF"
    os.makedirs(downloads_dir, exist_ok=True)
    dest = os.path.join(downloads_dir, filename)
    shutil.copy(filename, dest)

    log_end(filename)

    # Affiche instructions de téléchargement claires
    print("\n" + "="*60)
    print("  RAPPORT PDF PRET AU TELECHARGEMENT")
    print("="*60)
    print(f"\n  Fichier : {filename}")
    print(f"\n  Pour telecharger sur ton PC :")
    print(f"  1. Barre laterale gauche VS Code")
    print(f"  2. Dossier RAPPORTS_PDF")
    print(f"  3. Clic droit sur {filename}")
    print(f"  4. Download...")
    print("="*60 + "\n")

    return dest