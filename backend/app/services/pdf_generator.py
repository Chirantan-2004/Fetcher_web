from io import BytesIO
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from app.schemas import CanonicalDocument

def generate_pdf(document: CanonicalDocument) -> bytes:
    output = BytesIO(); styles = getSampleStyleSheet(); styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER)); story = [Paragraph(document.title or "Fetched document", styles["TitleCenter"]), Paragraph(document.source_url, styles["Normal"]), Spacer(1, .2*inch), Paragraph("Metadata", styles["Heading1"]), Paragraph(f"Domain: {document.domain} | Words: {document.statistics.word_count}", styles["BodyText"]), Paragraph("Extracted Content", styles["Heading1"])]
    for section in document.content["sections"]:
        if section.heading: story.append(Paragraph(section.heading, styles[f"Heading{min(section.level, 4)}"]))
        for block in section.blocks:
            if block.type in {"paragraph", "quote", "code"}: story.append(Paragraph((block.text or "").replace("&", "&amp;").replace("<", "&lt;"), styles["BodyText"])); story.append(Spacer(1, .08*inch))
            elif block.type == "list":
                for item in block.items: story.append(Paragraph(f"• {item}", styles["BodyText"]))
            elif block.type == "table":
                table = Table([block.headers] + block.rows, repeatRows=1); table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#183642")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .25, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP")])); story.append(table); story.append(Spacer(1, .12*inch))
    story += [Paragraph("Source Information", styles["Heading1"]), Paragraph(document.canonical_url or document.source_url, styles["BodyText"])]
    def footer(canvas, doc): canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.drawRightString(7.5*inch, .45*inch, f"Page {doc.page}"); canvas.restoreState()
    SimpleDocTemplate(output, pagesize=letter, rightMargin=.7*inch, leftMargin=.7*inch, topMargin=.65*inch, bottomMargin=.7*inch).build(story, onFirstPage=footer, onLaterPages=footer); return output.getvalue()
