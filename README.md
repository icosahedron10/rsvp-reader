# RSVP Reader

Basic parsing of text based files into Rapid Serial Visual Presentation streams for efficient speed reading.

## Overview

The RSVP (Rapid Serial Visual Presentation) Reader is a Python application that enables speed reading by displaying words one at a time at a controlled pace. The project is organized into three main components:

### Part One: File Parsing
Parses text-based files (.txt and .pdf) into tokens while carefully preserving the structure of special characters and formatting.

**Features:**
- Support for `.txt` and `.pdf` files
- Preserves punctuation and special characters
- Maintains text structure and formatting
- Tokenizes text into individual words

**Module:** `file_parser.py`

### Part Two: Token Displayer
Creates a class for displaying tokens in RSVP format, managing the presentation logic and playback controls.

**Features:**
- Configurable reading speed (WPM - Words Per Minute)
- Playback controls (play, pause, stop, reset)
- Navigation (next, previous, seek)
- Progress tracking
- Search functionality

**Module:** `token_displayer.py`

### Part Three: RSVP Reader UI
A graphical user interface built with Tkinter that integrates all components and provides user control.

**Features:**
- File selection dialog
- Large, clear word display
- Playback controls (play/pause, next, previous, reset)
- Speed control slider (100-1000 WPM)
- Progress bar and position indicator
- Search bar with "Find Next" functionality

**Module:** `rsvp_reader.py`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/icosahedron10/rsvp-reader.git
cd rsvp-reader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the GUI Application

```bash
python rsvp_reader.py
```

This will launch the graphical interface where you can:
1. Click "Open File" to select a .txt or .pdf file
2. Use the playback controls to start/pause reading
3. Adjust the speed slider to your preferred reading pace
4. Use the search bar to find specific words
5. Navigate through the text using Previous/Next buttons

### Using as a Library

```python
from file_parser import FileParser
from token_displayer import RSVPTokenDisplayer

# Parse a file
parser = FileParser("example.txt")
tokens = parser.parse()

# Create displayer
displayer = RSVPTokenDisplayer(tokens, wpm=300)

# Navigate and search
displayer.next_token()
displayer.set_speed(500)
index = displayer.search("keyword")
```

## Project Structure

```
rsvp-reader/
├── file_parser.py          # Part 1: File parsing module
├── token_displayer.py      # Part 2: RSVP token displayer
├── rsvp_reader.py          # Part 3: GUI application
├── test_file_parser.py     # Tests for file parser
├── test_token_displayer.py # Tests for token displayer
├── test_integration.py     # Integration tests
├── example.txt             # Example text file
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Testing

Run all tests:
```bash
python -m unittest discover -s . -p "test_*.py" -v
```

Run specific test modules:
```bash
python -m unittest test_file_parser.py -v
python -m unittest test_token_displayer.py -v
```

Run integration test:
```bash
python test_integration.py
```

## Requirements

- Python 3.7+
- PyPDF2 (for PDF support)
- tkinter (usually comes with Python)

## Features

- **Multiple File Formats:** Support for .txt and .pdf files
- **Customizable Speed:** Adjust reading speed from 100 to 1000 WPM
- **Search Functionality:** Find and jump to specific words
- **Progress Tracking:** Visual progress bar and position counter
- **Playback Controls:** Full control over reading experience
- **Token Preservation:** Maintains special characters and formatting

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

