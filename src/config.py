"""Configuration"""

import os
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv(Path(__file__).parent.parent / '.env.local')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash-lite'
REPORTS_DIR = Path(__file__).parent.parent / "reports"
HISTORIC_DATA = json.load(open("static/roomtypes/historic_data.json"))

FORMATS = {
    "1": ("PDF", ".pdf"),
    "2": ("DOCX", ".docx"),
    "3": ("Markdown", ".md"),
    "4": ("All", "all"),
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
            "A.8 KG 480 - Gebäudeautomation",
        ],
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

WICHTIG - Mathematische Notation:
- Verwenden Sie KEINE LaTeX-Notation (keine $, \\text{}, _{}, ^{})
- Schreiben Sie Variablen normal: Ve,build statt $V_{e,build}$
- Schreiben Sie Einheiten normal: m³ statt $\\text{m}^3$, m² statt $\\text{m}^2$
- Verwenden Sie normale Hochzahlen: h⁻¹ statt $\\text{h}^{-1}$

Beachten Sie die DIN 276 Kostengruppen (KG) für die Strukturierung."""
