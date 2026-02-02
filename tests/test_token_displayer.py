"""
Tests for token_displayer.py (Part Two)
"""

import unittest
from src.token_displayer import RSVPTokenDisplayer


class TestRSVPTokenDisplayer(unittest.TestCase):
    """Test cases for RSVPTokenDisplayer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tokens = ["Hello", "world!", "This", "is", "a", "test."]
        self.displayer = RSVPTokenDisplayer(self.tokens, wpm=300)
    
    def test_initialization(self):
        """Test displayer initialization."""
        self.assertEqual(self.displayer.tokens, self.tokens)
        self.assertEqual(self.displayer.wpm, 300)
        self.assertEqual(self.displayer.current_index, 0)
        self.assertFalse(self.displayer.is_playing)
        self.assertFalse(self.displayer.is_paused)
    
    def test_set_speed(self):
        """Test setting display speed."""
        self.displayer.set_speed(500)
        self.assertEqual(self.displayer.get_speed(), 500)
    
    def test_set_speed_invalid(self):
        """Test setting invalid speed."""
        with self.assertRaises(ValueError):
            self.displayer.set_speed(0)
        with self.assertRaises(ValueError):
            self.displayer.set_speed(-100)
    
    def test_get_delay(self):
        """Test delay calculation with word-length cadence."""
        self.displayer.set_speed(300)
        base_delay = 60.0 / 300  # 0.2 seconds

        # Current token is "Hello" (5 chars) -> multiplier = 0.7 + (5 * 0.05) = 0.95
        expected_delay = base_delay * 0.95
        self.assertAlmostEqual(self.displayer.get_delay(), expected_delay)

        # Move to "a" (1 char) -> multiplier = 0.7 + (1 * 0.05) = 0.75
        self.displayer.seek(4)  # "a"
        expected_delay = base_delay * 0.75
        self.assertAlmostEqual(self.displayer.get_delay(), expected_delay)

        # Move to "world!" (6 chars) -> multiplier = 0.7 + (6 * 0.05) = 1.0
        self.displayer.seek(1)  # "world!"
        expected_delay = base_delay * 1.0
        self.assertAlmostEqual(self.displayer.get_delay(), expected_delay)

    def test_get_delay_long_words(self):
        """Test delay calculation caps at 12 characters."""
        long_tokens = ["supercalifragilisticexpialidocious"]  # 34 chars, but capped at 12
        displayer = RSVPTokenDisplayer(long_tokens, wpm=300)
        base_delay = 60.0 / 300

        # Multiplier capped at 12 chars: 0.7 + (12 * 0.05) = 1.3
        expected_delay = base_delay * 1.3
        self.assertAlmostEqual(displayer.get_delay(), expected_delay)
    
    def test_get_current_token(self):
        """Test getting current token."""
        self.assertEqual(self.displayer.get_current_token(), "Hello")
        
        self.displayer.next_token()
        self.assertEqual(self.displayer.get_current_token(), "world!")
    
    def test_get_current_index(self):
        """Test getting current index."""
        self.assertEqual(self.displayer.get_current_index(), 0)
        
        self.displayer.next_token()
        self.assertEqual(self.displayer.get_current_index(), 1)
    
    def test_get_total_tokens(self):
        """Test getting total token count."""
        self.assertEqual(self.displayer.get_total_tokens(), 6)
    
    def test_next_token(self):
        """Test advancing to next token."""
        token = self.displayer.next_token()
        self.assertEqual(token, "world!")
        self.assertEqual(self.displayer.get_current_index(), 1)
    
    def test_next_token_at_end(self):
        """Test next_token at the end of tokens."""
        self.displayer.current_index = len(self.tokens) - 1
        token = self.displayer.next_token()
        self.assertIsNone(token)
        self.assertEqual(self.displayer.get_current_index(), len(self.tokens) - 1)
    
    def test_previous_token(self):
        """Test going to previous token."""
        self.displayer.next_token()
        self.displayer.next_token()
        
        token = self.displayer.previous_token()
        self.assertEqual(token, "world!")
        self.assertEqual(self.displayer.get_current_index(), 1)
    
    def test_previous_token_at_beginning(self):
        """Test previous_token at the beginning."""
        token = self.displayer.previous_token()
        self.assertIsNone(token)
        self.assertEqual(self.displayer.get_current_index(), 0)
    
    def test_seek(self):
        """Test seeking to specific index."""
        token = self.displayer.seek(3)
        self.assertEqual(token, "is")
        self.assertEqual(self.displayer.get_current_index(), 3)
    
    def test_seek_out_of_bounds(self):
        """Test seeking to invalid index."""
        token = self.displayer.seek(100)
        self.assertIsNone(token)
        
        token = self.displayer.seek(-1)
        self.assertIsNone(token)
    
    def test_reset(self):
        """Test reset functionality."""
        self.displayer.next_token()
        self.displayer.next_token()
        self.displayer.is_playing = True
        self.displayer.is_paused = True
        
        self.displayer.reset()
        
        self.assertEqual(self.displayer.get_current_index(), 0)
        self.assertFalse(self.displayer.is_playing)
        self.assertFalse(self.displayer.is_paused)
    
    def test_pause_resume(self):
        """Test pause and resume."""
        self.displayer.pause()
        self.assertTrue(self.displayer.is_paused)
        
        self.displayer.resume()
        self.assertFalse(self.displayer.is_paused)
    
    def test_stop(self):
        """Test stop functionality."""
        self.displayer.is_playing = True
        self.displayer.is_paused = True
        
        self.displayer.stop()
        
        self.assertFalse(self.displayer.is_playing)
        self.assertFalse(self.displayer.is_paused)
    
    def test_search(self):
        """Test search functionality."""
        index = self.displayer.search("world")
        self.assertEqual(index, 1)
        
        index = self.displayer.search("test")
        self.assertEqual(index, 5)
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search."""
        index = self.displayer.search("WORLD")
        self.assertEqual(index, 1)
    
    def test_search_not_found(self):
        """Test search when query is not found."""
        index = self.displayer.search("notfound")
        self.assertIsNone(index)
    
    def test_search_from_start_index(self):
        """Test search from specific start index."""
        # Search for "is" starting from index 0 (will find "This" which contains "is" as substring)
        index = self.displayer.search("is", 0)
        self.assertEqual(index, 2)  # "This" contains "is"
        
        # Search for "is" starting from index 3 (will find exact token "is")
        index = self.displayer.search("is", 3)
        self.assertEqual(index, 3)  # "is"
        
        # Search for "is" starting from index 4 (should not find "is")
        index = self.displayer.search("is", 4)
        self.assertIsNone(index)
    
    def test_get_progress_percentage(self):
        """Test progress percentage calculation."""
        self.assertAlmostEqual(self.displayer.get_progress_percentage(), 0.0)
        
        self.displayer.seek(3)  # 3/6 = 50%
        self.assertAlmostEqual(self.displayer.get_progress_percentage(), 50.0)
        
        self.displayer.seek(5)  # 5/6 = 83.33%
        self.assertAlmostEqual(self.displayer.get_progress_percentage(), 83.333, places=2)
    
    def test_empty_tokens(self):
        """Test with empty token list."""
        empty_displayer = RSVPTokenDisplayer([], wpm=300)
        self.assertEqual(empty_displayer.get_total_tokens(), 0)
        self.assertIsNone(empty_displayer.get_current_token())
        self.assertEqual(empty_displayer.get_progress_percentage(), 0.0)


if __name__ == '__main__':
    unittest.main()
