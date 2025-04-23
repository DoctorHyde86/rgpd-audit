from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import io
import tempfile

# Map des domaines RGPD
DOMAIN_MAP = {
    0: "Collecte de données",
    1: "Politique de confidentialité",
    2: "Registre des traitements",
    3: "DPO",
    4: "Stockage des données",
    5: "Outils tiers",
    6: "Processus de fuite",
    7: "Consentement explicite",
    8: "Rétention des données",
    9: "Formation des salariés",
}

# Couleurs de criticité
CRITICALITY_COLORS = {
    'high': colors.red,
    'medium': colors.orange,
    'low': colors.green,
}

# Styles personnalisés
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#003366'), spaceAfter=12))
styles.add(ParagraphStyle(name='HeadingStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#003366'), spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name='NormalStyle', parent=styles['BodyText'], fontSize=10, leading=12))
styles.add(ParagraphStyle(name='TipStyle', parent=styles['BodyText'], backColor=colors.HexColor('#f2f9ff'), borderPadding=6, fontSize=9, leading=11, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='LinkStyle', parent=styles['BodyText'], textColor=colors.HexColor('#005599'), fontSize=10, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='CitationStyle', parent=styles['BodyText'], fontSize=9, fontName='Helvetica-Oblique', leading=11, spaceBefore=2, spaceAfter=4))


def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Titre et introduction
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['TitleStyle']))
    intro_text = (
        "Ce rapport propose une synthèse de votre conformité au RGPD selon la législation européenne. "
        "Il met en évidence les points de conformité, les manquements critiques et fournit des recommandations."
    )
    story.append(Paragraph(intro_text, styles['NormalStyle']))
    story.append(Spacer(1, 12))

    # Score encadré
    score_table = Table([[f"Score de conformité: <b>{score}/{max_score}</b>"]], colWidths=[6*cm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#005599')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # Graphique
    fig, ax = plt.subplots()
    ax.bar(["Conformité", "Manquants"], [score, max_score-score])
    ax.set_ylim(0, max_score)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        fig.savefig(img.name, bbox_inches='tight')
        story.append(Image(img.name, width=16*cm, height=9*cm))
    story.append(Spacer(1, 12))

    # Sections par domaine
    for idx, domain in DOMAIN_MAP.items():
        resp = responses.get(idx, '')
        crit_level = 'low' if resp == 'Oui' else ('high' if idx in [0,1,6,7] else 'medium')
        color = CRITICALITY_COLORS[crit_level]

        # Titre domaine
        story.append(Paragraph(domain, styles['HeadingStyle']))
        # Réponse
        response_para = Paragraph(
            f"<b>Réponse:</b> {resp}",
            ParagraphStyle('RespStyle', parent=styles['BodyText'], backColor=color, fontSize=11, leading=13, spaceAfter=6, leftIndent=6)
        )
        story.append(response_para)

        # Recommandation et lien
        if resp == 'Non':
            link_info = links_detail.get(idx)
            if link_info:
                url, citation = link_info
                story.append(Paragraph(f"<link href='{url}'>En savoir plus sur le site CNIL</link>", styles['LinkStyle']))
                story.append(Paragraph(citation, styles['CitationStyle']))

        # Tip
        tip_text = tips.get(idx)
        if tip_text:
            story.append(Paragraph(f"<b>Tip:</b> {tip_text}", styles['TipStyle']))

        story.append(Spacer(1, 12))
        story.append(PageBreak())

    # Conclusion
    story.append(Paragraph("Conclusion et ressources complémentaires", styles['HeadingStyle']))
    story.append(Paragraph(conclusion, styles['NormalStyle']))

    doc.build(story)
    buffer.seek(0)
    return buffer
