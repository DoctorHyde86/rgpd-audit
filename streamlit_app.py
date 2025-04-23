import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
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
styles.add(ParagraphStyle(name='PDFTitle', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#2C3E50'), spaceAfter=14))
styles.add(ParagraphStyle(name='IntroMetrics', parent=styles['BodyText'], fontSize=9, textColor=colors.HexColor('#7F8C8D'), spaceAfter=12))
styles.add(ParagraphStyle(name='SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#34495E'), spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name='NormalText', parent=styles['BodyText'], fontSize=9, leading=11))
styles.add(ParagraphStyle(name='TipBox', parent=styles['BodyText'], backColor=colors.HexColor('#ECF0F1'), borderPadding=6, fontSize=8, leading=10, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='LinkText', parent=styles['BodyText'], textColor=colors.HexColor('#2980B9'), fontSize=9, spaceBefore=2, spaceAfter=2))
styles.add(ParagraphStyle(name='CitationText', parent=styles['BodyText'], fontSize=8, fontName='Helvetica-Oblique', leading=9, spaceBefore=2, spaceAfter=4))
CRIT_COLORS = {True: '#FDEDEC', False: '#E8F8F5'}

def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    # Title and intro
    story.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    intro = ("Ce rapport synthétise votre niveau de conformité RGPD. "
             "Vous retrouvez vos points forts, les lacunes critiques et nos recommandations.")
    metrics = ("Metrics clés 2024 (Europe):\n"
               "- 2 086 sanctions prononcées, totalisant 4,48 Md€ de montant de sanctions.\n"
               "- 33% de baisse des amendes en 2024 (1,2 Md€) par rapport à 2023.\n"
               "- 48% des entreprises déclarent un processus de gestion des fuites formalisé.")
    story.append(Paragraph(intro, styles['NormalText']))
    story.append(Paragraph(metrics, styles['IntroMetrics']))
    story.append(Spacer(1, 8))
    # Score chart
    story.append(Paragraph(f"<b>Score de conformité:</b> {score}/{max_score}", styles['NormalText']))
    fig, ax = plt.subplots(figsize=(4, 2)); ax.bar(['Conformité','Manquants'], [score, max_score-score], color=['#27AE60','#C0392B']); ax.set_ylim(0, max_score)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        fig.savefig(img.name, bbox_inches='tight', dpi=300); story.append(Image(img.name, width=10*cm, height=5*cm))
    story.append(Spacer(1, 12))
    # Sections
    for idx, question in enumerate(QUESTIONS):
        resp = responses.get(idx, '')
        color = CRIT_COLORS[resp=='Non']
        story.append(Paragraph(question, styles['SectionHeading']))
        resp_style = ParagraphStyle(name=f"Resp{idx}", parent=styles['BodyText'], backColor=colors.HexColor(color), fontSize=8, leading=10, spaceAfter=4, leftIndent=6)
        story.append(Paragraph(f"<b>Réponse:</b> {resp}", resp_style))
        if resp=='Non':
            if idx in recommendations: story.append(Paragraph(recommendations[idx], styles['NormalText']))
            if idx in links_detail:
                url, cit = links_detail[idx]; story.append(Paragraph(f"<link href='{url}'>Voir documentation CNIL</link>", styles['LinkText'])); story.append(Paragraph(cit, styles['CitationText']))
        if idx in tips: story.append(Paragraph(f"<b>Tip:</b> {tips[idx]}", styles['TipBox']))
        story.append(Spacer(1, 8))
    # Conclusion
    story.append(Paragraph("Conclusion", styles['SectionHeading'])); story.append(Paragraph(conclusion, styles['NormalText']))
    doc.build(story); buffer.seek(0); return buffer

# Streamlit UI
st.title("Outil d'Audit de Conformité RGPD")
responses = {i: st.radio(q, ["Oui","Non"], key=i) for i,q in enumerate(QUESTIONS)}
if st.button("Générer le rapport PDF"):
    max_score, score = len(QUESTIONS), sum(1 for v in responses.values() if v=="Oui")
    recs = {i:f"Mettre en place: {QUESTIONS[i]}" for i,v in responses.items() if v=="Non"}
    links = {0:("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#article6","« Le traitement n'est licite que si... »"),3:("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4#article37","« Article 37 – DPO »")}
    tips = {0:"Limitez la collecte aux données strictement nécessaires.",7:"Privilégiez le consentement granulaire."}
    conclusion = "Pour aller plus loin, consultez la CNIL et planifiez une revue annuelle."
    pdf = generate_pdf(responses,score,max_score,recs,links,tips,conclusion)
    st.download_button("Télécharger le rapport PDF", data=pdf, file_name="rapport_rgpd.pdf", mime="application/pdf")
