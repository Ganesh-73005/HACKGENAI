# utilities.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import re

def generate_pdf(title, sections):
    safe_title = re.sub(r'[\\/*?:"<>|\n\r]', '_', title)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    story.append(Paragraph(f"<b>Scene Title:</b> {title}", styles["Title"]))
    story.append(Spacer(1, 12))
    
    # Process each section (camera_angles, lighting_setups, lens_options)
    for section_name, items in sections.items():
        story.append(Paragraph(f"<b>{section_name.replace('_', ' ').title()}:</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))
        
        for item in items:
            # Handle both dict format (with name and description) and simple strings
            if isinstance(item, dict):
                name = item.get('name', '')
                description = item.get('description', '')
                story.append(Paragraph(f"<b>{name}:</b> {description}", styles["Normal"]))
            else:
                story.append(Paragraph(f"- {str(item)}", styles["Normal"]))
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 10))
    
    doc.build(story)
    buffer.seek(0)
    return buffer