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
    "Utilisez-vous des outils tiers (CRM, newsletter, analytics) ? Lesquels ?",
    "Avez-vous mis en place un processus en cas de fuite de données ?",
    "Vos formulaires incluent-ils une case à cocher pour consentement explicite ?",
    "Conservez-vous les données plus de 3 ans sans action de l'utilisateur ?",
    "Avez-vous informé vos salariés de leurs droits en matière de données ?",
]

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PDFTitle', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#003366'), spaceAfter=12))
styles.add(ParagraphStyle(name='SectionHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#003366'), spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name='NormalText', parent=styles['BodyText'], fontSize=10, leading=12))
styles.add(ParagraphStyle(name='TipBox', parent=styles['BodyText'], backColor=colors.HexColor('#f2f9ff'), borderPadding=6, fontSize=9, leading=11, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='LinkText', parent=styles['BodyText'], textColor=colors.HexColor('#005599'), fontSize=10, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='CitationText', parent=styles['BodyText'], fontSize=9, fontName='Helvetica-Oblique', leading=11, spaceBefore=2, spaceAfter=4))

# Colors for non/ok
CRIT_COLORS = {
    True: '#FFCCCC',   # non-conform
    False: '#CCFFCC',  # conform
}

def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Title and intro
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    intro = (
        "Ce rapport synthétise votre niveau de conformité RGPD. "
        "Vous retrouvez vos points forts, les lacunes critiques et nos recommandations."
    )
    story.append(Paragraph(intro, styles['NormalText']))
    story.append(Spacer(1, 12))

    # Score and chart
    story.append(Paragraph(f"<b>Score de conformité:</b> {score}/{max_score}", styles['NormalText']))
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(['Conformité', 'Manquants'], [score, max_score - score])
    ax.set_ylim(0, max_score)
    ax.set_ylabel('Nombre de points')
    ax.set_xlabel('Catégorie')
    for tick in ax.get_xticklabels():
        tick.set_fontsize(10)
    for tick in ax.get_yticklabels():
        tick.set_fontsize(10)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        fig.savefig(img.name, bbox_inches='tight', dpi=300)
        story.append(Image(img.name, width=16*cm, height=9*cm))
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
            backColor=colors.HexColor(color_hex), fontSize=10, leading=12,
            spaceAfter=6, leftIndent=6
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

        story.append(Spacer(1, 12))

    # Conclusion
    story.append(Paragraph("Conclusion", styles['SectionHeading']))
    story.append(Paragraph(conclusion, styles['NormalText']))

    doc.build(story)
    buffer.seek(0)
    return buffer
