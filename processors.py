import os
import re
import logging
import fitz  # PyMuPDF
from pathlib import Path

class BaseProcessor:
    def __init__(self, database):
        self.db = database

    def extract_metadata(self, content):
        """Extract metadata from content using pattern matching"""
        metadata = {}
        patterns = {
            'module': [
                r'(?:CAS|Certificate of Advanced Studies)\s+([^\.]+)',
                r'(?:Modul|Module)\s*(?:\d+)?:\s*([^\n]+)',
                r'(?:^|\n)M\d+\s*[-:]\s*([^\n]+)'
            ],
            'topic': [
                r'(?:Topic|Thema|Subject)\s*:\s*([^\n]+)',
                r'(?:^|\n)(?:Thema|Topic)\s*\d*\s*[-:]\s*([^\n]+)'
            ],
            'instructor': [
                r'(?:Instructor|Dozent|Lecturer|Referent)\s*:\s*([^\n]+)',
                r'(?:By|Von)\s*:\s*([^\n]+)'
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    value = match.group(1).strip()
                    if value and len(value) < 100:
                        metadata[key] = value
                        break
        return metadata

    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove special characters but keep German umlauts
        text = re.sub(r'[^\w\s\däöüßÄÖÜ\.,;:\-\(\)]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

class TextProcessor(BaseProcessor):
    def process(self, file_path):
        """Process text files (.txt, .py, .sql)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logging.warning(f"Empty file: {file_path}")
                return None, 0
            
            cleaned_content = self.clean_text(content)
            metadata = self.extract_metadata(cleaned_content)
            
            # Extract additional metadata based on file type
            if file_path.suffix.lower() == '.py':
                docstring_pattern = r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''
                docstrings = re.findall(docstring_pattern, content)
                if docstrings:
                    metadata['docstrings'] = '\n'.join(docstrings)
            elif file_path.suffix.lower() == '.sql':
                table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)'
                tables = re.findall(table_pattern, content, re.IGNORECASE)
                if tables:
                    metadata['tables'] = ', '.join(tables)
            
            content_id = self.db.store_content(
                file_path=str(file_path),
                content=cleaned_content,
                metadata=metadata,
                file_type=file_path.suffix.lower()[1:]
            )
            
            word_count = len(cleaned_content.split())
            logging.info(f"Processed {file_path} - {word_count} words")
            return content_id, word_count
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            self.db.store_error(str(file_path), str(e))
            raise

class PDFProcessor(BaseProcessor):
    def process(self, file_path):
        """Process PDF files using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            total_word_count = 0
            content_id = None
            
            for page_number, page in enumerate(doc, start=1):
                # Extract text and clean it
                text = page.get_text()
                cleaned_content = self.clean_text(text)
                if not cleaned_content.strip():
                    continue  # Skip empty pages
                
                # Extract metadata
                metadata = self.extract_metadata(cleaned_content)
                metadata['page_number'] = page_number  # Add page number
                
                # Store content in database
                content_id = self.db.store_content(
                    file_path=str(file_path),
                    content=cleaned_content,
                    metadata=metadata,
                    file_type='pdf'
                )
                
                # Update word count
                total_word_count += len(cleaned_content.split())
            
            doc.close()
            
            # Return total word count and last content_id
            return content_id, total_word_count

        except Exception as e:
            logging.error(f"Error processing PDF {file_path}: {str(e)}")
            self.db.store_error(str(file_path), str(e))
            raise
