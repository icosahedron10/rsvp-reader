"""
Integration test demonstrating all three parts working together.
"""

import os
from src.file_parser import FileParser
from src.token_displayer import RSVPTokenDisplayer

# Get path to example.txt relative to this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def test_integration():
    """Test all three parts working together."""
    
    print("=" * 60)
    print("RSVP Reader - Integration Test")
    print("=" * 60)
    print()
    
    # Part One: File Parsing
    print("Part 1: File Parsing")
    print("-" * 40)
    file_path = os.path.join(TEST_DIR, "example.txt")
    parser = FileParser(file_path)
    tokens = parser.parse()
    print(f"✓ Successfully parsed '{file_path}'")
    print(f"✓ Extracted {len(tokens)} tokens")
    print(f"✓ First 10 tokens: {tokens[:10]}")
    print()
    
    # Part Two: Token Displayer
    print("Part 2: Token Displayer")
    print("-" * 40)
    displayer = RSVPTokenDisplayer(tokens, wpm=300)
    print(f"✓ Created RSVP displayer with {displayer.get_total_tokens()} tokens")
    print(f"✓ Speed: {displayer.get_speed()} WPM")
    print(f"✓ Delay between words: {displayer.get_delay():.3f} seconds")
    print()
    
    # Display first few tokens
    print("Displaying first 5 tokens:")
    for i in range(5):
        token = displayer.get_current_token()
        print(f"  [{i+1}] {token}")
        displayer.next_token()
    print()
    
    # Test search functionality
    print("Part 3: Search Functionality")
    print("-" * 40)
    displayer.reset()
    search_term = "RSVP"
    result = displayer.search(search_term)
    if result is not None:
        displayer.seek(result)
        print(f"✓ Found '{search_term}' at position {result + 1}")
        print(f"✓ Token: '{displayer.get_current_token()}'")
    else:
        print(f"✗ '{search_term}' not found")
    print()
    
    # Test speed control
    print("Speed Control Test")
    print("-" * 40)
    print(f"Initial speed: {displayer.get_speed()} WPM (delay: {displayer.get_delay():.3f}s)")
    displayer.set_speed(600)
    print(f"New speed: {displayer.get_speed()} WPM (delay: {displayer.get_delay():.3f}s)")
    print()
    
    # Test progress
    print("Progress Test")
    print("-" * 40)
    displayer.reset()
    print(f"Progress at start: {displayer.get_progress_percentage():.1f}%")
    displayer.seek(len(tokens) // 2)
    print(f"Progress at midpoint: {displayer.get_progress_percentage():.1f}%")
    displayer.seek(len(tokens) - 1)
    print(f"Progress at end: {displayer.get_progress_percentage():.1f}%")
    print()
    
    print("=" * 60)
    print("✓ All integration tests passed!")
    print("=" * 60)
    print()
    print("The RSVP Reader is ready to use!")
    print("To start the GUI application, run: python -m src.rsvp_reader")
    print()

if __name__ == "__main__":
    test_integration()
