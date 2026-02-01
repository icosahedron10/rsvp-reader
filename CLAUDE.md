# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the GUI application:**
```bash
python rsvp_reader.py
```

**Run all tests:**
```bash
python -m unittest discover -s . -p "test_*.py" -v
```

**Run a specific test file:**
```bash
python -m unittest test_file_parser.py -v
python -m unittest test_token_displayer.py -v
```

**Run integration tests:**
```bash
python test_integration.py
```

## Architecture

This is an RSVP (Rapid Serial Visual Presentation) speed reading application with three main components:

1. **file_parser.py** - `FileParser` class that extracts tokens from .txt, .pdf, .epub, and .pub files. Uses PyPDF2 for PDF, standard library (zipfile, xml) for EPUB. Tokens are whitespace-split words with punctuation preserved. `parse_chapters()` method splits content by chapter headings.

2. **token_displayer.py** - `RSVPTokenDisplayer` class that manages token navigation and playback state. Handles WPM-based timing, play/pause/seek controls, and search functionality. This is a stateful class that tracks current position and playback state.

3. **rsvp_reader.py** - `RSVPReaderUI` class that provides the Tkinter GUI. Integrates FileParser and RSVPTokenDisplayer. Uses `root.after()` for non-blocking playback timing rather than the displayer's synchronous `play()` method.

## Key Patterns

- The UI owns the event loop timing - it calls `displayer.next_token()` and `displayer.get_current_token()` directly rather than using the displayer's blocking `play()` method
- Speed is measured in WPM (words per minute), converted to delay via `60.0 / wpm`
- Search is case-insensitive substring matching
