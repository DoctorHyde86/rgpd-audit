import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
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
styles.add(ParagraphStyle(name='PDFTitle', fontSize=22, alignment=1, textColor=colors.HexColor('#1B2631'), spaceAfter=20))
styles.add(ParagraphStyle(name='Intro', fontSize=10, textColor=colors.HexColor('#34495E'), spaceAfter=14))
styles.add(ParagraphStyle(name='Question', fontSize=12, textColor=colors.white, backColor=colors.HexColor('#1B2631'),
                          leftIndent=6, rightIndent=6, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='Response', fontSize=9, textColor=colors.HexColor('#2C3E50'), spaceAfter=6))
styles.add(ParagraphStyle(name='CommentOK', backColor=colors.HexColor('#1F618D'), textColor=colors.white,
                          fontSize=8, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=6))
styles.add(ParagraphStyle(name='CommentKO', backColor=colors.HexColor('#922B21'), textColor=colors.white,
                          fontSize=8, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=6))
styles.add(ParagraphStyle(name='Law', fontSize=7.5, fontName='Helvetica-Oblique', textColor=colors.HexColor('#7F8C8D'),
                          spaceAfter=4))
styles.add(ParagraphStyle(name='Criticity', fontSize=8, textColor=colors.HexColor('#C0392B'), spaceAfter=6))
styles.add(ParagraphStyle(name='Conclusion', fontSize=10, textColor=colors.HexColor('#2C3E50'), spaceBefore=20, leading=14))

# Criticité & textes de loi
CRIT_LEVEL = {i: f"{10-i}/10" for i in range(len(QUESTIONS))}
LAW_TEXT = {
    0: "Article 5 RGPD – Principes relatifs au traitement des données.",
    1: "Article 12 RGPD – Transparence des informations.",
    3: "Article 37 RGPD – Désignation du DPO.",
    6: "Article 33 RGPD – Notification des violations de données."
}

def generate_pdf(responses, score, max_score, recommendations, tips, conclusion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    flowables = []

    # Titre & intro
    flowables.append(Paragraph("Rapport d'Audit de Conformité RGPD", styles['PDFTitle']))
    flowables.append(Paragraph(
        "Ce rapport de conformité RGPD 2024 met en lumière votre position par rapport aux exigences légales européennes "
        "et propose des recommandations adaptées.", styles['Intro']))

    # Graphique
    fig, ax = plt.subplots(figsize=(4, 1.2))
    ax.bar(['✔️','❌'], [score, max_score-score], color=['#1ABC9C','#E74C3C'])
    ax.set_ylim(0, max_score)
    ax.axis('off')
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(tmp.name, dpi=200, bbox_inches='tight')
    flowables.append(Image(tmp.name, width=16*cm, height=4*cm))
    flowables.append(Spacer(1, 12))

    # Sections détaillées
    for idx, question in enumerate(QUESTIONS):
        resp = responses[idx]
        flowables.append(Paragraph(question, styles['Question']))
        flowables.append(Paragraph(f"<b>Votre réponse:</b> {resp}", styles['Response']))

        crit = CRIT_LEVEL[idx]
        if resp == "Oui":
            comment = tips.get(idx, "Très bien ! Pensez à réviser annuellement cette pratique.")
            flowables.append(Paragraph(comment, styles['CommentOK']))
            flowables.append(Paragraph(f"Criticité positive: {crit}", styles['Criticity']))
        else:
            recomm = recommendations.get(idx, "Il est crucial d'adresser ce point sans délai.")
            law = LAW_TEXT.get(idx, "Article 6 RGPD – Licéité du traitement.")
            flowables.append(Paragraph(recomm, styles['CommentKO']))
            flowables.append(Paragraph(law, styles['Law']))
            flowables.append(Paragraph(f"Criticité: {crit}", styles['Criticity']))
        flowables.append(Spacer(1, 10))

    # Conclusion enrichie
    flowables.append(Paragraph("Conclusion Approfondie", styles['Question']))
    flowables.append(Paragraph(
        conclusion +
        " Pour aller plus loin, établissez un plan d’action structuré, associez vos processus RGPD à votre gouvernance "
        "et formez régulièrement vos équipes. Un audit périodique (au moins annuel) permettra de maintenir ce niveau de conformité.",
        styles['Conclusion']))

    doc.build(flowables)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Outil d'Audit de Conformité RGPD")
responses = {i: st.radio(q, ["Oui","Non"], key=i) for i,q in enumerate(QUESTIONS)}
if st.button("Générer le rapport PDF"):
    max_score = len(QUESTIONS)
    score = sum(v == "Oui" for v in responses.values())
    recs = {i: f"Mettre en place: {QUESTIONS[i]}" for i,v in responses.items() if v=="Non"}
    tips = {
        0: "Limitez la collecte aux données strictement nécessaires.",
        1: "Rédigez un texte clair et facilement compréhensible.",
        2: "Mettez à jour systématiquement votre registre.",
        3: "DPO nommé, pensez à le former et l'impliquer.",
        4: "Vérifiez la localisation et la protection de vos serveurs.",
        5: "Planifiez votre DPIA pour tout nouveau projet.",
        6: "Élaborez un protocole de réponse aux fuites.",
        7: "Adoptez des consentements granulaires et explicites.",
        8: "Appliquez des durées de conservation adaptées.",
        9: "Organisez des sessions de sensibilisation annuelles."
    }
    conclusion = (
        "Votre audit révèle à la fois des points forts à consolider et des marges de progression. "
        "Structurer un plan d’action et instaurer une culture RGPD transversale garantira la durabilité de votre conformité."
    )
    pdf = generate_pdf(responses, score, max_score, recs, tips, conclusion)
    st.download_button("Télécharger le rapport PDF", data=pdf, file_name="rapport_rgpd.pdf", mime="application/pdf")
