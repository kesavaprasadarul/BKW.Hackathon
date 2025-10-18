"""Configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-flash-lite-latest'
REPORTS_DIR = Path(__file__).parent.parent / "reports"

FORMATS = {
    '1': ('PDF', '.pdf'),
    '2': ('DOCX', '.docx'),
    '3': ('Markdown', '.md'),
    '4': ('All', 'all')
}

# Simple prompt enhancement
PROMPT_ENHANCEMENT = "\n\nProvide a clear, well-structured response suitable for a report."
