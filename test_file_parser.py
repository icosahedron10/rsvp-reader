"""
Tests for file_parser.py (Part One)
"""

import unittest
import tempfile
import os
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


if __name__ == '__main__':
    unittest.main()
