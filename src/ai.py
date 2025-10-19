"""AI Service"""
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, REPORT_STRUCTURE


class AIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env.local")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)
        
        self.keywords = {
            'KG 410': ['410', 'abwasser', 'wasser', 'gas', 'sanitär', 'trinkwasser'],
            'KG 420': ['420', 'heizung', 'wärme', 'heizlast', 'kessel', 'fernwärme'],
            'KG 430': ['430', 'lüftung', 'rlt', 'klima', 'kühllast', 'ventilation'],
            'KG 440': ['440', 'elektro', 'strom', 'beleuchtung', 'netzersatzanlage'],
            'KG 450': ['450', 'kommunikation', 'brandmeldeanlage', 'bma', 'sicherheit'],
            'KG 470': ['470', 'aufzug', 'förderanlagen', 'küche', 'küchengeräte'],
            'KG 480': ['480', 'gebäudeautomation', 'msr', 'glt', 'regelung']
        }
    
    def generate_report_chunked(self, project_data):
        """Generate report section by section with smart context extraction"""
        sections = []
        
        for i, section_info in enumerate(REPORT_STRUCTURE[0]["subsections"]):
            print(f"\nGeneriere Abschnitt {i+1}/{len(REPORT_STRUCTURE[0]['subsections'])}: {section_info.split(' - ')[0]}...")
            
            relevant_data = self._get_relevant_data(project_data, section_info, i == 0)
            prompt = f"Relevante Projektdaten:\n{relevant_data}\n\nErstellen Sie den Abschnitt '{section_info}' des Erläuterungsberichts."
            
            section_text = self._generate(prompt)
            if section_text:
                sections.append(section_text)
        
        return "\n".join(sections)
    
    def _get_relevant_data(self, project_data, section_info, is_first):
        """Extract relevant data for current section"""
        if is_first:
            return self._extract_with_keywords(project_data, ['projekt', 'gebäude', 'lage', 'aufgabenstellung'])
        
        # keywords for section
        section_keywords = []
        for kg, kw_list in self.keywords.items():
            if kg in section_info:
                section_keywords = kw_list
                break
        
        if not section_keywords:
            return self._fallback_search(project_data, section_info)
        
        result = self._extract_with_keywords(project_data, section_keywords)
        return result if result.strip() else self._fallback_search(project_data, section_info)
    
    def _extract_with_keywords(self, project_data, keywords):
        """Extract lines matching keywords with context"""
        lines = project_data.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in keywords):
                start = max(0, i - 3)
                end = min(len(lines), i + 6)
                relevant_lines.extend(lines[start:end])
        
        # Remove duplicates
        seen = set()
        unique_lines = [line for line in relevant_lines if line not in seen and not seen.add(line)]
        
        return '\n---\n'.join(unique_lines) if unique_lines else '\n'.join(lines[:50])
    
    def _fallback_search(self, project_data, section_info):
        """Fallback search for section"""
        # KG number
        kg_number = next((word for word in section_info.split() if word.isdigit() and len(word) == 3), None)
        
        fallback_keywords = []
        if kg_number:
            fallback_keywords.extend([kg_number, f"kg {kg_number}"])
        
        related = {
            'allgemein': ['übersicht', 'einleitung'],
            'wasser': ['sanitär', 'entwässerung'],
            'heizung': ['wärme', 'thermisch'],
            'lüftung': ['klima', 'luft'],
            'elektro': ['strom', 'energie']
        }
        
        for term, words in related.items():
            if term in section_info.lower():
                fallback_keywords.extend(words)
                break
        
        return self._extract_with_keywords(project_data, fallback_keywords)
    
    def _generate(self, prompt):
        """Generate content"""
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            print(f"Fehler: {e}")
            return None
