"""AI Service"""
import google.generativeai as genai
git from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, REPORT_STRUCTURE


class AIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env.local")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)
    
    def generate_report_chunked(self, project_data):
        """Generate report section by section with summarization"""
        sections = []
        context = f"Projektdaten:\n{project_data}\n\n"
        
        for i, section_info in enumerate(REPORT_STRUCTURE[0]["subsections"]):
            print(f"\nGeneriere Abschnitt {i+1}/{len(REPORT_STRUCTURE[0]['subsections'])}: {section_info.split(' - ')[0]}...")
            
            # Generate section
            if i == 0:
                prompt = f"{context}Erstellen Sie den ersten Abschnitt '{section_info}' des Erläuterungsberichts. Beschreiben Sie die Aufgabenstellung, Lage, das Gebäude und die Planungsgrundlagen basierend auf den Projektdaten."
            else:
                summary = self._summarize_previous(sections)
                prompt = f"{context}Bisheriger Inhalt:\n{summary}\n\nErstellen Sie nun den Abschnitt '{section_info}'. Beschreiben Sie die technischen Anlagen dieser Kostengruppe detailliert und fachgerecht."
            
            section_text = self._generate(prompt)
            if section_text:
                sections.append(f"\n{section_info}\n\n{section_text}")
        
        return "\n".join(sections)
    
    def _summarize_previous(self, sections):
        """Summarize previous sections for context"""
        if not sections:
            return ""
        
        previous_text = "\n".join(sections[-2:])  # Last 2 sections
        prompt = f"Fassen Sie folgende Abschnitte in 2-3 Sätzen zusammen:\n\n{previous_text}"
        return self._generate(prompt) or ""
    
    def _generate(self, prompt):
        """Internal generate method"""
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            print(f"Fehler: {e}")
            return None
