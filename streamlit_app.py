import streamlit as st
from utils import generate_pdf

# Questionnaire (synchronisé avec utils.py)
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

st.title("Outil d'Audit de Conformité RGPD")

# Collecte des réponses
responses = {idx: st.radio(q, ["Oui", "Non"], key=idx) for idx, q in enumerate(QUESTIONS)}

if st.button("Générer le rapport PDF"):
    max_score = len(QUESTIONS)
    score = sum(1 for ans in responses.values() if ans == "Oui")

    # Préparer recommandations, liens et tips
    recommendations = {idx: f"Mettre en place: {QUESTIONS[idx]}" for idx, ans in responses.items() if ans == "Non"}
    links_detail = {
        0: ("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#article6",
            "« Le traitement n'est licite que si... » (Article 6 RGPD)"),
        3: ("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4#article37",
            "« Article 37 – Désignation du DPO. »"),
    }
    tips = {
        0: "Limitez la collecte aux données strictement nécessaires et définissez des durées de conservation.",
        7: "Privilégiez le consentement granulaire et documentez chaque choix de l'utilisateur.",
    }
    conclusion = (
        "Pour aller plus loin, consultez les ressources CNIL et prévoyez une revue annuelle. "
        "Mettez en place une gouvernance transverse et formez régulièrement vos équipes."
    )

    # Génération du PDF
    pdf = generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion)
    st.download_button(
        label="Télécharger le rapport PDF",
        data=pdf,
        file_name="rapport_rgpd.pdf",
        mime="application/pdf"
    )
