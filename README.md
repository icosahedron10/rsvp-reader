# RSVP Reader

A Python speed-reading application that displays text one word at a time using Rapid Serial Visual Presentation (RSVP).

## Quick Start

```bash
# Clone the repository
git clone https://github.com/icosahedron10/rsvp-reader.git
cd rsvp-reader

# Install dependencies
pip install -r requirements.txt

# Run the application
python rsvp_reader.py
```

That's it! The GUI will open and you can start speed reading immediately.

## What is RSVP?

RSVP (Rapid Serial Visual Presentation) is a speed-reading technique that displays words one at a time in a fixed location. By eliminating eye movement across the page, readers can achieve significantly faster reading speeds while maintaining comprehension.

## Features

- **Multiple File Formats**: Supports `.txt`, `.pdf`, `.epub`, and `.pub` files
- **Adjustable Speed**: 100 to 1000 words per minute (WPM)
- **Playback Controls**: Play, pause, previous, next, and reset
- **Search**: Find and jump to specific words
- **Progress Tracking**: Visual progress bar and word counter
- **Reading Queue**: Queue multiple files or chapters for continuous reading
- **Chapter Detection**: Automatically splits books into chapters
- **Autoplay**: Optionally auto-advance to the next queued item

## System Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- PyPDF2 (for PDF support)

### Platform-Specific Notes

| Platform | tkinter Installation |
|----------|---------------------|
| **Windows** | Included with Python |
| **macOS** | Included with Python |
| **Ubuntu/Debian** | `sudo apt-get install python3-tk` |
| **Fedora** | `sudo dnf install python3-tkinter` |
| **Arch** | `sudo pacman -S tk` |

## Usage Guide

### Opening Files

1. Click **"Open File"** to load a single file
2. Or use **"Add Files"** in the queue panel to add multiple files
3. For books with chapters, use **"Add Chapters"** to split them automatically

### Playback Controls

| Button | Action |
|--------|--------|
| **▶ Play / ⏸ Pause** | Start or pause automatic playback |
| **⏮ Previous** | Go back one word |
| **⏭ Next** | Advance one word |
| **⏹ Reset** | Return to the beginning |

### Speed Settings

Use the WPM slider to adjust your reading speed:

| Speed | Best For |
|-------|----------|
| 200-300 WPM | Beginners, complex material |
| 300-450 WPM | Comfortable speed reading |
| 450-600 WPM | Intermediate speed readers |
| 600-1000 WPM | Advanced speed readers |

### Search

1. Type a word in the search box
2. Press **Enter** or click **Search** to find the first occurrence
3. Click **Find Next** to jump to subsequent matches

### Managing the Reading Queue

The queue panel on the right lets you organize your reading session:

- **Add Files**: Add multiple files to the queue
- **Add Chapters**: Extract chapters from a book and queue them separately
- **▲ / ▼**: Reorder items in the queue
- **Remove**: Remove the selected item
- **Clear**: Empty the entire queue
- **Autoplay next**: When enabled, automatically starts the next item when one finishes
- **Double-click**: Play any item in the queue

## Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain Text | `.txt` | UTF-8 encoded |
| PDF | `.pdf` | Text-based PDFs (not scanned images) |
| EPUB | `.epub` | Standard e-book format |
| PUB | `.pub` | E-book format variant |

## Using as a Library

You can integrate the RSVP components into your own Python projects:

```python
from file_parser import FileParser
from token_displayer import RSVPTokenDisplayer

# Parse a file into tokens
parser = FileParser("book.epub")
tokens = parser.parse()

# Or parse into chapters
chapters = parser.parse_chapters()
for chapter_name, chapter_tokens in chapters.items():
    print(f"{chapter_name}: {len(chapter_tokens)} words")

# Create a displayer for navigation
displayer = RSVPTokenDisplayer(tokens, wpm=400)

# Navigate through tokens
print(displayer.get_current_token())  # Get current word
displayer.next_token()                 # Move forward
displayer.previous_token()             # Move backward
displayer.seek(100)                    # Jump to position
displayer.set_speed(500)               # Change WPM

# Search for text
index = displayer.search("keyword", start_from=0)
if index is not None:
    displayer.seek(index)
```

## Project Structure

```
rsvp-reader/
├── rsvp_reader.py          # Main GUI application
├── file_parser.py          # File parsing (TXT, PDF, EPUB)
├── token_displayer.py      # Token navigation and playback state
├── test_file_parser.py     # Unit tests for file parser
├── test_token_displayer.py # Unit tests for token displayer
├── test_integration.py     # Integration tests
├── example.txt             # Sample text file for testing
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Running Tests

```bash
# Run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Run specific test files
python -m unittest test_file_parser.py -v
python -m unittest test_token_displayer.py -v

# Run integration tests
python test_integration.py
```

## Troubleshooting

### "No module named 'tkinter'"

Install tkinter for your platform (see [System Requirements](#system-requirements)).

### "No module named 'PyPDF2'"

```bash
pip install PyPDF2
```

### PDF file shows no content

The PDF might contain only scanned images rather than text. RSVP Reader can only extract text-based PDFs.

### EPUB file doesn't load correctly

Some EPUBs have non-standard formatting. Try converting to a standard EPUB format using Calibre or similar tools.

### Words appear too fast or slow

Adjust the WPM slider. Start at 250-300 WPM and gradually increase as you become comfortable.

### Application window is too small

Resize the window by dragging its edges. The layout will adapt to the new size.

## Tips for Effective Speed Reading

1. **Start slow**: Begin at 250-300 WPM and gradually increase
2. **Focus on the center**: Keep your eyes fixed on the display area
3. **Reduce subvocalization**: Try not to "speak" words in your mind
4. **Practice regularly**: Speed reading improves with consistent practice
5. **Monitor comprehension**: Slow down if you're not retaining information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
