import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import generate_pdf

# Questions et domaines (ordre synchronisé avec utils.DOMAIN_MAP)
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

st.title("Outil d'Audit de Conformité RGPD")

# Collecte des réponses
responses = {}
for i, q in enumerate(QUESTIONS):
    if i == 5:  # question textuelle
        responses[i] = st.text_input(q, key=i)
    else:
        responses[i] = st.radio(q, ["Oui", "Non"], key=i)

if st.button("Générer le rapport PDF"):
    # Score
    max_score = sum(1 for i in range(10) if i != 5)
    score = sum(1 for i, ans in responses.items() if i != 5 and ans == "Oui")

    # Recommandations et liens légaux
    recommendations = {i: f"Mettre en place: {QUESTIONS[i]}" for i in range(10) if i != 5 and responses[i] == "Non"}
    links_detail = {
        0: ("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#article6",
            "« Le traitement n'est licite que si... » (Article 6 RGPD)"),
        3: ("https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4#article37",
            "« Article 37 – Désignation du DPO. »"),
        # Autres: renvoi vers guide CNIL général
    }

    # Tips par domaine
    tips = {
        0: "Limitez la collecte aux données strictement nécessaires et définissez des durées de conservation.",
        7: "Privilégiez le consentement granulaire et documentez chaque choix de l'utilisateur.",
    }

    # Graphique
    fig, ax = plt.subplots()
    ax.bar(["Conformité", "Manquants"], [score, max_score-score])
    ax.set_ylim(0, max_score)

    # Conclusion
    conclusion = (
        "Pour aller plus loin, consultez les ressources CNIL et prévoyez une revue annuelle. "
        "Mettez en place une gouvernance transverse et formez régulièrement vos équipes."
    )

    # Génération PDF
    pdf = generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion, fig)
    st.download_button(
        label="Télécharger le rapport PDF",
        data=pdf,
        file_name="rapport_rgpd.pdf",
        mime="application/pdf"
    )
