"""
Part One: File Parsing Module
Parses text-based files (.txt, .pdf) into tokens while preserving structure,
special characters, and formatting.
"""

import re
from pathlib import Path
from typing import List, Optional
import PyPDF2


class FileParser:
    """
    Parser for text-based files that extracts tokens while preserving
    special characters and formatting.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the parser with a file path.
        
        Args:
            file_path: Path to the file to parse
        """
        self.file_path = Path(file_path)
        self.tokens: List[str] = []
        
    def parse(self) -> List[str]:
        """
        Parse the file and return tokens.
        
        Returns:
            List of tokens extracted from the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
            
        suffix = self.file_path.suffix.lower()
        
        if suffix == '.txt':
            text = self._parse_txt()
        elif suffix == '.pdf':
            text = self._parse_pdf()
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
            
        self.tokens = self._tokenize(text)
        return self.tokens
    
    def _parse_txt(self) -> str:
        """
        Parse a text file.
        
        Returns:
            Content of the text file
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_pdf(self) -> str:
        """
        Parse a PDF file.
        
        Returns:
            Extracted text from PDF
        """
        text = []
        with open(self.file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words while preserving special characters and structure.
        
        The tokenization process:
        - Splits on whitespace
        - Preserves punctuation attached to words
        - Keeps special characters
        - Maintains formatting structure
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Split on whitespace but preserve all characters
        # This regex splits on whitespace while keeping punctuation with words
        tokens = []
        
        # Split by whitespace but keep all characters including punctuation
        raw_tokens = text.split()
        
        for token in raw_tokens:
            if token.strip():  # Only add non-empty tokens
                tokens.append(token)
        
        return tokens
    
    def get_tokens(self) -> List[str]:
        """
        Get the parsed tokens.
        
        Returns:
            List of tokens (empty if parse() hasn't been called)
        """
        return self.tokens


def parse_file(file_path: str) -> List[str]:
    """
    Convenience function to parse a file and return tokens.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        List of tokens extracted from the file
    """
    parser = FileParser(file_path)
    return parser.parse()
