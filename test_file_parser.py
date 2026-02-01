"""
Tests for file_parser.py (Part One)
"""

import unittest
import tempfile
import os
import zipfile
from pathlib import Path
from file_parser import FileParser, parse_file


class TestFileParser(unittest.TestCase):
    """Test cases for FileParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_parse_txt_file(self):
        """Test parsing a simple text file."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "Hello world! This is a test."
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Parse the file
        parser = FileParser(test_file)
        tokens = parser.parse()
        
        # Verify tokens
        self.assertEqual(tokens, ["Hello", "world!", "This", "is", "a", "test."])
        
    def test_parse_txt_with_special_characters(self):
        """Test parsing text with special characters."""
        test_file = os.path.join(self.temp_dir, "special.txt")
        test_content = "Hello, world! How's it going? (Great!) #hashtag @mention"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        parser = FileParser(test_file)
        tokens = parser.parse()
        
        # Special characters should be preserved with words
        self.assertIn("Hello,", tokens)
        self.assertIn("world!", tokens)
        self.assertIn("How's", tokens)
        self.assertIn("(Great!)", tokens)
        self.assertIn("#hashtag", tokens)
        self.assertIn("@mention", tokens)
    
    def test_parse_multiline_txt(self):
        """Test parsing multi-line text."""
        test_file = os.path.join(self.temp_dir, "multiline.txt")
        test_content = "Line one.\nLine two.\nLine three."
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        parser = FileParser(test_file)
        tokens = parser.parse()
        
        # Should have all tokens from all lines
        self.assertIn("Line", tokens)
        self.assertIn("one.", tokens)
        self.assertIn("two.", tokens)
        self.assertIn("three.", tokens)
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        parser = FileParser("/nonexistent/file.txt")
        with self.assertRaises(FileNotFoundError):
            parser.parse()
    
    def test_unsupported_file_type(self):
        """Test handling of unsupported file type."""
        test_file = os.path.join(self.temp_dir, "test.docx")
        with open(test_file, 'w') as f:
            f.write("content")
        
        parser = FileParser(test_file)
        with self.assertRaises(ValueError):
            parser.parse()
    
    def test_empty_file(self):
        """Test parsing an empty file."""
        test_file = os.path.join(self.temp_dir, "empty.txt")
        with open(test_file, 'w') as f:
            f.write("")
        
        parser = FileParser(test_file)
        tokens = parser.parse()
        
        self.assertEqual(tokens, [])
    
    def test_get_tokens_before_parse(self):
        """Test get_tokens() before parse() is called."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        parser = FileParser(test_file)
        self.assertEqual(parser.get_tokens(), [])
    
    def test_parse_file_convenience_function(self):
        """Test the convenience parse_file() function."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Quick test")

        tokens = parse_file(test_file)
        self.assertEqual(tokens, ["Quick", "test"])


class TestEpubParser(unittest.TestCase):
    """Test cases for EPUB/PUB parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_minimal_epub(self, filename, content_files):
        """
        Create a minimal EPUB file for testing.

        Args:
            filename: Name of the EPUB file to create
            content_files: List of (filename, xhtml_content) tuples
        """
        epub_path = os.path.join(self.temp_dir, filename)

        with zipfile.ZipFile(epub_path, 'w') as zf:
            # Add mimetype (required for valid EPUB)
            zf.writestr('mimetype', 'application/epub+zip')

            # Add container.xml
            container_xml = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
            zf.writestr('META-INF/container.xml', container_xml)

            # Build manifest and spine
            manifest_items = []
            spine_items = []
            for i, (fname, _) in enumerate(content_files):
                item_id = f"item{i}"
                manifest_items.append(f'<item id="{item_id}" href="{fname}" media-type="application/xhtml+xml"/>')
                spine_items.append(f'<itemref idref="{item_id}"/>')

            # Add content.opf
            opf_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
  </metadata>
  <manifest>
    {"".join(manifest_items)}
  </manifest>
  <spine>
    {"".join(spine_items)}
  </spine>
</package>'''
            zf.writestr('OEBPS/content.opf', opf_content)

            # Add content files
            for fname, content in content_files:
                zf.writestr(f'OEBPS/{fname}', content)

        return epub_path

    def test_parse_simple_epub(self):
        """Test parsing a simple EPUB file."""
        xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><p>Hello world from EPUB!</p></body>
</html>'''

        epub_path = self._create_minimal_epub('test.epub', [('chapter1.xhtml', xhtml)])

        parser = FileParser(epub_path)
        tokens = parser.parse()

        self.assertIn("Hello", tokens)
        self.assertIn("world", tokens)
        self.assertIn("EPUB!", tokens)

    def test_parse_pub_extension(self):
        """Test that .pub extension is handled same as .epub."""
        xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><p>Content from PUB file.</p></body>
</html>'''

        epub_path = self._create_minimal_epub('test.pub', [('chapter1.xhtml', xhtml)])

        parser = FileParser(epub_path)
        tokens = parser.parse()

        self.assertIn("Content", tokens)
        self.assertIn("PUB", tokens)

    def test_parse_epub_multiple_chapters(self):
        """Test parsing EPUB with multiple content files."""
        ch1 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><p>Chapter one content.</p></body>
</html>'''
        ch2 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><p>Chapter two content.</p></body>
</html>'''

        epub_path = self._create_minimal_epub('multi.epub', [
            ('ch1.xhtml', ch1),
            ('ch2.xhtml', ch2)
        ])

        parser = FileParser(epub_path)
        tokens = parser.parse()

        self.assertIn("one", tokens)
        self.assertIn("two", tokens)

    def test_parse_epub_special_characters(self):
        """Test EPUB parsing preserves special characters."""
        xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><p>"Hello," she said. It's great! (Really?) #test @mention</p></body>
</html>'''

        epub_path = self._create_minimal_epub('special.epub', [('ch.xhtml', xhtml)])

        parser = FileParser(epub_path)
        tokens = parser.parse()

        self.assertIn('"Hello,"', tokens)
        self.assertIn("It's", tokens)
        self.assertIn("(Really?)", tokens)
        self.assertIn("#test", tokens)

    def test_parse_epub_ignores_script_style(self):
        """Test that script and style content is ignored."""
        xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><style>body { color: red; }</style></head>
<body>
<script>alert("ignore me");</script>
<p>Real content here.</p>
</body>
</html>'''

        epub_path = self._create_minimal_epub('scripted.epub', [('ch.xhtml', xhtml)])

        parser = FileParser(epub_path)
        tokens = parser.parse()

        self.assertIn("Real", tokens)
        self.assertIn("content", tokens)
        self.assertNotIn("alert", tokens)
        self.assertNotIn("color:", tokens)


class TestChapterParsing(unittest.TestCase):
    """Test cases for chapter detection and splitting."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_parse_chapters_simple(self):
        """Test chapter detection with simple format."""
        content = """Chapter 1

This is the first chapter content.

Chapter 2

This is the second chapter content."""

        test_file = os.path.join(self.temp_dir, "chapters.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        self.assertEqual(len(chapters), 2)
        self.assertIn("Chapter 1", chapters)
        self.assertIn("Chapter 2", chapters)

    def test_parse_chapters_with_titles(self):
        """Test chapter detection with chapter titles."""
        content = """Chapter 1: The Beginning

It all started here.

Chapter 2: The Middle

Things got interesting."""

        test_file = os.path.join(self.temp_dir, "titled.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        self.assertEqual(len(chapters), 2)
        self.assertTrue(any("Beginning" in k for k in chapters.keys()))

    def test_parse_chapters_roman_numerals(self):
        """Test chapter detection with Roman numerals."""
        content = """Chapter I

First chapter.

Chapter II

Second chapter."""

        test_file = os.path.join(self.temp_dir, "roman.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        self.assertEqual(len(chapters), 2)

    def test_parse_chapters_parts(self):
        """Test detection of Part headings."""
        content = """Part 1

First part content.

Part 2

Second part content."""

        test_file = os.path.join(self.temp_dir, "parts.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        self.assertEqual(len(chapters), 2)
        self.assertIn("Part 1", chapters)

    def test_parse_chapters_no_chapters(self):
        """Test file without chapter markers returns single content."""
        content = "This is just plain text without any chapter markers."

        test_file = os.path.join(self.temp_dir, "plain.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        self.assertEqual(len(chapters), 1)
        self.assertIn("content", chapters)

    def test_parse_chapters_returns_tokens(self):
        """Test that parse_chapters returns tokenized content."""
        content = """Chapter 1

Hello world test."""

        test_file = os.path.join(self.temp_dir, "tokenized.txt")
        with open(test_file, 'w') as f:
            f.write(content)

        parser = FileParser(test_file)
        chapters = parser.parse_chapters()

        chapter_tokens = chapters.get("Chapter 1", [])
        self.assertIn("Hello", chapter_tokens)
        self.assertIn("world", chapter_tokens)


if __name__ == '__main__':
    unittest.main()
