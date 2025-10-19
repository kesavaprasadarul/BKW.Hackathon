#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from extractor import extract_project_data


load_dotenv(Path(__file__).parent.parent / '.env.local')


class DataAgent:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY nicht in .env.local gefunden")
        
        self.client = genai.Client(api_key=api_key)
        self.cache = None
        self.model = "gemini-2.5-flash-lite"
        self.system_instruction = None
    
    def load_data(self, data_dir: Path):
        if not data_dir.exists():
            raise FileNotFoundError(f"Verzeichnis nicht gefunden: {data_dir}")
        
        project_data = extract_project_data(data_dir)
        if not project_data:
            raise ValueError("Keine Daten extrahiert")
        
        files = [f.name for f in data_dir.rglob('*') if f.is_file()]
        
        self.system_instruction = f"""Du bist ein Experte für BKW Bauprojekte. Analysiere die folgenden Projektdaten präzise und antworte strukturiert auf Deutsch.

Verfügbare Dateien: {', '.join(files)}

PROJEKTDATEN:
{project_data}

ANWEISUNGEN:
- Beantworte ausschließlich Fragen zu den obigen Projektdaten
- Strukturiere Antworten mit klaren Überschriften und Aufzählungen
- Gib exakte Zahlen, Kosten, Maße und technische Daten wieder
- Verwende Fachbegriffe korrekt (TGA, Heizlast, Kühllast, etc.)
- Zitiere konkrete Seitenzahlen und Dokumentstellen, wenn verfügbar
- Bei fehlenden Informationen: "Diese Information ist nicht in den verfügbaren Daten enthalten"
- Antworte prägnant und fachlich korrekt
- Verwende deutsche Bau- und Technikterminologie"""

        estimated_tokens = len(self.system_instruction) // 4
        
        if estimated_tokens >= 2048:
            try:
                self.cache = self.client.caches.create(
                    model=self.model,
                    config=types.CreateCachedContentConfig(
                        display_name='bkw_project_data',
                        system_instruction=self.system_instruction,
                        ttl="3600s"
                    )
                )
                print(f"Daten gecacht: {len(project_data.split())} Wörter, {len(files)} Dateien")
            except Exception as e:
                print(f"Nutzen Sie das bezahlte Modell für die Cache-Funktion: {str(e).split(':')[0]}")
        else:
            print(f"Daten geladen: {len(project_data.split())} Wörter, {len(files)} Dateien")
    
    def ask(self, question: str) -> str:
        if not self.system_instruction:
            return "Fehler: Keine Daten geladen"
        
        try:
            if self.cache:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=question,
                    config=types.GenerateContentConfig(cached_content=self.cache.name)
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction
                    )
                )
            return response.text
        except Exception as e:
            return f"Fehler: {e}"
    
    def cleanup(self):
        if self.cache:
            try:
                self.client.caches.delete(self.cache.name)
            except Exception:
                pass
    
    def run(self):
        print("BKW Daten-Agent")
        print("Fragen stellen. 'exit' zum Beenden.")
        
        while True:
            try:
                question = input("\nFrage: ").strip()
                if not question:
                    continue
                if question.lower() in ['exit', 'quit', 'beenden']:
                    break
                
                answer = self.ask(question)
                print(f"\n{answer}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Fehler: {e}")


def main():
    agent = None
    try:
        agent = DataAgent()
        agent.load_data(Path(__file__).parent.parent / "agent_context")
        agent.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fehler: {e}")
        return 1
    finally:
        if agent:
            agent.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
