from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

class PDFService:
    @staticmethod
    async def generate_pdf(assignment_text: str, topic: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"Assignment: {topic}", styles['Title']))
        story.append(Spacer(1, 12))
        for para in assignment_text.split('\n\n'):
            story.append(Paragraph(para, styles['Normal']))
            story.append(Spacer(1, 12))
        doc.build(story)
        buffer.seek(0)
        return buffer.read()