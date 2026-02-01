"""
RSVP Reader - Usage Examples and Demonstration

This script demonstrates how to use each component of the RSVP Reader.
"""

from file_parser import FileParser, parse_file
from token_displayer import RSVPTokenDisplayer


def demo_file_parsing():
    """Demonstrate file parsing functionality."""
    print("\n" + "="*60)
    print("DEMO: File Parsing (Part One)")
    print("="*60)
    
    # Method 1: Using FileParser class
    print("\n1. Using FileParser class:")
    parser = FileParser("example.txt")
    tokens = parser.parse()
    print(f"   Parsed {len(tokens)} tokens from example.txt")
    print(f"   First 5 tokens: {tokens[:5]}")
    
    # Method 2: Using convenience function
    print("\n2. Using parse_file() convenience function:")
    tokens = parse_file("example.txt")
    print(f"   Parsed {len(tokens)} tokens")
    print(f"   Last 5 tokens: {tokens[-5:]}")
    
    # Demonstrate token preservation
    print("\n3. Token preservation:")
    print("   Tokens with punctuation:")
    for token in tokens[:15]:
        if any(c in token for c in ".,!?;:()[]{}"):
            print(f"   - {token}")


def demo_token_displayer():
    """Demonstrate token displayer functionality."""
    print("\n" + "="*60)
    print("DEMO: Token Displayer (Part Two)")
    print("="*60)
    
    # Parse a file first
    tokens = parse_file("example.txt")
    
    # Create displayer
    print("\n1. Creating RSVP Token Displayer:")
    displayer = RSVPTokenDisplayer(tokens, wpm=300)
    print(f"   Total tokens: {displayer.get_total_tokens()}")
    print(f"   Speed: {displayer.get_speed()} WPM")
    print(f"   Delay per word: {displayer.get_delay():.3f} seconds")
    
    # Navigation
    print("\n2. Navigation:")
    print(f"   Current token: '{displayer.get_current_token()}'")
    displayer.next_token()
    print(f"   Next token: '{displayer.get_current_token()}'")
    displayer.previous_token()
    print(f"   Previous token: '{displayer.get_current_token()}'")
    
    # Seeking
    print("\n3. Seeking to position:")
    displayer.seek(10)
    print(f"   Token at position 10: '{displayer.get_current_token()}'")
    
    # Speed control
    print("\n4. Speed control:")
    print(f"   Initial speed: {displayer.get_speed()} WPM")
    displayer.set_speed(600)
    print(f"   New speed: {displayer.get_speed()} WPM")
    print(f"   New delay: {displayer.get_delay():.3f} seconds")
    
    # Search
    print("\n5. Search functionality:")
    displayer.reset()
    search_terms = ["quick", "RSVP", "reading"]
    for term in search_terms:
        index = displayer.search(term)
        if index is not None:
            displayer.seek(index)
            print(f"   Found '{term}' at position {index}: '{displayer.get_current_token()}'")
        else:
            print(f"   '{term}' not found")
    
    # Progress tracking
    print("\n6. Progress tracking:")
    displayer.reset()
    print(f"   Progress at start: {displayer.get_progress_percentage():.1f}%")
    displayer.seek(displayer.get_total_tokens() // 2)
    print(f"   Progress at midpoint: {displayer.get_progress_percentage():.1f}%")
    print(f"   Position: {displayer.get_current_index() + 1}/{displayer.get_total_tokens()}")


def demo_rsvp_simulation():
    """Simulate RSVP reading (without GUI)."""
    print("\n" + "="*60)
    print("DEMO: RSVP Reading Simulation")
    print("="*60)
    
    tokens = parse_file("example.txt")
    displayer = RSVPTokenDisplayer(tokens, wpm=300)
    
    print("\nSimulating RSVP display of first 20 words...")
    print("(Each word would be displayed for {:.3f} seconds)".format(displayer.get_delay()))
    print("\n" + "-"*40)
    
    for i in range(20):
        token = displayer.get_current_token()
        position = f"[{displayer.get_current_index() + 1}/{displayer.get_total_tokens()}]"
        progress = f"({displayer.get_progress_percentage():.1f}%)"
        
        # Center the word for RSVP effect
        centered_token = token.center(30)
        print(f"\r{position:10} {centered_token} {progress:8}", end="", flush=True)
        
        import time
        time.sleep(0.1)  # Shortened for demo purposes
        
        if not displayer.next_token():
            break
    
    print("\n" + "-"*40)
    print("\nIn the actual GUI, words would be displayed one at a time")
    print("in a large font in the center of the screen.")


def demo_ui_features():
    """Describe UI features (Part Three)."""
    print("\n" + "="*60)
    print("DEMO: UI Features (Part Three)")
    print("="*60)
    
    print("""
The RSVP Reader GUI application (rsvp_reader.py) provides:

1. FILE SELECTION
   - Click "Open File" button to select .txt or .pdf files
   - Displays filename after loading
   - Shows word count

2. RSVP DISPLAY
   - Large, centered word display (48pt bold font)
   - Clear, easy-to-read presentation
   - Words change at controlled intervals

3. PLAYBACK CONTROLS
   - ▶ Play/Pause button (toggles playback)
   - ⏮ Previous button (go back one word)
   - ⏭ Next button (advance one word)
   - ⏹ Reset button (return to start)

4. SPEED CONTROL
   - Slider to adjust reading speed (100-1000 WPM)
   - Real-time speed display
   - Changes take effect immediately

5. PROGRESS TRACKING
   - Visual progress bar
   - Position counter (current/total)
   - Percentage indicator

6. SEARCH FUNCTIONALITY
   - Search box to find specific words
   - "Search" button to find first occurrence
   - "Find Next" button for subsequent occurrences
   - Case-insensitive search
   - Automatically jumps to found words

To launch the GUI:
    python rsvp_reader.py
    """)


def main():
    """Run all demonstrations."""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#" + "  RSVP READER - COMPREHENSIVE DEMONSTRATION  ".center(58) + "#")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    demo_file_parsing()
    demo_token_displayer()
    demo_rsvp_simulation()
    demo_ui_features()
    
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#" + "  END OF DEMONSTRATION  ".center(58) + "#")
    print("#" + " "*58 + "#")
    print("#"*60)
    print("\nFor the full experience, run: python rsvp_reader.py\n")


if __name__ == "__main__":
    main()
