"""Main Application"""
from ai import AIService
from designer import Designer
from config import FORMATS


def main():
    ai = AIService()
    designer = Designer()
    
    # Get prompt
    prompt = input("What would you like me to generate? ").strip()
    if not prompt:
        print("No input provided.")
        return
    
    # Generate content
    print("\nGenerating content...")
    content = ai.generate(prompt)
    if not content:
        return
    
    # Choose format
    print("\nFormat:")
    for k, v in FORMATS.items():
        print(f"{k}. {v[0]}")
    
    choice = input("Choice (1-4): ").strip()
    
    # Export
    if choice == '1':
        print(f"\nSaved: {designer.pdf(content)}")
    elif choice == '2':
        print(f"\nSaved: {designer.docx(content)}")
    elif choice == '3':
        print(f"\nSaved: {designer.markdown(content)}")
    elif choice == '4':
        print("\nSaved:")
        print(f"  PDF: {designer.pdf(content)}")
        print(f"  DOCX: {designer.docx(content)}")
        print(f"  Markdown: {designer.markdown(content)}")


if __name__ == "__main__":
    main()