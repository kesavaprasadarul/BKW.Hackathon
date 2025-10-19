"""Main Application"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai import AIService
from designer import Designer
from config import FORMATS
from extractor import extract_hvac_project_data


def main():
    ai = AIService()
    designer = Designer()
    
    print("TGA Erläuterungsbericht Generator\n" + "="*50)
    print("\nDieser Generator erstellt Erläuterungsberichte aus:")
    print("  - Excel-Datei mit Raumdaten")
    print("  - JSON-Datei mit Kostenschätzung/BOQ")
    print()
    
    # Get input file paths
    excel_path = input("Pfad zur Excel-Datei (Raumdaten): ").strip()
    json_path = input("Pfad zur JSON-Datei (Kostendaten): ").strip()
    
    # Resolve paths
    excel_path = Path(excel_path)
    json_path = Path(json_path)
    
    # Handle relative paths
    if not excel_path.is_absolute():
        excel_path = Path(__file__).parent.parent.parent / excel_path
    if not json_path.is_absolute():
        json_path = Path(__file__).parent.parent.parent / json_path
    
    # Validate files exist
    if not excel_path.exists():
        print(f"Fehler: Excel-Datei nicht gefunden: {excel_path}")
        return
    if not json_path.exists():
        print(f"Fehler: JSON-Datei nicht gefunden: {json_path}")
        return
    
    print("\n" + "="*50)
    print("Extrahiere Projektdaten...")
    print("="*50)
    
    # Extract data from Excel and JSON
    project_data = extract_hvac_project_data(excel_path, json_path)
    
    if not project_data:
        print("Fehler: Keine Daten extrahiert!")
        return
    
    print(f"✓ {len(project_data.split())} Wörter extrahiert")
    
    # Generate report in chunks
    print("\n" + "="*50)
    print("Generiere Erläuterungsbericht...")
    print("="*50)
    content = ai.generate_report_chunked(project_data)
    
    if not content:
        print("Fehler: Report-Generierung fehlgeschlagen!")
        return
    
    print("\n✓ Report erfolgreich generiert")
    
    # Auto-save all formats
    print("\n" + "="*50)
    print("Speichere Report in allen Formaten...")
    print("="*50)
    
    pdf_path = designer.pdf(content, 'Erläuterungsbericht')
    docx_path = designer.docx(content, 'Erläuterungsbericht')
    md_path = designer.markdown(content)
    
    print("\n✓ Berichte erfolgreich erstellt:")
    print(f"PDF:      {pdf_path}")
    print(f"DOCX:     {docx_path}")
    print(f"Markdown: {md_path}")
    print()


if __name__ == "__main__":
    main()