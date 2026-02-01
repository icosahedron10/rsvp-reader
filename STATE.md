# STATE

## Repo snapshot
- Base branch: main
- Agent branch: agent/auto
- Last run: February 1, 2026

## What is true right now

### Project Overview
RSVP Reader - A Python speed reading application using Rapid Serial Visual Presentation (RSVP). Displays words one at a time at configurable speeds.

### Implementation Status
All three parts are **fully implemented**:

1. **Part One: File Parser** (`file_parser.py`) ✅ Complete
   - `FileParser` class with `.txt`, `.pdf`, `.epub`, and `.pub` support
   - Token preservation (punctuation, special chars)
   - Convenience function `parse_file()`
   - Chapter detection via `parse_chapters()` method

2. **Part Two: Token Displayer** (`token_displayer.py`) ✅ Complete
   - `RSVPTokenDisplayer` class
   - Navigation: next/previous/seek/reset
   - Speed control (WPM configurable)
   - Search functionality (case-insensitive)
   - Progress tracking

3. **Part Three: RSVP Reader UI** (`rsvp_reader.py`) ✅ Complete
   - Tkinter-based GUI (800x600 window)
   - File selection dialog
   - Large word display (48pt bold)
   - Playback controls (play/pause/next/previous/reset)
   - Speed slider (100-1000 WPM)
   - Search bar with Find Next
   - Progress bar and position counter

### Build/Test Status
- **Dependencies installed**: PyPDF2 3.0.1, pytest 9.0.2, tkinter-tooltip 3.1.2
- **All tests pass**: 41 tests (19 parser, 22 displayer) - verified Feb 1, 2026
- **Test files exist**:
  - `test_file_parser.py` - 19 unit tests (including EPUB and chapter parsing)
  - `test_token_displayer.py` - 22 unit tests
  - `test_integration.py` - End-to-end integration test
- **Demo**: `demo.py` demonstrates all features

### File Inventory
| File | Purpose | Status |
|------|---------|--------|
| `file_parser.py` | Text/PDF parsing | Complete |
| `token_displayer.py` | RSVP display logic | Complete |
| `rsvp_reader.py` | Tkinter GUI | Complete |
| `test_file_parser.py` | Parser unit tests | Written |
| `test_token_displayer.py` | Displayer unit tests | Written |
| `test_integration.py` | Integration tests | Written |
| `demo.py` | Feature demonstration | Written |
| `demo.txt` | 652-word demo file for showcasing app | Complete |
| `example.txt` | Sample text file | Present |
| `requirements.txt` | Dependencies | PyPDF2>=3.0.0, tkinter-tooltip>=2.1.0 |
| `CLAUDE.md` | Claude Code guidance file | Complete |

### Known Issues

## Recent changes
- 2026-02-01: Added EPUB/PUB file parsing support to FileParser
- 2026-02-01: Added parse_chapters() method for chapter-separated output
- 2026-02-01: Added 11 new tests for EPUB and chapter parsing (19 total parser tests)
- 2026-02-01: Created demo.txt (652 words) for showcasing app features
- 2026-02-01: Created CLAUDE.md for Claude Code guidance

## Blockers / needs human input
