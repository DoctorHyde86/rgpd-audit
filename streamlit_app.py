# File: streamlit_app.py
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import io
import tempfile

# Questionnaire definitions
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

# PDF generation function inlined
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PDFTitle', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#2C3E50'), spaceAfter=16))
styles.add(ParagraphStyle(name='SectionBox', parent=styles['BodyText'], fontSize=10, backColor=colors.white, leftIndent=6, rightIndent=6, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='Question', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#2C3E50'), spaceAfter=4))
styles.add(ParagraphStyle(name='Response', parent=styles['BodyText'], fontSize=9, spaceAfter=4))
styles.add(ParagraphStyle(name='CommentOK', parent=styles['BodyText'], backColor=colors.HexColor('#D5F5E3'), fontSize=8, spaceAfter=4, borderPadding=4))
styles.add(ParagraphStyle(name='CommentKO', parent=styles['BodyText'], backColor=colors.HexColor('#FADBD8'), fontSize=8, spaceAfter=4, borderPadding=4))
styles.add(ParagraphStyle(name='Law', parent=styles['BodyText'], fontSize=7.5, fontName='Helvetica-Oblique', textColor=colors.HexColor('#7F8C8D'), spaceAfter=4))
styles.add(ParagraphStyle(name='Criticity', parent=styles['BodyText'], fontSize=7.5, textColor=colors.HexColor('#C0392B'), spaceAfter=4))
styles.add(ParagraphStyle(name='Conclusion', parent=styles['BodyText'], fontSize=9, leading=12, spaceBefore=12))

# Criticality ratings
CRIT_LEVEL = {0: '10/10', 1: '9/10', 2: '8/10', 3: '7/10', 4: '6/10', 5: '5/10', 6: '7/10', 7: '9/10', 8: '6/10', 9: '8/10'}

# Law citations
LAW_TEXT = {
    0: "Article 5 RGPD – Principes relatifs au traitement des données.",
    1: "Article 12 RGPD – Transparence des informations.",
    3: "Article 37 RGPD – Désignation du DPO.",
    6: "Article 33 RGPD – Notification des violations de données.",
}

def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    story = []
    # Title
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    story.append(Spacer(1, 8))
    # Score chart
    fig, ax = plt.subplots(figsize=(3, 1.2))
    ax.bar(['OK','Manquants'], [score, max_score-score], color=['#27AE60','#C0392B']);
    ax.set_ylim(0, max_score); ax.tick_params(labelsize=8)
    img_buf = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(img_buf.name, bbox_inches='tight', dpi=300)
    story.append(Image(img_buf.name, width=8*cm, height=3*cm))
    story.append(Spacer(1, 12))
    # Sections with frames
    for idx, question in enumerate(QUESTIONS):
        # Container table
        data = []
        resp = responses.get(idx, '')
        # Question
        data.append([Paragraph(question, styles['Question'])])
        # Response
        data.append([Paragraph(f"<b>Réponse:</b> {resp}", styles['Response'])])
        # Comment
        if resp == 'Oui':
            comment = tips.get(idx, "Vous êtes en conformité. Conseil: continuez à maintenir vos bonnes pratiques et reconsidérez annuellement vos processus.")
            style = styles['CommentOK']
            data.append([Paragraph(f"<b>Positif:</b> {comment}", style)])
        else:
            comm = recommendations.get(idx, "Non conforme, renforcer ce point dès que possible.")
            law = LAW_TEXT.get(idx, "Article 6 RGPD – Licéité du traitement.")
            crit = CRIT_LEVEL.get(idx, '5/10')
            style = styles['CommentKO']
            data.append([Paragraph(f"<b>Importance:</b> Renforcer cette pratique. {comm}", style)])
            data.append([Paragraph(law, styles['Law'])])
            data.append([Paragraph(f"Criticité: {crit}", styles['Criticity'])])
        
        tbl = Table(data, colWidths=[18*cm])
        tbl.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECF0F1')),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 8))
        story.append(Spacer(1, 8))
    # Conclusion extended
    story.append(Paragraph("Conclusion approfondie", styles['SectionHeading']))
    story.append(Paragraph(conclusion + " Cette analyse met en lumière vos axes d'amélioration prioritaires. Il est recommandé de mettre en place un plan d'action structuré, impliquant à la fois la gouvernance, la technique et la formation continue. N'oubliez pas de documenter chaque processus et de revoir votre conformité au moins une fois par an. Pour aller plus loin, explorez les ressources CNIL, les guides sectoriels et envisagez l'accompagnement d'un expert RGPD.", styles['Conclusion']))
    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Outil d'Audit de Conformité RGPD")
responses = {i: st.radio(q, ["Oui","Non"], key=i) for i, q in enumerate(QUESTIONS)}
if st.button("Générer le rapport PDF"):
    max_score, score = len(QUESTIONS), sum(v=="Oui" for v in responses.values())
    recs = {i: f"Mettre en place: {QUESTIONS[i]}" for i,v in responses.items() if v=="Non"}
    links = {0:("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#article6","« Le traitement n'est licite que si... »"), 3:("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4#article37","« Article 37 – Désignation du DPO. »")}
    tips = {0:"Limitez la collecte aux données strictement nécessaires.", 7:"Privilégiez le consentement granulaire."}
    conclusion = "Pour aller plus loin, consultez la CNIL et établissez un plan RGPD robuste, associant gouvernance, processus et formation continue."
    pdf = generate_pdf(responses, score, max_score, recs, links, tips, conclusion)
    st.download_button("Télécharger le rapport PDF", data=pdf, file_name="rapport_rgpd.pdf", mime="application/pdf")
