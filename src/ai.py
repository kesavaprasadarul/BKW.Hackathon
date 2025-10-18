"""AI Service"""

import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, REPORT_STRUCTURE
import json
import time
from typing import List, Dict, Any


class AIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env.local")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            GEMINI_MODEL, system_instruction=SYSTEM_PROMPT
        )

    def generate_report_chunked(self, project_data):
        """Generate report section by section with summarization"""
        sections = []
        context = f"Projektdaten:\n{project_data}\n\n"

        for i, section_info in enumerate(REPORT_STRUCTURE[0]["subsections"]):
            print(
                f"\nGeneriere Abschnitt {i+1}/{len(REPORT_STRUCTURE[0]['subsections'])}: {section_info.split(' - ')[0]}..."
            )

            # Generate section
            if i == 0:
                prompt = f"{context}Erstellen Sie den ersten Abschnitt '{section_info}' des Erläuterungsberichts. Beschreiben Sie die Aufgabenstellung, Lage, das Gebäude und die Planungsgrundlagen basierend auf den Projektdaten."
            else:
                summary = self._summarize_previous(sections)
                prompt = f"{context}Bisheriger Inhalt:\n{summary}\n\nErstellen Sie nun den Abschnitt '{section_info}'. Beschreiben Sie die technischen Anlagen dieser Kostengruppe detailliert und fachgerecht."

            section_text = self._generate(prompt)
            if section_text:
                sections.append(section_text)

        return "\n".join(sections)

    def _summarize_previous(self, sections):
        """Summarize previous sections for context"""
        if not sections:
            return ""

        previous_text = "\n".join(sections[-2:])  # Last 2 sections
        prompt = (
            f"Fassen Sie folgende Abschnitte in 2-3 Sätzen zusammen:\n\n{previous_text}"
        )
        return self._generate(prompt) or ""

    def _generate(self, prompt):
        """Internal generate method"""
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
