# File: streamlit_app.py
import streamlit as st
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Flowable)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import io
import tempfile

# Custom Flowable for background watermark
class Background(Flowable):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
    def draw(self):
        c = self.canv
        c.drawImage(self.img_path, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True, mask='auto')

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

# Styles and layout
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PDFTitle', parent=styles['Title'], fontSize=24, alignment=1, textColor=colors.HexColor('#1B2631'), spaceAfter=20))
styles.add(ParagraphStyle(name='Intro', parent=styles['BodyText'], fontSize=10, textColor=colors.HexColor('#34495E'), spaceAfter=14))
styles.add(ParagraphStyle(name='Question', parent=styles['Heading2'], fontSize=12, textColor=colors.white, backColor=colors.HexColor('#1B2631'), leftIndent=6, rightIndent=6, spaceAfter=6, spaceBefore=6))
styles.add(ParagraphStyle(name='Response', parent=styles['BodyText'], fontSize=9, textColor=colors.HexColor('#2C3E50'), spaceAfter=6))
styles.add(ParagraphStyle(name='CommentOK', parent=styles['BodyText'], backColor=colors.HexColor('#1F618D'), textColor=colors.white, fontSize=8, leftIndent=6, rightIndent=6, spaceAfter=6, spaceBefore=4))
styles.add(ParagraphStyle(name='CommentKO', parent=styles['BodyText'], backColor=colors.HexColor('#922B21'), textColor=colors.white, fontSize=8, leftIndent=6, rightIndent=6, spaceAfter=6, spaceBefore=4))
styles.add(ParagraphStyle(name='Law', parent=styles['BodyText'], fontSize=7.5, fontName='Helvetica-Oblique', textColor=colors.HexColor('#7F8C8D'), spaceAfter=4))
styles.add(ParagraphStyle(name='Criticity', parent=styles['BodyText'], fontSize=8, textColor=colors.HexColor('#C0392B'), spaceAfter=6))
styles.add(ParagraphStyle(name='Conclusion', parent=styles['BodyText'], fontSize=10, textColor=colors.HexColor('#2C3E50'), spaceBefore=20, leading=14))

CRIT_LEVEL = {i: f"{10-i}/10" for i in range(len(QUESTIONS))}
LAW_TEXT = {0: "Article 5 RGPD – Principes relatifs au traitement des données.",
            1: "Article 12 RGPD – Transparence des informations.",
            3: "Article 37 RGPD – Désignation du DPO.",
            6: "Article 33 RGPD – Notification des violations de données."}

# Generate PDF
def generate_pdf(responses, score, max_score, recommendations, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    flowables = []
    # Background image
    # Replace 'background.png' with actual path if needed
    # flowables.append(Background('background.png'))
    # Title and intro
    flowables.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    flowables.append(Paragraph("Ce rapport de conformité RGPD 2024 met en lumière votre position par rapport aux exigences légales européennes et propose des recommandations adaptées.", styles['Intro']))
    # Chart
    fig, ax = plt.subplots(figsize=(4,1.2))
    ax.bar(['✔️','❌'], [score, max_score-score], color=['#1ABC9C','#E74C3C'])
    ax.set_ylim(0, max_score)
    ax.axis('off')
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(tmp.name, dpi=200, bbox_inches='tight')
    flowables.append(Image(tmp.name, width=16*cm, height=4*cm))
    flowables.append(Spacer(1,12))
    # Sections
    for idx, question in enumerate(QUESTIONS):
        resp = responses.get(idx, '')
        flowables.append(Paragraph(question, styles['Question']))
        flowables.append(Paragraph(f"<b>Votre réponse:</b> {resp}", styles['Response']))
        if resp == 'Oui':
            crit = CRIT_LEVEL[idx]
            # Personalized comment
            comment = tips.get(idx, f"Vous remplissez bien cette exigence. Pour aller plus loin, envisagez une revue annuelle dédiée.")
            flowables.append(Paragraph(f"{comment}", styles['CommentOK']))
            flowables.append(Paragraph(f"Criticité: {crit}", styles['Criticity']))
        else:
            crit = CRIT_LEVEL[idx]
            recomm = recommendations.get(idx, f"Il est essentiel de mettre en place cette pratique pour assurer la conformité.")
            law = LAW_TEXT.get(idx, "Article 6 RGPD – Licéité du traitement.")
            flowables.append(Paragraph(f"{recomm}", styles['CommentKO']))
            flowables.append(Paragraph(law, styles['Law']))
            flowables.append(Paragraph(f"Criticité: {crit}", styles['Criticity']))
        flowables.append(Spacer(1,10))
    # Conclusion
    flowables.append(Paragraph("Conclusion Approfondie", styles['Question']))
    flowables.append(Paragraph(conclusion + " Dans l’optique d’une conformité durable, nous vous recommandons d’intégrer ces actions dans votre gouvernance, de documenter chaque processus et de sensibiliser régulièrement votre équipe. Un audit annuel permettra de mesurer les progrès et d’ajuster votre plan d’action.", styles['Conclusion']))
    doc.build(flowables)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Outil d'Audit de Conformité RGPD")
responses = {i: st.radio(q, ["Oui","Non"], key=i) for i,q in enumerate(QUESTIONS)}
if st.button("Générer le rapport PDF"):
    max_score = len(QUESTIONS)
    score = sum(v=="Oui" for v in responses.values())
    recs = {i: f"Mettre en place: {QUESTIONS[i]}" for i,v in responses.items() if v=="Non"}
    tips = {0: "Limitez la collecte aux données strictement nécessaires.", 1: "Rédigez un texte clair et précis, facilement accessible.", 2: "Tenez à jour votre registre des traitements.", 3: "Nommer un DPO interne ou externe dès maintenant.", 4: "Assurez-vous de localiser les données dans un environnement protégé.", 5: "Réalisez systématiquement une DPIA pour les traitements sensibles.", 6: "Préparez un protocole de réponse aux incidents.", 7: "Utilisez des cases explicites et granuleuses.", 8: "Revoyez vos durées de conservation pour éviter l’excès.", 9: "Organisez des sessions de formation régulières."}
    conclusion = "Votre audit révèle à la fois des points forts à consolider et des marges de progression ciblées. En structurant votre plan d’action autour de ces points et en instaurant une culture RGPD interne, vous sécuriserez vos traitements et renforcerez la confiance de vos parties prenantes."
    pdf = generate_pdf(responses, score, max_score, recs, tips, tips, conclusion)
    st.download_button("Télécharger le rapport PDF", data=pdf, file_name="rapport_rgpd.pdf", mime="application/pdf")
