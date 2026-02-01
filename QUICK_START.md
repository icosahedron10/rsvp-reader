# RSVP Reader - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/icosahedron10/rsvp-reader.git
cd rsvp-reader

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python rsvp_reader.py
```

## Using the GUI

### 1. Load a File
- Click **"Open File"** button
- Select a `.txt` or `.pdf` file
- The first word will appear in the display

### 2. Control Playback
- **▶ Play/⏸ Pause**: Start or pause automatic word display
- **⏮ Previous**: Go back one word
- **⏭ Next**: Advance one word
- **⏹ Reset**: Return to the beginning

### 3. Adjust Speed
- Use the **WPM slider** to set reading speed
- Range: 100 to 1000 words per minute
- Changes take effect immediately
- Recommended speeds:
  - 200-300 WPM: Comfortable reading
  - 400-600 WPM: Speed reading
  - 700-1000 WPM: Advanced speed reading

### 4. Search for Words
- Type a word in the **search box**
- Click **"Search"** to find first occurrence
- Click **"Find Next"** to find next occurrence
- Search is case-insensitive

### 5. Track Progress
- **Progress bar**: Visual representation
- **Position counter**: Shows current/total words
- Updated in real-time as you read

## Tips for Effective Speed Reading

1. **Start Slow**: Begin at 250-300 WPM and gradually increase
2. **Focus**: Keep your eyes centered on the display area
3. **Don't Subvocalize**: Avoid "speaking" words in your mind
4. **Practice**: Speed reading is a skill that improves with practice
5. **Comprehension**: If comprehension drops, reduce speed

## Keyboard Shortcuts (Future Enhancement)
The current version uses button controls. Future versions may add:
- `Space`: Play/Pause
- `Left Arrow`: Previous word
- `Right Arrow`: Next word
- `Ctrl+F`: Focus search box
- `Ctrl+R`: Reset

## Supported File Types

- **Text Files (.txt)**: Full support with UTF-8 encoding
- **PDF Files (.pdf)**: Extracts text from all pages

## Troubleshooting

**Problem**: "No module named 'tkinter'"
**Solution**: Install tkinter:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: Included with Python
- Windows: Included with Python

**Problem**: "No module named 'PyPDF2'"
**Solution**: `pip install PyPDF2`

**Problem**: PDF file doesn't load
**Solution**: Ensure the PDF contains text (not just images)

**Problem**: Words display too fast/slow
**Solution**: Adjust the WPM slider to your comfortable reading speed

## Examples

### Loading a Text File
1. Click "Open File"
2. Navigate to `example.txt`
3. Click "Open"
4. You'll see "The" (first word) in the display

### Speed Reading Session
1. Load your file
2. Set speed to 400 WPM
3. Click "▶ Play"
4. Focus on the center of the display
5. Click "⏸ Pause" when you need a break

### Finding Specific Content
1. Type "keyword" in search box
2. Click "Search"
3. The display jumps to that word
4. Click "Find Next" to find more occurrences

## Command Line Testing

```bash
# Run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Run demonstration
python demo.py

# Run integration test
python test_integration.py
```

## Getting Help

- Check the README.md for detailed documentation
- Review PROJECT_SUMMARY.md for technical details
- Run demo.py to see features in action

Enjoy speed reading!
