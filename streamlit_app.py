import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import generate_pdf

# Questionnaire definition
QUESTIONS = [
    {"q": "Collectez-vous des données personnelles de vos clients ?", "type": "bool"},
    {"q": "Avez-vous mis à disposition une politique de confidentialité claire sur votre site ?", "type": "bool"},
    {"q": "Conservez-vous un registre des traitements de données ?", "type": "bool"},
    {"q": "Avez-vous désigné un DPO (Délégué à la protection des données) ?", "type": "bool"},
    {"q": "Les données sont-elles stockées dans l’UE ou dans un pays avec un niveau de protection adéquat ?", "type": "bool"},
    {"q": "Utilisez-vous des outils tiers (CRM, newsletter, analytics) ? Lesquels ?", "type": "text"},
    {"q": "Avez-vous mis en place un processus en cas de fuite de données ?", "type": "bool"},
    {"q": "Vos formulaires incluent-ils une case à cocher pour consentement explicite ?", "type": "bool"},
    {"q": "Conservez-vous les données plus de 3 ans sans action de l'utilisateur ?", "type": "bool"},
    {"q": "Avez-vous informé vos salariés de leurs droits en matière de données ?", "type": "bool"},
]

st.title("Outil d'Audit de Conformité RGPD")

# Collect responses
responses = {}
for idx, item in enumerate(QUESTIONS):
    if item['type'] == 'bool':
        responses[idx] = st.radio(item['q'], ["Oui", "Non"], key=idx)
    else:
        responses[idx] = st.text_input(item['q'], key=idx)

if st.button("Générer le rapport PDF"):
    # Scoring
    max_score = sum(1 for q in QUESTIONS if q['type']=='bool')
    score = sum(1 for idx,q in enumerate(QUESTIONS) if q['type']=='bool' and responses[idx]=="Oui")

    # Analysis and recommendations
    analysis = []
    recommendations = []
    links = {
        "CNIL Guide": "https://www.cnil.fr/fr/rgpd-de-quoi-parle-t-on",
        "Documentation UE": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32016R0679",
    }
    for idx,q in enumerate(QUESTIONS):
        if q['type']=='bool' and responses[idx]=="Non":
            analysis.append(f"{q['q']} -> Non")
            recommendations.append(f"Mettre en place: {q['q']}")

    # Chart
    fig, ax = plt.subplots()
    ax.bar(['Conformité', 'Manquants'], [score, max_score-score])
    ax.set_ylim(0, max_score)
    st.pyplot(fig)

    # Generate PDF
    pdf_buffer = generate_pdf(responses, score, max_score, analysis, recommendations, links)
    st.download_button(
        label="Télécharger le rapport PDF",
        data=pdf_buffer,
        file_name="rapport_rgpd.pdf",
        mime="application/pdf"
    )
