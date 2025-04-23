from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import io
import tempfile

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#003366')))
styles.add(ParagraphStyle(name='SectionHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#003366'), spaceBefore=12))
styles.add(ParagraphStyle(name='Normal', parent=styles['BodyText'], fontSize=10, leading=12))
styles.add(ParagraphStyle(name='Tip', parent=styles['BodyText'], backColor=colors.HexColor('#f2f9ff'), borderPadding=6, fontSize=9, leading=11, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='Link', parent=styles['BodyText'], textColor=colors.HexColor('#005599'), fontSize=10, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='Citation', parent=styles['BodyText'], fontSize=9, fontName='Helvetica-Oblique', leading=11, spaceBefore=2, spaceAfter=4))

def generate_pdf(responses, score, max_score, recommendations, links, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Introduction
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['Title']))
    intro = ("Ce rapport synthétise votre niveau de conformité RGPD. "
             "Vous retrouvez vos points forts, les lacunes critiques et nos recommandations.")
    story.append(Paragraph(intro, styles['Normal']))
    story.append(Spacer(1, 12))

    # Score and chart
    story.append(Paragraph(f"<b>Score de conformité:</b> {score}/{max_score}", styles['Normal']))
    fig, ax = plt.subplots()
    ax.bar(['Conformité', 'Manquants'], [score, max_score - score])
    ax.set_ylim(0, max_score)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        fig.savefig(img.name, bbox_inches='tight')
        story.append(Image(img.name, width=16*cm, height=9*cm))
    story.append(Spacer(1, 12))

    # Sections
    for idx, question in enumerate(responses.keys()):
        resp = responses[idx]
        crit = 'red' if resp == 'Non' else 'green'
        story.append(Paragraph(question, styles['SectionHeading']))
        story.append(Paragraph(f"<b>Réponse:</b> {resp}", ParagraphStyle('Resp', parent=styles['BodyText'], backColor=colors.HexColor('#' + ('FFCCCC' if crit=='red' else 'CCFFCC')), fontSize=10, leading=12, spaceAfter=6, leftIndent=6)))
        if resp == 'Non':
            if idx in recommendations:
                story.append(Paragraph(recommendations[idx], styles['Normal']))
            if idx in links:
                url, citation = links[idx]
                story.append(Paragraph(f"<link href='{url}'>Voir documentation CNIL</link>", styles['Link']))
                story.append(Paragraph(citation, styles['Citation']))
        if idx in tips:
            story.append(Paragraph(f"<b>Tip:</b> {tips[idx]}", styles['Tip']))
        story.append(Spacer(1, 12))

    # Conclusion
    story.append(Paragraph("Conclusion", styles['SectionHeading']))
    story.append(Paragraph(conclusion, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer
