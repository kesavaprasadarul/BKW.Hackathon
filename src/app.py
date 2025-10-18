"""Main Application"""
from ai import AIService
from designer import Designer
from config import FORMATS
from pathlib import Path


def main():
    ai = AIService()
    designer = Designer()
    
    # Read project data from example_data.txt
    data_file = Path(__file__).parent.parent / "example_data.txt"
    
    if not data_file.exists():
        print("Fehler: example_data.txt nicht gefunden!")
        return
    
    print("Erläuterungsbericht Generator\n" + "="*50)
    print(f"Lade Projektdaten aus: {data_file.name}")
    
    try:
        project_data = data_file.read_text(encoding='utf-8')
        print(f"✓ {len(project_data.split())} Wörter geladen")
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        return
    
    # Generate report in chunks
    print("\n" + "="*50)
    print("Generiere Erläuterungsbericht...")
    print("="*50)
    content = ai.generate_report_chunked(project_data)
    if not content:
        return
    
    # Choose format
    print("\n" + "="*50)
    print("Format auswählen:")
    for k, v in FORMATS.items():
        print(f"{k}. {v[0]}")
    
    choice = input("Auswahl (1-4): ").strip()
    
    # Export
    print()
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