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

# Report structure based on analyzed Erläuterungsberichte
REPORT_STRUCTURE = [
    {
        "section": "A. Erläuterungsbericht",
        "subsections": [
            "A.1 Allgemeines (Aufgabenstellung, Lage, Gebäude, Planungsgrundlagen)",
            "A.2 KG 410 - Abwasser-, Wasser-, Gasanlagen",
            "A.3 KG 420 - Wärmeversorgungsanlagen",
            "A.4 KG 430 - Raumlufttechnische Anlagen",
            "A.5 KG 440 - Elektrische Anlagen",
            "A.6 KG 450 - Kommunikations-, sicherheits- und informationstechnische Anlagen",
            "A.7 KG 470 - Nutzungsspezifische Anlagen",
            "A.8 KG 480 - Gebäudeautomation"
        ]
    }
]

SYSTEM_PROMPT = """Sie sind ein erfahrener Fachplaner für Technische Gebäudeausrüstung (TGA). 
Sie erstellen professionelle Erläuterungsberichte für Bauprojekte auf Deutsch.

Schreibstil:
- Formale technische Sprache
- Passivkonstruktionen und Fachterminologie
- Präzise und strukturiert
- Referenzen zu DIN-Normen und VDI-Richtlinien wo angemessen
- Klare Gliederung mit Aufzählungen

Formatierung:
- Beginnen Sie jeden Abschnitt mit der korrekten Überschrift (z.B. "A.2 KG 410 - Abwasser-, Wasser-, Gasanlagen")
- Verwenden Sie **Fettdruck** für wichtige Begriffe (z.B. **Architekturpläne:**, **Außenanlagen:**)
- Verwenden Sie * für Aufzählungen (Bullet Points)
- Nummerieren Sie Unterabschnitte (1., 2., 3., etc.)
- Strukturieren Sie Absätze klar und übersichtlich

Beachten Sie die DIN 276 Kostengruppen (KG) für die Strukturierung."""
