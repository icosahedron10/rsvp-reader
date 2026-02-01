# RSVP Reader - Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RSVP Reader Application                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Part Three: UI Layer (rsvp_reader.py)                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  RSVPReaderUI Class                                           │  │
│  │  • File Selection Dialog                                      │  │
│  │  • Word Display (48pt, centered)                              │  │
│  │  • Playback Controls (Play/Pause/Next/Previous/Reset)         │  │
│  │  • Speed Slider (100-1000 WPM)                                │  │
│  │  • Search Bar + Find Next                                     │  │
│  │  • Progress Bar + Position Counter                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
┌─────────────────────────────────┐   ┌───────────────────────────────┐
│  Part One: File Parser          │   │  Part Two: Token Displayer    │
│  (file_parser.py)                │   │  (token_displayer.py)         │
│  ┌───────────────────────────┐  │   │  ┌─────────────────────────┐  │
│  │  FileParser Class         │  │   │  │  RSVPTokenDisplayer     │  │
│  │  • parse_txt()            │  │   │  │  • Navigation           │  │
│  │  • parse_pdf()            │  │   │  │    - next_token()       │  │
│  │  • tokenize()             │  │   │  │    - previous_token()   │  │
│  │  • Token preservation     │  │   │  │    - seek()             │  │
│  └───────────────────────────┘  │   │  │  • Speed Control        │  │
│                                  │   │  │    - set_speed()        │  │
│  Input:                          │   │  │    - get_delay()        │  │
│  • .txt files (UTF-8)            │   │  │  • Search               │  │
│  • .pdf files (PyPDF2)           │   │  │    - search()           │  │
│                                  │   │  │  • Progress             │  │
│  Output:                         │   │  │    - get_progress()     │  │
│  • List of tokens (strings)     │   │  │  • Playback             │  │
│  • Preserves punctuation         │   │  │    - play/pause/stop    │  │
│  • Maintains structure           │   │  └─────────────────────────┘  │
│                                  │   │                               │
└─────────────────────────────────┘   └───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Data Flow                                                           │
│  ┌────────┐      ┌────────┐      ┌──────────┐      ┌──────────┐   │
│  │  File  │  →   │ Parser │  →   │  Tokens  │  →   │ Displayer│   │
│  │ (.txt) │      │        │      │  (List)  │      │  (RSVP)  │   │
│  │ (.pdf) │      │        │      │          │      │          │   │
│  └────────┘      └────────┘      └──────────┘      └──────────┘   │
│                                                           │          │
│                                                           ▼          │
│                                                     ┌──────────┐    │
│                                                     │    UI    │    │
│                                                     │ Display  │    │
│                                                     └──────────┘    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Testing & Quality Assurance                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  test_file_parser.py          │  8 unit tests               │   │
│  │  test_token_displayer.py      │  22 unit tests              │   │
│  │  test_integration.py          │  End-to-end testing         │   │
│  │  demo.py                      │  Feature demonstration       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Total: 30 unit tests passing, 0 security vulnerabilities           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Key Features                                                        │
│  ✓ Dual file format support (.txt, .pdf)                            │
│  ✓ Character preservation (punctuation, special chars)              │
│  ✓ Configurable speed (100-1000 WPM)                                │
│  ✓ Full playback control (play/pause/next/previous/reset)           │
│  ✓ Case-insensitive search with Find Next                           │
│  ✓ Visual progress tracking                                         │
│  ✓ Comprehensive test coverage                                      │
│  ✓ Security validated (CodeQL scan)                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Dependencies                                                        │
│  • Python 3.7+         (Runtime)                                     │
│  • PyPDF2 ≥3.0.0       (PDF parsing)                                │
│  • tkinter             (GUI framework, built-in)                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Example

```python
# 1. User selects a file in the UI
ui.open_file("example.txt")

# 2. UI creates FileParser
parser = FileParser("example.txt")
tokens = parser.parse()  # Returns: ["The", "quick", "brown", ...]

# 3. UI creates RSVPTokenDisplayer with tokens
displayer = RSVPTokenDisplayer(tokens, wpm=300)

# 4. User clicks Play button
ui.play()  # Starts timer-based display

# 5. For each timer tick:
token = displayer.get_current_token()  # Gets current word
ui.display_word(token)                 # Shows word in UI
displayer.next_token()                 # Advances to next word

# 6. User searches for a word
index = displayer.search("keyword")    # Finds position
displayer.seek(index)                  # Jumps to that position
ui.update_display()                    # Updates UI

# 7. User adjusts speed
displayer.set_speed(500)               # Changes WPM
# Timer automatically adjusts delay
```

## Design Principles

1. **Separation of Concerns**
   - File parsing is independent of display logic
   - Display logic is independent of UI
   - Each component can be tested independently

2. **Clean Interfaces**
   - Simple, well-documented APIs
   - Clear input/output contracts
   - Minimal dependencies between layers

3. **Extensibility**
   - Easy to add new file formats (just extend FileParser)
   - Easy to add new UI controls (just extend RSVPReaderUI)
   - Token displayer can work with any token source

4. **Testability**
   - Each component has comprehensive unit tests
   - Integration tests verify component interaction
   - Demo script showcases all features

5. **User Experience**
   - Intuitive GUI layout
   - Clear visual feedback
   - Responsive controls
   - Helpful error messages
