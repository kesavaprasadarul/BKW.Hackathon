"""AI Service"""

import google.generativeai as genai
from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SYSTEM_PROMPT,
    REPORT_STRUCTURE,
    HISTORIC_DATA,
)
import json
import time
from typing import List, Dict, Any


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

    def choose_roomtypes(
        self,
        queries: List[str],
        catalog: List[Dict[str, str]],
        batch_size: int = 25,
        min_confidence_if_unsure: float = 0.0,
        max_retries: int = 3,
        retry_backoff_sec: float = 1.5,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Given raw query strings and a catalog [{"nr": "...", "roomtype": "..."}],
        returns a dict keyed by normalized query -> {nr, roomtype, confidence, rationale}.
        Uses the already-configured Gemini model in this service.
        """

        def _norm(s: str) -> str:
            import re, unicodedata

            s = (s or "").strip().lower()
            s = unicodedata.normalize("NFKD", s)
            s = (
                s.replace("ä", "ae")
                .replace("ö", "oe")
                .replace("ü", "ue")
                .replace("ß", "ss")
            )
            s = re.sub(r"[^a-z0-9\s]", " ", s)
            s = re.sub(r"\s+", " ", s).strip()
            return s

        seen, uniq = set(), []
        for q in queries:
            k = _norm(q)
            if k and k not in seen:
                seen.add(k)
                uniq.append(q)

        sys_prompt = (
            "You are given a fixed catalog of room types. For each query, choose the best matching item from the catalog. "
            "You can orient yourself on the following historic data: "
            + json.dumps(HISTORIC_DATA, ensure_ascii=False)
            + " "
            "If none fits well, set confidence < 0.85. "
            "Return ONLY a JSON array with one object per input in the same order. "
            'Each object must be: {"nr": str, "roomtype": str, "confidence": number, "rationale": str}. '
            "Do not include ellipses, code fences, or prose."
        )

        def _call_once(batch: List[str]) -> List[Dict[str, Any]]:
            payload = {"catalog": catalog, "queries": batch}
            prompt = sys_prompt + "\n\n" + json.dumps(payload, ensure_ascii=False)
            text = self._generate(prompt) or ""
            start = text.find("[")
            end = text.rfind("]")
            if start == -1 or end == -1:
                return []
            try:
                arr = json.loads(text[start : end + 1])
                if isinstance(arr, list):
                    return arr
                return []
            except Exception:
                return []

        out_map: Dict[str, Dict[str, Any]] = {}

        for i in range(0, len(uniq), batch_size):
            batch = uniq[i : i + batch_size]
            arr: List[Dict[str, Any]] = []
            for r in range(max_retries):
                arr = _call_once(batch)
                if len(arr) == len(batch):
                    break
                time.sleep(retry_backoff_sec * (r + 1))

            if len(arr) < len(batch):
                arr = arr + [
                    {
                        "nr": "",
                        "roomtype": "",
                        "confidence": min_confidence_if_unsure,
                        "rationale": "no_response",
                    }
                    for _ in range(len(batch) - len(arr))
                ]
            elif len(arr) > len(batch):
                arr = arr[: len(batch)]

            for q, o in zip(batch, arr):
                k = _norm(q)
                out_map[k] = {
                    "nr": str(o.get("nr", "")).strip(),
                    "roomtype": str(o.get("roomtype", "")).strip(),
                    "confidence": float(o.get("confidence", 0.0)),
                    "rationale": str(o.get("rationale", "")),
                }

        return out_map
