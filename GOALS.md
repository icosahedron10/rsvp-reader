# GOALS

## North star
- Enable a user to reliably read 2 to 3 times faster with equal or better comprehension using Rapid serial visual presentation.

## Current goals (tight scope)

1. Keyboard shortcuts for core actions
   - Acceptance criteria:
     - Space toggles play/pause (except in search field) ✅
     - Left/Right arrows navigate previous/next word ✅
     - R resets to beginning, Ctrl+O opens file, Escape stops ✅
     - Shortcuts work globally regardless of focus ✅
   - Notes: Implemented _setup_keyboard_bindings() in rsvp_reader.py using root.bind()
   - Status: ✅ Complete

2. Tooltips for all interactive elements
   - Acceptance criteria:
     - Every button shows tooltip on 0.5s hover ✅
     - Tooltips include keyboard shortcuts (e.g., "Play/Pause (Space)") ✅
     - Speed slider, queue listbox, and search field have explanatory tooltips ✅
   - Notes: Uses tkinter-tooltip. ToolTip() calls added after widget creation.
   - Status: ✅ Complete

3. Visual status feedback
   - Acceptance criteria:
     - Status bar at bottom shows state ("Playing...", "Paused at word 125", etc.) ✅
     - Word display changes color when playing vs paused ✅
     - Currently playing queue item has distinct highlight ✅
   - Notes: Added status_var StringVar and status bar. Updates in _toggle_play(), _open_file(), _play_queue_item().
   - Status: ✅ Complete

4. Dark Mode
   - Acceptance criteria:
     - Provide a dark theme with high contrast and reduced eye strain (background #121212, text #EAEAEA) ✅
     - Include a user-selectable secondary accent color for highlights (default #4C9FFE) ✅
   - Notes: Theme colors exposed via LIGHT_THEME/DARK_THEME dicts. _apply_theme() applies to all UI elements.
   - Status: ✅ Complete

## Constraints
- Commit often and with descriptive messages
- Keep diffs small and reviewable
- Prefer minimal dependencies
