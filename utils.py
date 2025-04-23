from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import io
import tempfile

# Questionnaire
QUESTIONS = [
    "Collectez-vous des données personnelles de vos clients ?",
    "Avez-vous mis à disposition une politique de confidentialité claire sur votre site ?",
    "Conservez-vous un registre des traitements de données ?",
    "Avez-vous désigné un DPO (Délégué à la protection des données) ?",
    "Les données sont-elles stockées dans l’UE ou dans un pays avec un niveau de protection adéquat ?",
    "Avez-vous réalisé une Analyse d'Impact relative à la Protection des Données (DPIA) ?",
    "Avez-vous mis en place un processus en cas de fuite de données ?",
    "Vos formulaires incluent-ils une case à cocher pour consentement explicite ?",
    "Conservez-vous les données plus de 3 ans sans action de l'utilisateur ?",
    "Avez-vous informé vos salariés de leurs droits en matière de données ?",
]

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PDFTitle', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#2C3E50'), spaceAfter=14))
styles.add(ParagraphStyle(name='IntroMetrics', parent=styles['BodyText'], fontSize=9, textColor=colors.HexColor('#7F8C8D'), spaceAfter=12))
styles.add(ParagraphStyle(name='SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#34495E'), spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name='NormalText', parent=styles['BodyText'], fontSize=9, leading=11))
styles.add(ParagraphStyle(name='TipBox', parent=styles['BodyText'], backColor=colors.HexColor('#ECF0F1'), borderPadding=6, fontSize=8, leading=10, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='LinkText', parent=styles['BodyText'], textColor=colors.HexColor('#2980B9'), fontSize=9, spaceBefore=2, spaceAfter=2))
styles.add(ParagraphStyle(name='CitationText', parent=styles['BodyText'], fontSize=8, fontName='Helvetica-Oblique', leading=9, spaceBefore=2, spaceAfter=4))

# Colors for non/ok
CRIT_COLORS = {
    True: '#FDEDEC',   # non-conform
    False: '#E8F8F5',  # conform
}

def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Title
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    # Intro and metrics
    intro = (
        "Ce rapport synthétise votre niveau de conformité RGPD. "
        "Vous retrouvez vos points forts, les lacunes critiques et nos recommandations."
    )
    metrics = (
        "Metrics clés 2024 (Europe):
"
        "- 2 086 sanctions prononcées, totalisant 4,48 Md€ de montant de sanctions.
"
        "- 33% de baisse des amendes en 2024 (1,2 Md€) par rapport à 2023.
"
        "- 48% des entreprises déclarent un processus de gestion des fuites formalisé."
    )
    story.append(Paragraph(intro, styles['NormalText']))
    story.append(Paragraph(metrics, styles['IntroMetrics']))
    story.append(Spacer(1, 8))

    # Score and chart
    story.append(Paragraph(f"<b>Score de conformité:</b> {score}/{max_score}", styles['NormalText']))
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.bar(['Conformité', 'Manquants'], [score, max_score - score], color=['#27AE60', '#C0392B'])
    ax.set_ylim(0, max_score)
    ax.set_xticklabels(['Conformité', 'Manquants'], fontsize=8)
    ax.set_yticklabels([str(int(t)) for t in ax.get_yticks()], fontsize=8)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        fig.savefig(img.name, bbox_inches='tight', dpi=300)
        story.append(Image(img.name, width=10*cm, height=5*cm))
    story.append(Spacer(1, 12))

    # Sections for each question
    for idx, question in enumerate(QUESTIONS):
        resp = responses.get(idx, '')
        color_hex = CRIT_COLORS[resp == 'Non']

        # Section heading
        story.append(Paragraph(question, styles['SectionHeading']))
        
        # Response box
        resp_style = ParagraphStyle(
            name=f"RespStyle{idx}", parent=styles['BodyText'],
            backColor=colors.HexColor(color_hex), fontSize=8, leading=10,
            spaceAfter=4, leftIndent=6
        )
        story.append(Paragraph(f"<b>Réponse:</b> {resp}", resp_style))

        if resp == 'Non':
            if idx in recommendations:
                story.append(Paragraph(recommendations[idx], styles['NormalText']))
            if idx in links_detail:
                url, citation = links_detail[idx]
                story.append(Paragraph(f"<link href='{url}'>Voir documentation CNIL</link>", styles['LinkText']))
                story.append(Paragraph(citation, styles['CitationText']))

        if idx in tips:
            story.append(Paragraph(f"<b>Tip:</b> {tips[idx]}", styles['TipBox']))

        story.append(Spacer(1, 8))

    # Conclusion
    story.append(Paragraph("Conclusion", styles['SectionHeading']))
    story.append(Paragraph(conclusion, styles['NormalText']))

    doc.build(story)
    buffer.seek(0)
    return buffer
