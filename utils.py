from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import io
import matplotlib.pyplot as plt
import tempfile

# Map des domaines RGPD
DOMAIN_MAP = {
    0: "Collecte de données",
    1: "Politique de confidentialité",
    2: "Registre des traitements",
    3: "DPO",
    4: "Stockage des données",
    5: "Outils tiers",
    6: "Processus de fuite",
    7: "Consentement explicite",
    8: "Rétention des données",
    9: "Formation des salariés",
}

# Couleurs de criticité
CRITICALITY_COLORS = {
    'high': colors.red,
    'medium': colors.orange,
    'low': colors.green,
}

def generate_pdf(responses, score, max_score, recommendations, links_detail, tips, conclusion, chart_fig):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Titres et introduction
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor('#003366'))
    c.drawString(2*cm, height-2*cm, "Rapport d'Audit de Conformité RGPD")
    c.setFont("Helvetica", 10)
    intro = (
        "Ce rapport propose une synthèse de votre conformité au RGPD selon la législation européenne. "
        "Il met en évidence les points de conformité, les manquements critiques et fournit des recommandations."
    )
    text = c.beginText(2*cm, height-2.8*cm)
    text.setFillColor(colors.black)
    text.textLines(intro)
    c.drawText(text)

    # Score encadré
    c.setFillColor(colors.HexColor('#005599'))
    c.rect(2*cm, height-4.5*cm, 6*cm, 1*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2.2*cm, height-4.1*cm, f"Score de conformité: {score}/{max_score}")

    # Insertion du graphique
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
        chart_fig.savefig(img.name, bbox_inches='tight')
        c.drawImage(img.name, 2*cm, height-12*cm, width=12*cm, preserveAspectRatio=True)

    y = height-13*cm

    # Sections par domaine
    for idx, domain in DOMAIN_MAP.items():
        resp = responses[idx]
        # Détermination de la criticité
        if resp == 'Non':
            crit = 'high' if idx in [0,1,6,7] else 'medium'
        else:
            crit = 'low'
        color = CRITICALITY_COLORS[crit]

        # Section domaine
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor('#003366'))
        c.drawString(2*cm, y, domain)
        y -= 0.7*cm

        # Réponse et highlight
        c.setFont("Helvetica", 11)
        c.setFillColor(color)
        c.drawString(3*cm, y, f"Réponse: {resp}")
        y -= 0.7*cm

        if resp == 'Non':
            # Bouton recommandation
            c.setFillColor(colors.HexColor('#005599'))
            c.rect(3*cm, y-0.2*cm, 12*cm, 0.8*cm, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(3.2*cm, y, "En savoir plus")
            # Lien URL et citation
            url, citation = links_detail.get(idx, (None, None))
            if url:
                c.linkURL(url, (3*cm, y-0.2*cm, 15*cm, y+0.6*cm))
            y -= 1*cm
            if citation:
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(colors.black)
                c.drawString(3.2*cm, y, citation)
                y -= 0.7*cm

        # Encadré Tip
        tip = tips.get(idx)
        if tip:
            c.setFillColor(colors.HexColor('#f2f9ff'))
            c.rect(2*cm, y-0.2*cm, 16*cm, 1*cm, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(2.2*cm, y, tip)
            y -= 1.2*cm

        # Nouvelle page si nécessaire
        if y < 4*cm:
            c.showPage()
            y = height-2*cm

    # Conclusion
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor('#003366'))
    c.drawString(2*cm, y, "Conclusion et ressources complémentaires")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    text = c.beginText(2*cm, y)
    text.textLines(conclusion)
    c.drawText(text)

    c.save()
    buffer.seek(0)
    return buffer
