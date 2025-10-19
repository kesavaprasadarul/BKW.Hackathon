#!/usr/bin/env python3
"""
BKW Hackathon Data Agent - Minimal Version
"""

import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import os

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
import importlib.util
spec = importlib.util.spec_from_file_location("extractor", src_path / "extractor.py")
extractor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor_module)
extract_project_data = extractor_module.extract_project_data

load_dotenv('.env.local')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class DataAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env.local")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = None
        self.project_data = ""
        
    def load_data(self, agent_context_dir: Path):
        """Load data from agent_context directory"""
        if not agent_context_dir.exists():
            raise FileNotFoundError(f"agent_context directory not found: {agent_context_dir}")
        
        self.project_data = extract_project_data(agent_context_dir)
        if not self.project_data:
            raise ValueError("No data extracted from agent_context directory")
        
        # Get file list
        files = [f.name for f in agent_context_dir.rglob('*') if f.is_file()]
        data_summary = f"Files: {', '.join(files)}" if files else "No files found"
        
        # Initialize model
        system_prompt = f"""You are a specialized assistant for BKW Hackathon project data.
Answer ONLY questions about the loaded project data. If information is not available in the data, say so clearly.
Available data: {data_summary}"""
        
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=system_prompt)
        print(f"✓ Data loaded: {len(self.project_data.split())} words from {len(files)} files")
    
    def ask(self, question: str) -> str:
        """Ask a question about the loaded data"""
        if not self.model:
            return "Error: No data loaded"
        
        try:
            prompt = f"Question: {question}\n\nUse this project data to answer:\n\n{self.project_data}\n\nAnswer only based on available data."
            return self.model.generate_content(prompt).text
        except Exception as e:
            return f"Error: {e}"
    
    def run(self):
        """Start interactive mode"""
        print("🤖 BKW Hackathon Data Agent")
        print("Ask questions about your data. Type 'exit' to quit.")
        
        while True:
            try:
                question = input("\n❓ Question: ").strip()
                if not question:
                    continue
                if question.lower() in ['exit', 'quit']:
                    break
                
                answer = self.ask(question)
                print(f"\n💡 Answer:\n{answer}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    try:
        agent = DataAgent()
        agent.load_data(Path(__file__).parent / "agent_context")
        agent.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
