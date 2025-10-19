"""File Extractor for Multiple Formats"""
import pandas as pd
import PyPDF2
import docx
from pathlib import Path
import logging
from typing import Dict, List, Optional, Union
import re
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileExtractor:
    """Extracts text content from various file formats"""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt': self._extract_txt,
            '.md': self._extract_txt,
            '.pdf': self._extract_pdf,
            '.docx': self._extract_docx,
            '.xlsx': self._extract_excel,
            '.xls': self._extract_excel,
            '.csv': self._extract_csv
        }
    
    def extract_from_directory(self, directory_path: Union[str, Path]) -> Dict[str, str]:
        """
        Extract text content from all supported files in a directory
        
        Args:
            directory_path: Path to directory containing files
            
        Returns:
            Dictionary mapping filename to extracted content
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        extracted_data = {}
        
        # Get all files in directory and subdirectories
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    content = self.extract_from_file(file_path)
                    if content:
                        extracted_data[file_path.name] = content
                        logger.info(f"Successfully extracted content from: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to extract from {file_path.name}: {e}")
        
        return extracted_data
    
    def extract_from_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Extract text content from a single file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        extension = file_path.suffix.lower()
        if extension not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {extension}")
            return None
        
        try:
            extractor_func = self.supported_extensions[extension]
            return extractor_func(file_path)
        except Exception as e:
            logger.error(f"Error extracting from {file_path.name}: {e}")
            return None
    
    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT and MD files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not decode file with any supported encoding")
        except Exception as e:
            logger.error(f"Error reading text file {file_path.name}: {e}")
            return ""
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Seite {page_num + 1} ---\n{text}")
            
            return "\n\n".join(text_content)
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path.name}: {e}")
            return ""
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            paragraphs = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            
            # Also extract text from tables
            for table in doc.tables:
                table_text = []
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        table_text.append(" | ".join(row_text))
                if table_text:
                    paragraphs.append("Tabelle:\n" + "\n".join(table_text))
            
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path.name}: {e}")
            return ""
    
    def _extract_excel(self, file_path: Path) -> str:
        """Extract text from Excel files"""
        try:
            excel_content = []
            
            # suppress warnings (openpyxl)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
                
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Add sheet header
                    excel_content.append(f"=== Arbeitsblatt: {sheet_name} ===")
                    
                    # Convert DataFrame to readable text
                    if not df.empty:
                        # Get column names
                        columns = df.columns.tolist()
                        excel_content.append(f"Spalten: {', '.join(map(str, columns))}")
                        
                        # Add data rows (limit to first 100 rows to avoid too much content)
                        max_rows = min(100, len(df))
                        for i in range(max_rows):
                            row_data = []
                            for col in columns:
                                value = df.iloc[i][col]
                                if pd.notna(value):
                                    row_data.append(str(value))
                                else:
                                    row_data.append("")
                            excel_content.append(" | ".join(row_data))
                        
                        if len(df) > 100:
                            excel_content.append(f"... und {len(df) - 100} weitere Zeilen")
                    
                    excel_content.append("")  # Empty line between sheets
            
            return "\n".join(excel_content)
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path.name}: {e}")
            return ""
    
    def _extract_csv(self, file_path: Path) -> str:
        """Extract text from CSV files"""
        try:
            df = pd.read_csv(file_path)
            
            csv_content = []
            csv_content.append(f"=== CSV Datei: {file_path.name} ===")
            
            if not df.empty:
                # Get column names
                columns = df.columns.tolist()
                csv_content.append(f"Spalten: {', '.join(map(str, columns))}")
                
                # Add data rows (limit to first 100 rows)
                max_rows = min(100, len(df))
                for i in range(max_rows):
                    row_data = []
                    for col in columns:
                        value = df.iloc[i][col]
                        if pd.notna(value):
                            row_data.append(str(value))
                        else:
                            row_data.append("")
                    csv_content.append(" | ".join(row_data))
                
                if len(df) > 100:
                    csv_content.append(f"... und {len(df) - 100} weitere Zeilen")
            
            return "\n".join(csv_content)
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path.name}: {e}")
            return ""
    
    def combine_extracted_data(self, extracted_data: Dict[str, str], 
                             project_name: str = "Projekt") -> str:
        """
        Combine extracted data from multiple files into a structured format
        
        Args:
            extracted_data: Dictionary mapping filename to content
            project_name: Name of the project
            
        Returns:
            Combined text content suitable for report generation
        """
        combined_content = []
        combined_content.append(f"# Projektdaten - {project_name}")
        combined_content.append(f"Extrahierte Informationen aus {len(extracted_data)} Dateien")
        combined_content.append("=" * 50)
        combined_content.append("")
        
        # Sort files by type and name for better organization
        file_categories = {
            'Berichte': [],
            'Kosten': [],
            'Berechnungen': [],
            'Pläne': [],
            'Sonstige': []
        }
        
        for filename, content in extracted_data.items():
            filename_lower = filename.lower()
            if any(keyword in filename_lower for keyword in ['bericht', 'report', 'erläuterung']):
                file_categories['Berichte'].append((filename, content))
            elif any(keyword in filename_lower for keyword in ['kosten', 'cost', 'preis', 'kobe', 'kosch']):
                file_categories['Kosten'].append((filename, content))
            elif any(keyword in filename_lower for keyword in ['berechnung', 'calculation', 'heizlast', 'kühllast']):
                file_categories['Berechnungen'].append((filename, content))
            elif any(keyword in filename_lower for keyword in ['plan', 'schema', 'grundriss']):
                file_categories['Pläne'].append((filename, content))
            else:
                file_categories['Sonstige'].append((filename, content))
        
        # Add content by category
        for category, files in file_categories.items():
            if files:
                combined_content.append(f"## {category}")
                combined_content.append("")
                
                for filename, content in files:
                    combined_content.append(f"### {filename}")
                    combined_content.append("")
                    
                    # Clean and format content
                    cleaned_content = self._clean_content(content)
                    combined_content.append(cleaned_content)
                    combined_content.append("")
                    combined_content.append("---")
                    combined_content.append("")
        
        return "\n".join(combined_content)
    
    def _clean_content(self, content: str) -> str:
        """Clean and format extracted content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove very short lines that might be artifacts
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 2 or line in ['', '---', '===']:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


def extract_project_data(context_directory: Union[str, Path]) -> str:
    """
    Convenience function to extract all project data from context directory
    
    Args:
        context_directory: Path to directory containing project files
        
    Returns:
        Combined project data as text
    """
    extractor = FileExtractor()
    
    # Extract data from all files
    extracted_data = extractor.extract_from_directory(context_directory)
    
    if not extracted_data:
        logger.warning("No data extracted from context directory")
        return ""
    
    # Combine into structured format
    project_data = extractor.combine_extracted_data(extracted_data)
    
    logger.info(f"Successfully extracted data from {len(extracted_data)} files")
    return project_data


if __name__ == "__main__":
    # Test the extractor
    context_dir = Path(__file__).parent.parent / "context"
    if context_dir.exists():
        project_data = extract_project_data(context_dir)
        print(f"Extracted {len(project_data)} characters of project data")
        print("\nFirst 500 characters:")
        print(project_data[:500])
    else:
        print(f"Context directory not found: {context_dir}")
