"""Main Application"""
from src.ai import AIService
from designer import Designer
from src.config import FORMATS
from extractor import extract_project_data
from pathlib import Path


def main():
    ai = AIService()
    designer = Designer()
    
    print("Erläuterungsbericht Generator\n" + "="*50)
    
    # Extract data from context directory
    context_dir = Path(__file__).parent.parent / "context"
    project_data = extract_project_data(context_dir)
    
    if not project_data:
        print("Fehler: Keine Daten aus Context-Verzeichnis extrahiert!")
        return
    
    print(f"{len(project_data.split())} Wörter extrahiert")
    
    # Generate report in chunks
    print("\n" + "="*50)
    print("Generiere Erläuterungsbericht...")
    print("="*50)
    content = ai.generate_report_chunked(project_data)
    # content = "test"
    if not content:
        return
    
    # Choose format
    print("\n" + "="*50)
    print("Format auswählen:")
    for k, v in FORMATS.items():
        print(f"{k}. {v[0]}")
    
    choice = input("Auswahl (1-4): ").strip()

    if choice == '1':
        print(f"Gespeichert: {designer.pdf(content, 'Erläuterungsbericht')}")
    elif choice == '2':
        print(f"Gespeichert: {designer.docx(content, 'Erläuterungsbericht')}")
    elif choice == '3':
        print(f"Gespeichert: {designer.markdown(content)}")
    elif choice == '4':
        print("Gespeichert:")
        print(f"  PDF: {designer.pdf(content, 'Erläuterungsbericht')}")
        print(f"  DOCX: {designer.docx(content, 'Erläuterungsbericht')}")
        print(f"  Markdown: {designer.markdown(content)}")


if __name__ == "__main__":
    main()