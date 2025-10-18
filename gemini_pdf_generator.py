#!/usr/bin/env python3
"""
Gemini PDF Report Generator
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from dotenv import load_dotenv


def load_api_key():
    """Load API key from .env.local file."""
    load_dotenv('.env.local')
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env.local file.")
        sys.exit(1)
    return api_key


def generate_content(prompt):
    """Generate content using Gemini Flash Lite."""
    genai.configure(api_key=load_api_key())
    model = genai.GenerativeModel('gemini-flash-lite-latest')
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return None


def create_pdf(content, filename):
    """Create PDF report from content."""
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(reports_dir / filename), pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=16, spaceAfter=20,
        textColor=colors.darkblue, alignment=1
    )
    heading_style = ParagraphStyle(
        'Heading', parent=styles['Heading2'], fontSize=12, spaceAfter=10,
        textColor=colors.darkblue
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontSize=10, spaceAfter=8
    )
    
    story = []
    
    # Title and timestamp
    story.append(Paragraph("AI Generated Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Process content
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1*inch))
            continue
        
        if line.startswith('#') or (len(line) < 50 and line.isupper()):
            heading_text = line.lstrip('#').strip()
            if heading_text:
                story.append(Paragraph(heading_text, heading_style))
        else:
            story.append(Paragraph(line, body_style))
    
    doc.build(story)
    return str(reports_dir / filename)


def main():
    """Main function."""
    prompt = input("What would you like me to generate? ").strip()
    
    if not prompt:
        print("No input provided.")
        return
    
    content = generate_content(prompt)
    if not content:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gemini_report_{timestamp}.pdf"
    
    pdf_path = create_pdf(content, filename)
    if pdf_path:
        print(f"Report saved: {pdf_path}")
    else:
        print("Failed to create PDF.")


if __name__ == "__main__":
    main()