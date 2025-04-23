from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io

def generate_pdf(responses, score, max_score, analysis, recommendations, links):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "Rapport d'Audit de Conformité RGPD")

    # Score
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height - 3*cm, f"Score de conformité: {score}/{max_score}")

    # Analysis
    text = c.beginText(2*cm, height - 4*cm)
    text.setFont("Helvetica", 10)
    text.textLines("Analyse des réponses:")
    for line in analysis:
        text.textLine(f"- {line}")
    c.drawText(text)

    # Recommendations
    text = c.beginText(2*cm, height - (6+len(analysis))*cm)
    text.setFont("Helvetica", 10)
    text.textLines("Recommandations:")
    for rec in recommendations:
        text.textLine(f"- {rec}")
    c.drawText(text)

    # Resource links
    text = c.beginText(2*cm, height - (8+len(analysis)+len(recommendations))*cm)
    text.setFont("Helvetica", 10)
    text.textLines("Ressources utiles:")
    for label, url in links.items():
        text.textLine(f"{label}: {url}")
    c.drawText(text)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
