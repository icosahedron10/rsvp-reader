# RSVP Reader - Quick Start Guide

Get reading in under a minute.

## Installation

```bash
git clone https://github.com/icosahedron10/rsvp-reader.git
cd rsvp-reader
pip install -r requirements.txt
```

## Launch

```bash
python rsvp_reader.py
```

## Basic Workflow

### 1. Load a File

Click **"Open File"** and select a `.txt`, `.pdf`, `.epub`, or `.pub` file.

### 2. Start Reading

Click **▶ Play** to begin. Words display one at a time in the center.

### 3. Adjust Speed

Drag the **WPM slider** to set your pace:
- **250-300**: Comfortable reading
- **400-500**: Speed reading
- **600+**: Advanced

### 4. Control Playback

| Button | Action |
|--------|--------|
| ▶ / ⏸ | Play/Pause |
| ⏮ | Previous word |
| ⏭ | Next word |
| ⏹ | Reset to start |

### 5. Search

Type in the search box and press **Enter** to jump to that word.

## Queue Panel (Right Side)

For longer reading sessions:

- **Add Files**: Queue multiple files
- **Add Chapters**: Split a book into chapters automatically
- **Double-click**: Jump to any queued item
- **Autoplay next**: Continue to next item when current one ends

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named 'tkinter'" | Ubuntu: `sudo apt-get install python3-tk` |
| "No module named 'PyPDF2'" | `pip install PyPDF2` |
| PDF shows nothing | PDF may be scanned images, not text |

## Supported Files

- `.txt` - Plain text (UTF-8)
- `.pdf` - PDF documents (text-based)
- `.epub` / `.pub` - E-books

## Next Steps

- See **README.md** for full documentation
- Try `example.txt` to test the application
- Run `python demo.py` for a feature demonstration

Happy speed reading!
