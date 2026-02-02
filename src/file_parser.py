"""
Part One: File Parsing Module
Parses text-based files (.txt, .pdf, .epub, .pub) into tokens while preserving structure,
special characters, and formatting.
"""

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict
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
        elif suffix in ('.epub', '.pub'):
            text = self._parse_epub()
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

    def _parse_epub(self) -> str:
        """
        Parse an EPUB/PUB file.

        EPUB files are ZIP archives containing XHTML content.

        Returns:
            Extracted text from EPUB
        """
        text_parts = []

        with zipfile.ZipFile(self.file_path, 'r') as zf:
            # Find content files (XHTML/HTML)
            content_files = self._get_epub_content_files(zf)

            for content_file in content_files:
                try:
                    content = zf.read(content_file).decode('utf-8')
                    extracted = self._extract_text_from_xhtml(content)
                    if extracted.strip():
                        text_parts.append(extracted)
                except Exception:
                    continue

        return '\n\n'.join(text_parts)

    def _get_epub_content_files(self, zf: zipfile.ZipFile) -> List[str]:
        """
        Get ordered list of content files from EPUB.

        Args:
            zf: ZipFile object for the EPUB

        Returns:
            List of content file paths in reading order
        """
        content_files = []

        # Try to find and parse container.xml to get the OPF file
        try:
            container = zf.read('META-INF/container.xml').decode('utf-8')
            root = ET.fromstring(container)
            # Find rootfile element (handle namespaces)
            for elem in root.iter():
                if 'rootfile' in elem.tag:
                    opf_path = elem.get('full-path')
                    if opf_path:
                        content_files = self._parse_opf_spine(zf, opf_path)
                        if content_files:
                            return content_files
        except Exception:
            pass

        # Fallback: find all XHTML/HTML files
        for name in sorted(zf.namelist()):
            if name.endswith(('.xhtml', '.html', '.htm')) and 'toc' not in name.lower():
                content_files.append(name)

        return content_files

    def _parse_opf_spine(self, zf: zipfile.ZipFile, opf_path: str) -> List[str]:
        """
        Parse OPF file to get content files in spine order.

        Args:
            zf: ZipFile object
            opf_path: Path to OPF file within the EPUB

        Returns:
            List of content file paths in reading order
        """
        content_files = []
        opf_dir = str(Path(opf_path).parent)
        if opf_dir == '.':
            opf_dir = ''

        try:
            opf_content = zf.read(opf_path).decode('utf-8')
            root = ET.fromstring(opf_content)

            # Build manifest id -> href mapping
            manifest = {}
            for elem in root.iter():
                if 'item' in elem.tag:
                    item_id = elem.get('id')
                    href = elem.get('href')
                    if item_id and href:
                        manifest[item_id] = href

            # Get spine order
            for elem in root.iter():
                if 'itemref' in elem.tag:
                    idref = elem.get('idref')
                    if idref and idref in manifest:
                        href = manifest[idref]
                        # Resolve path relative to OPF location
                        if opf_dir:
                            full_path = f"{opf_dir}/{href}"
                        else:
                            full_path = href
                        content_files.append(full_path)
        except Exception:
            pass

        return content_files

    def _extract_text_from_xhtml(self, content: str) -> str:
        """
        Extract plain text from XHTML content.

        Args:
            content: XHTML content string

        Returns:
            Extracted plain text
        """
        # Remove XML declaration if present
        content = re.sub(r'<\?xml[^>]*\?>', '', content)

        try:
            # Try parsing as XML
            root = ET.fromstring(content)
            return self._get_element_text(root)
        except ET.ParseError:
            # Fallback: strip HTML tags with regex
            text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    def _get_element_text(self, element: ET.Element) -> str:
        """
        Recursively extract text from XML element.

        Args:
            element: XML element

        Returns:
            Concatenated text content
        """
        text_parts = []

        if element.text:
            text_parts.append(element.text)

        for child in element:
            # Skip script and style elements
            tag_name = child.tag.lower() if isinstance(child.tag, str) else ''
            if 'script' in tag_name or 'style' in tag_name:
                continue

            text_parts.append(self._get_element_text(child))

            if child.tail:
                text_parts.append(child.tail)

        return ' '.join(text_parts)

    def parse_chapters(self) -> Dict[str, List[str]]:
        """
        Parse file and return chapters as separate token lists.

        Uses regex patterns to detect chapter boundaries.

        Returns:
            Dictionary mapping chapter names to token lists.
            Returns {'content': tokens} if no chapters detected.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        suffix = self.file_path.suffix.lower()

        if suffix == '.txt':
            text = self._parse_txt()
        elif suffix == '.pdf':
            text = self._parse_pdf()
        elif suffix in ('.epub', '.pub'):
            text = self._parse_epub()
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        chapters = self._split_into_chapters(text)

        # Tokenize each chapter
        result = {}
        for name, content in chapters.items():
            result[name] = self._tokenize(content)

        return result

    def _split_into_chapters(self, text: str) -> Dict[str, str]:
        """
        Split text into chapters using regex patterns.

        Detects patterns like:
        - Chapter 1, Chapter I, CHAPTER ONE
        - Part 1, Part I, PART ONE
        - Article 1, Section 1

        Args:
            text: Full text content

        Returns:
            Dictionary mapping chapter names to content
        """
        # Pattern to match chapter/part/section headings
        # Uses [^\S\n]* to match horizontal whitespace only (not newlines)
        chapter_pattern = re.compile(
            r'^[^\S\n]*'
            r'((?:Chapter|Part|Article|Section)'
            r'[^\S\n]+(?:\d+|[IVXLCDM]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten))'
            r'[:\.]?[^\S\n]*([^\n]*)$',
            re.MULTILINE | re.IGNORECASE
        )

        matches = list(chapter_pattern.finditer(text))

        if not matches:
            return {'content': text}

        chapters = {}
        for i, match in enumerate(matches):
            chapter_name = match.group(1).strip()
            chapter_title = match.group(2).strip()
            if chapter_title:
                chapter_name = f"{chapter_name}: {chapter_title}"

            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            content = text[start:end].strip()
            if content:
                chapters[chapter_name] = content

        # Include any content before first chapter
        if matches and matches[0].start() > 0:
            preface = text[:matches[0].start()].strip()
            if preface and len(preface.split()) > 10:  # Only if substantial
                chapters = {'Preface': preface, **chapters}

        return chapters if chapters else {'content': text}

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
