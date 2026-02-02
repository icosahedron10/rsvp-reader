# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RSVP Reader is a Python speed-reading application using Rapid Serial Visual Presentation (RSVP) - displaying text one word at a time at adjustable speeds (100-1000 WPM). Supports TXT, PDF, EPUB, and PUB file formats.

## Commands

```bash
# Activate the virtual environment (required before running anything)
source .claude/claude_env.sh

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.rsvp_reader

# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run specific test file
python -m unittest tests.test_file_parser -v
python -m unittest tests.test_token_displayer -v

# Run integration tests
python -m tests.test_integration
```

## Project Structure

```
rsvp-reader/
├── src/                    # Source code
│   ├── __init__.py
│   ├── file_parser.py      # File parsing and tokenization
│   ├── token_displayer.py  # Playback state management
│   └── rsvp_reader.py      # Main GUI application
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_file_parser.py
│   ├── test_token_displayer.py
│   ├── test_integration.py
│   └── example.txt         # Sample file for testing
└── .claude/                # Autonomous agent infrastructure
```

## Architecture

The codebase follows a three-part modular architecture:

1. **FileParser** (`src/file_parser.py`): Handles file parsing and tokenization
   - Parses TXT (direct read), PDF (via PyPDF2), EPUB/PUB (as ZIP archives with XHTML)
   - `parse()` returns flat token list; `parse_chapters()` returns dict of chapter_name -> tokens
   - Chapter detection uses regex patterns for "Chapter X", "Part X", "Section X" headings

2. **RSVPTokenDisplayer** (`src/token_displayer.py`): Manages playback state and navigation
   - Stateful token iterator with play/pause/seek/search functionality
   - Calculates display delay based on WPM and word length (longer words display longer)
   - Provides progress tracking (percentage, current index, total tokens)

3. **RSVPReaderUI** (`src/rsvp_reader.py`): Tkinter GUI application
   - Uses `tk.after()` for non-blocking word display during playback
   - Reading queue system: stores list of (display_name, tokens) tuples
   - Supports light/dark themes and customizable accent colors
   - Keyboard shortcuts: Space (play/pause), Left/Right (prev/next), R (reset), Ctrl+O (open)

## Key Dependencies

- **PyPDF2**: PDF text extraction
- **tkinter-tooltip**: Hover tooltips for UI elements
- **tkinter**: GUI (usually bundled with Python, may need separate install on Linux)

## Coding Principles

1. **Descriptive variable names**: Use full, descriptive names rather than abbreviations. Exceptions: Python stdlib conventions like `std`, `min`, `max`, `idx`, `i` for loop counters.

2. **Simplicity over complexity**: Prefer straightforward solutions. When considering imports, evaluate whether the module serves an integral purpose or merely saves minor effort. Avoid dependencies that don't provide substantial value.

3. **Section-level comments**: Write block comments that describe what a section of code will accomplish, rather than line-by-line commentary. Explain the "what and why" upfront, then let the code speak for itself.

4. **Docstrings for all functions**: Every function should have a docstring. Match the level of detail to the function's complexity—simple functions need brief descriptions, complex functions need thorough explanations of parameters, return values, and behavior.

5. **No redundant code**: Before adding new functions or utilities, verify the functionality doesn't already exist in the codebase. Each addition should serve a unique purpose to prevent code bloat.

6. **Commit early and often**: Create commits frequently, ideally once or more per TODO item completed. Reserve pushes to the remote for the end of a coding session.

## Autonomous Agent Setup

The `.claude/` directory contains infrastructure for autonomous coding sessions:

| File | Purpose |
|------|---------|
| `STATE.md` | Current codebase snapshot—updated at session end |
| `GOALS.md` | North star and current goals with acceptance criteria |
| `RUNLOG.md` | Session log with timestamps, summaries, commit hashes |
| `run_agent.py` | Two-phase runner (planner → executor) |
| `agent_rules.txt` | Behavioral constraints appended to system prompt |
| `claude_env.sh` | Activates `.venv/claude-base` virtual environment |

**Autonomous run constraints:**
- Work on `agent/auto` branch, no push (human reviews and pushes)
- Tools limited to: Bash, Read, Edit, Write, Grep, Glob
- Complete all goals sequentially, commit per goal
- Run tests after each significant change
- Update STATE.md, GOALS.md, RUNLOG.md before session ends
