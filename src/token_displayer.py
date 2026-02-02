"""
Part Two: Token Displayer Module
Creates a class for displaying tokens in RSVP (Rapid Serial Visual Presentation) format.
"""

from typing import List, Optional, Callable
import time


class RSVPTokenDisplayer:
    """
    Displays tokens in RSVP format for speed reading.
    """
    
    def __init__(self, tokens: List[str], wpm: int = 300):
        """
        Initialize the RSVP token displayer.
        
        Args:
            tokens: List of tokens to display
            wpm: Words per minute for display speed (default: 300)
        """
        self.tokens = tokens
        self.wpm = wpm
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        
    def set_speed(self, wpm: int) -> None:
        """
        Set the display speed in words per minute.
        
        Args:
            wpm: Words per minute (recommended range: 100-1000)
        """
        if wpm < 1:
            raise ValueError("WPM must be positive")
        self.wpm = wpm
    
    def get_speed(self) -> int:
        """
        Get the current display speed.
        
        Returns:
            Current words per minute
        """
        return self.wpm
    
    def get_delay(self) -> float:
        """
        Calculate the delay for the current word based on WPM and word length.

        Longer words receive slightly more display time, shorter words slightly less.
        This creates a natural reading cadence that improves comprehension.

        The scaling formula uses word length to compute a multiplier:
        - 1-2 character words: ~0.8x base delay
        - 5 character words: ~1.0x base delay (baseline)
        - 10+ character words: ~1.3x base delay

        Returns:
            Delay in seconds for the current word
        """
        base_delay = 60.0 / self.wpm

        token = self.get_current_token()
        if not token:
            return base_delay

        # Scale delay based on word length
        # Short words (1-2 chars) get ~0.8x, average words (5 chars) get 1.0x,
        # long words (10+ chars) get up to ~1.3x
        word_length = len(token)
        multiplier = 0.7 + (min(word_length, 12) * 0.05)

        return base_delay * multiplier
    
    def get_current_token(self) -> Optional[str]:
        """
        Get the current token to display.
        
        Returns:
            Current token or None if at the end
        """
        if 0 <= self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None
    
    def get_current_index(self) -> int:
        """
        Get the current token index.
        
        Returns:
            Current index in the token list
        """
        return self.current_index
    
    def get_total_tokens(self) -> int:
        """
        Get the total number of tokens.
        
        Returns:
            Total number of tokens
        """
        return len(self.tokens)
    
    def next_token(self) -> Optional[str]:
        """
        Move to the next token.
        
        Returns:
            Next token or None if at the end
        """
        if self.current_index < len(self.tokens) - 1:
            self.current_index += 1
            return self.get_current_token()
        return None
    
    def previous_token(self) -> Optional[str]:
        """
        Move to the previous token.
        
        Returns:
            Previous token or None if at the beginning
        """
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current_token()
        return None
    
    def seek(self, index: int) -> Optional[str]:
        """
        Seek to a specific token index.
        
        Args:
            index: Token index to seek to
            
        Returns:
            Token at the specified index or None if out of bounds
        """
        if 0 <= index < len(self.tokens):
            self.current_index = index
            return self.get_current_token()
        return None
    
    def reset(self) -> None:
        """
        Reset to the beginning.
        """
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
    
    def play(self, callback: Optional[Callable[[str, int], None]] = None) -> None:
        """
        Play through tokens at the specified speed.
        
        This is a basic synchronous implementation. For GUI integration,
        use the callback-based approach or integrate with an event loop.
        
        Args:
            callback: Optional callback function called for each token
                     with signature: callback(token: str, index: int)
        """
        self.is_playing = True
        self.is_paused = False
        
        while self.is_playing and self.current_index < len(self.tokens):
            if not self.is_paused:
                token = self.get_current_token()
                if callback:
                    callback(token, self.current_index)
                time.sleep(self.get_delay())
                self.next_token()
    
    def pause(self) -> None:
        """
        Pause playback.
        """
        self.is_paused = True
    
    def resume(self) -> None:
        """
        Resume playback.
        """
        self.is_paused = False
    
    def stop(self) -> None:
        """
        Stop playback.
        """
        self.is_playing = False
        self.is_paused = False
    
    def search(self, query: str, start_index: int = 0) -> Optional[int]:
        """
        Search for a token containing the query string.
        
        Args:
            query: String to search for
            start_index: Index to start searching from
            
        Returns:
            Index of the first matching token, or None if not found
        """
        query_lower = query.lower()
        for i in range(start_index, len(self.tokens)):
            if query_lower in self.tokens[i].lower():
                return i
        return None
    
    def get_progress_percentage(self) -> float:
        """
        Get the current progress as a percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        if len(self.tokens) == 0:
            return 0.0
        return (self.current_index / len(self.tokens)) * 100
