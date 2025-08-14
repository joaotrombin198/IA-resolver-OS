"""
File processing module for importing cases from various file formats
"""
import os
import logging
import pandas as pd
from typing import List, Dict, Optional
import csv
from io import StringIO
import json

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class FileProcessor:
    def __init__(self):
        # Sistema 100% interno - sem OpenAI
        self.openai_client = None
    
    def process_file(self, file_path: str, format_type: str = "auto") -> List[Dict[str, str]]:
        """
        Process uploaded file and extract cases
        
        Args:
            file_path: Path to the uploaded file
            format_type: Only 'structured' supported - no external AI processing
        
        Returns:
            List of dictionaries with 'system_type', 'problem_description', 'solution'
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            # Sistema interno - apenas formatos estruturados
            if format_type != "structured":
                raise ValueError("Apenas formato estruturado é suportado (sistema 100% interno)")
            
            # Extract raw content based on file type
            if file_extension in ['.xlsx', '.xls']:
                content = self._process_excel(file_path, format_type)
            elif file_extension == '.csv':
                content = self._process_csv(file_path, format_type)
            elif file_extension == '.txt':
                content = self._process_txt(file_path, format_type)
            elif file_extension == '.pdf' and PDF_AVAILABLE:
                content = self._process_pdf(file_path, format_type)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_extension}")
            
            return content
            
        except Exception as e:
            logging.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
            raise
    
    def _process_excel(self, file_path: str, format_type: str) -> List[Dict[str, str]]:
        """Process Excel files"""
        df = pd.read_excel(file_path)
        return self._process_structured_dataframe(df)
    
    def _process_csv(self, file_path: str, format_type: str) -> List[Dict[str, str]]:
        """Process CSV files"""
        df = pd.read_csv(file_path)
        return self._process_structured_dataframe(df)
    
    def _process_txt(self, file_path: str, format_type: str) -> List[Dict[str, str]]:
        """Process text files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self._process_structured_text(content)
    
    def _process_pdf(self, file_path: str, format_type: str) -> List[Dict[str, str]]:
        """Process PDF files"""
        if not PDF_AVAILABLE:
            raise ValueError("PyPDF2 não está disponível para processar arquivos PDF")
        
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
        
        return self._process_structured_text(content)
    
    def _process_structured_dataframe(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Process structured Excel/CSV with expected columns"""
        cases = []
        
        # Try to find relevant columns (case-insensitive)
        columns = {col.lower(): col for col in df.columns}
        
        system_col = None
        problem_col = None
        solution_col = None
        
        # Map common column names (including Portuguese variations)
        for col_lower, col_original in columns.items():
            if any(word in col_lower for word in ['sistema', 'system', 'tipo']):
                system_col = col_original
            elif any(word in col_lower for word in ['problema', 'problem', 'issue', 'erro', 'error']):
                problem_col = col_original
            elif any(word in col_lower for word in ['solução', 'soluçao', 'solution', 'resolução', 'resolucao', 'fix']):
                solution_col = col_original
        
        if not problem_col or not solution_col:
            raise ValueError("Não foi possível identificar as colunas de problema e solução no arquivo")
        
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row[problem_col]).any() if hasattr(pd.isna(row[problem_col]), 'any') else pd.isna(row[problem_col]) or \
               pd.isna(row[solution_col]).any() if hasattr(pd.isna(row[solution_col]), 'any') else pd.isna(row[solution_col]):
                continue
                
            system_val = row[system_col] if system_col else None
            case = {
                'system_type': str(system_val).strip() if system_col and not (pd.isna(system_val).any() if hasattr(pd.isna(system_val), 'any') else pd.isna(system_val)) else 'Desconhecido',
                'problem_description': str(row[problem_col]).strip(),
                'solution': str(row[solution_col]).strip()
            }
            
            # Only add cases with meaningful content
            if (case['problem_description'] and case['solution'] and 
                case['problem_description'] != 'nan' and case['solution'] != 'nan' and
                len(case['problem_description']) > 10 and len(case['solution']) > 10):
                cases.append(case)
        
        return cases
    
    def _process_structured_text(self, content: str) -> List[Dict[str, str]]:
        """Process structured text with separators"""
        cases = []
        
        # Split by common separators
        sections = []
        if "---" in content:
            sections = content.split("---")
        elif "\n\n\n" in content:
            sections = content.split("\n\n\n")
        else:
            sections = content.split("\n\n")
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            case = self._extract_case_from_text(section)
            if case:
                cases.append(case)
        
        return cases
    
    def _extract_case_from_text(self, text: str) -> Optional[Dict[str, str]]:
        """Extract a case from a text section"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        system_type = "Desconhecido"
        problem_description = ""
        solution = ""
        
        current_section = "problem"
        
        for line in lines:
            # Check for section headers
            line_lower = line.lower()
            if any(word in line_lower for word in ['sistema:', 'system:']):
                system_type = line.split(':', 1)[1].strip()
            elif any(word in line_lower for word in ['problema:', 'problem:', 'issue:']):
                current_section = "problem"
                if ':' in line:
                    problem_description += line.split(':', 1)[1].strip() + " "
            elif any(word in line_lower for word in ['solução:', 'solution:', 'fix:']):
                current_section = "solution"
                if ':' in line:
                    solution += line.split(':', 1)[1].strip() + " "
            else:
                # Add to current section
                if current_section == "problem":
                    problem_description += line + " "
                elif current_section == "solution":
                    solution += line + " "
        
        if problem_description.strip() and solution.strip():
            return {
                'system_type': system_type,
                'problem_description': problem_description.strip(),
                'solution': solution.strip()
            }
        
        return None
    
