"""
Part Three: RSVP Reader UI
A graphical user interface for the RSVP reader with search bar, speed controls,
and file queue management.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Tuple
from file_parser import FileParser
from token_displayer import RSVPTokenDisplayer
from tktooltip import ToolTip


class RSVPReaderUI:
    """
    Main UI for the RSVP Reader application.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the RSVP Reader UI.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("RSVP Speed Reader")
        self.root.geometry("1000x650")

        self.displayer: Optional[RSVPTokenDisplayer] = None
        self.is_playing = False
        self.after_id = None

        # Queue state: list of (display_name, tokens) tuples
        self.queue: List[Tuple[str, List[str]]] = []
        self.current_queue_index = -1
        self.autoplay_enabled = tk.BooleanVar(value=True)

        self._setup_ui()
        self._setup_keyboard_bindings()
        
    def _setup_ui(self) -> None:
        """
        Set up the user interface components.
        """
        # Main container with two columns: reader (left) and queue (right)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)  # Reader takes more space
        main_frame.columnconfigure(1, weight=1)  # Queue panel
        main_frame.rowconfigure(0, weight=1)

        # Left side: Reader controls
        reader_frame = ttk.Frame(main_frame)
        reader_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        reader_frame.columnconfigure(0, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(reader_frame, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        self.open_button = ttk.Button(file_frame, text="Open File", command=self._open_file)
        self.open_button.grid(row=0, column=0, sticky=tk.W)
        ToolTip(self.open_button, msg="Open a file (Ctrl+O)", delay=0.5)

        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # RSVP display section
        display_frame = ttk.LabelFrame(reader_frame, text="RSVP Display", padding="20")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        reader_frame.rowconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        self.word_label = tk.Label(
            display_frame,
            text="Load a file to begin",
            font=("Arial", 48, "bold"),
            fg="#2c3e50",
            bg="#ecf0f1",
            relief=tk.RAISED,
            padx=20,
            pady=20
        )
        self.word_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress section
        progress_frame = ttk.Frame(reader_frame)
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.position_label = ttk.Label(progress_frame, text="0 / 0")
        self.position_label.grid(row=1, column=0)

        # Control buttons section
        control_frame = ttk.LabelFrame(reader_frame, text="Playback Controls", padding="10")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.play_button = ttk.Button(
            control_frame, text="▶ Play", command=self._toggle_play
        )
        self.play_button.grid(row=0, column=0, padx=5)
        ToolTip(self.play_button, msg="Play/Pause (Space)", delay=0.5)

        self.prev_button = ttk.Button(control_frame, text="⏮ Previous", command=self._previous_word)
        self.prev_button.grid(row=0, column=1, padx=5)
        ToolTip(self.prev_button, msg="Previous word (Left Arrow)", delay=0.5)

        self.next_button = ttk.Button(control_frame, text="⏭ Next", command=self._next_word)
        self.next_button.grid(row=0, column=2, padx=5)
        ToolTip(self.next_button, msg="Next word (Right Arrow)", delay=0.5)

        self.reset_button = ttk.Button(control_frame, text="⏹ Reset", command=self._reset)
        self.reset_button.grid(row=0, column=3, padx=5)
        ToolTip(self.reset_button, msg="Reset to beginning (R)", delay=0.5)

        # Speed control section
        speed_frame = ttk.LabelFrame(reader_frame, text="Speed Control", padding="10")
        speed_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        speed_frame.columnconfigure(1, weight=1)

        ttk.Label(speed_frame, text="WPM:").grid(row=0, column=0, sticky=tk.W)

        self.speed_var = tk.IntVar(value=300)
        self.speed_slider = ttk.Scale(
            speed_frame,
            from_=100,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._update_speed
        )
        self.speed_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        ToolTip(self.speed_slider, msg="Reading speed (100-1000 words per minute)", delay=0.5)

        self.speed_label = ttk.Label(speed_frame, text="300 WPM")
        self.speed_label.grid(row=0, column=2, sticky=tk.E)

        # Search section
        search_frame = ttk.LabelFrame(reader_frame, text="Search", padding="10")
        search_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Find:").grid(row=0, column=0, sticky=tk.W)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        self.search_entry.bind('<Return>', lambda e: self._search())
        ToolTip(self.search_entry, msg="Type text to find in document (Enter to search)", delay=0.5)

        self.search_button = ttk.Button(search_frame, text="Search", command=self._search)
        self.search_button.grid(row=0, column=2, padx=(0, 5))
        ToolTip(self.search_button, msg="Find text in document", delay=0.5)

        self.find_next_button = ttk.Button(search_frame, text="Find Next", command=self._search_next)
        self.find_next_button.grid(row=0, column=3)
        ToolTip(self.find_next_button, msg="Find next occurrence", delay=0.5)

        # Right side: Queue panel
        self._setup_queue_panel(main_frame)

    def _setup_queue_panel(self, parent: ttk.Frame) -> None:
        """
        Set up the queue panel on the right side.
        """
        queue_frame = ttk.LabelFrame(parent, text="Reading Queue", padding="10")
        queue_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(1, weight=1)

        # Queue controls at top
        controls_frame = ttk.Frame(queue_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.add_files_button = ttk.Button(controls_frame, text="Add Files", command=self._add_to_queue)
        self.add_files_button.grid(row=0, column=0, padx=2)
        ToolTip(self.add_files_button, msg="Add one or more files to the reading queue", delay=0.5)

        self.add_chapters_button = ttk.Button(controls_frame, text="Add Chapters", command=self._add_chapters_to_queue)
        self.add_chapters_button.grid(row=0, column=1, padx=2)
        ToolTip(self.add_chapters_button, msg="Extract chapters from a file and add to queue", delay=0.5)

        # Queue listbox with scrollbar
        list_frame = ttk.Frame(queue_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.queue_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=10)
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.queue_listbox.bind('<Double-1>', lambda e: self._play_selected())
        ToolTip(self.queue_listbox, msg="Double-click to play an item", delay=0.5)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.queue_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_listbox.config(yscrollcommand=scrollbar.set)

        # Queue manipulation buttons
        btn_frame = ttk.Frame(queue_frame)
        btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        self.move_up_button = ttk.Button(btn_frame, text="▲", width=3, command=self._move_up)
        self.move_up_button.grid(row=0, column=0, padx=2)
        ToolTip(self.move_up_button, msg="Move selected item up", delay=0.5)

        self.move_down_button = ttk.Button(btn_frame, text="▼", width=3, command=self._move_down)
        self.move_down_button.grid(row=0, column=1, padx=2)
        ToolTip(self.move_down_button, msg="Move selected item down", delay=0.5)

        self.remove_button = ttk.Button(btn_frame, text="Remove", command=self._remove_from_queue)
        self.remove_button.grid(row=0, column=2, padx=2)
        ToolTip(self.remove_button, msg="Remove selected item from queue", delay=0.5)

        self.clear_button = ttk.Button(btn_frame, text="Clear", command=self._clear_queue)
        self.clear_button.grid(row=0, column=3, padx=2)
        ToolTip(self.clear_button, msg="Clear entire queue", delay=0.5)

        # Autoplay checkbox
        autoplay_frame = ttk.Frame(queue_frame)
        autoplay_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        self.autoplay_checkbox = ttk.Checkbutton(
            autoplay_frame,
            text="Autoplay next",
            variable=self.autoplay_enabled
        )
        self.autoplay_checkbox.grid(row=0, column=0, sticky=tk.W)
        ToolTip(self.autoplay_checkbox, msg="Automatically start next item when current finishes", delay=0.5)

        self.play_selected_button = ttk.Button(autoplay_frame, text="Play Selected", command=self._play_selected)
        self.play_selected_button.grid(row=0, column=1, padx=(10, 0))
        ToolTip(self.play_selected_button, msg="Start playing selected queue item", delay=0.5)

    def _setup_keyboard_bindings(self) -> None:
        """
        Set up keyboard bindings for the application.
        """
        # Play/Pause with Space (except when in search entry)
        self.root.bind('<space>', self._on_space_pressed)

        # Navigation with arrow keys
        self.root.bind('<Left>', lambda e: self._previous_word())
        self.root.bind('<Right>', lambda e: self._next_word())

        # Reset with R
        self.root.bind('<r>', lambda e: self._reset())
        self.root.bind('<R>', lambda e: self._reset())

        # Open file with Ctrl+O
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-O>', lambda e: self._open_file())

        # Stop/Pause with Escape
        self.root.bind('<Escape>', self._on_escape_pressed)

    def _on_space_pressed(self, event: tk.Event) -> str:
        """
        Handle space key press for play/pause.
        Ignores if focus is in search entry.
        """
        # Don't toggle play if typing in search entry
        if event.widget == self.search_entry:
            return ""
        self._toggle_play()
        return "break"  # Prevent default space behavior

    def _on_escape_pressed(self, event: tk.Event) -> None:
        """
        Handle Escape key to stop playback.
        """
        if self.is_playing:
            self._toggle_play()

    def _add_to_queue(self) -> None:
        """Add files to the queue."""
        file_paths = filedialog.askopenfilenames(
            title="Select files to add to queue",
            filetypes=[
                ("All supported", "*.txt *.pdf *.epub *.pub"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("EPUB files", "*.epub *.pub"),
                ("All files", "*.*")
            ]
        )

        for file_path in file_paths:
            try:
                parser = FileParser(file_path)
                tokens = parser.parse()
                if tokens:
                    name = file_path.split('/')[-1]
                    self.queue.append((name, tokens))
                    self.queue_listbox.insert(tk.END, name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}: {str(e)}")

    def _add_chapters_to_queue(self) -> None:
        """Add chapters from a file to the queue."""
        file_path = filedialog.askopenfilename(
            title="Select file to extract chapters",
            filetypes=[
                ("All supported", "*.txt *.pdf *.epub *.pub"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("EPUB files", "*.epub *.pub"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                parser = FileParser(file_path)
                chapters = parser.parse_chapters()
                base_name = file_path.split('/')[-1]

                for chapter_name, tokens in chapters.items():
                    if tokens:
                        display_name = f"{base_name} - {chapter_name}"
                        self.queue.append((display_name, tokens))
                        self.queue_listbox.insert(tk.END, display_name)

                if chapters:
                    messagebox.showinfo(
                        "Chapters Added",
                        f"Added {len(chapters)} chapter(s) from {base_name}"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load chapters: {str(e)}")

    def _remove_from_queue(self) -> None:
        """Remove selected item from queue."""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            self.queue_listbox.delete(index)
            self.queue.pop(index)
            if self.current_queue_index >= len(self.queue):
                self.current_queue_index = len(self.queue) - 1

    def _clear_queue(self) -> None:
        """Clear the entire queue."""
        self.queue.clear()
        self.queue_listbox.delete(0, tk.END)
        self.current_queue_index = -1

    def _move_up(self) -> None:
        """Move selected item up in queue."""
        selection = self.queue_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.queue[index], self.queue[index - 1] = self.queue[index - 1], self.queue[index]
            item = self.queue_listbox.get(index)
            self.queue_listbox.delete(index)
            self.queue_listbox.insert(index - 1, item)
            self.queue_listbox.selection_set(index - 1)

    def _move_down(self) -> None:
        """Move selected item down in queue."""
        selection = self.queue_listbox.curselection()
        if selection and selection[0] < len(self.queue) - 1:
            index = selection[0]
            self.queue[index], self.queue[index + 1] = self.queue[index + 1], self.queue[index]
            item = self.queue_listbox.get(index)
            self.queue_listbox.delete(index)
            self.queue_listbox.insert(index + 1, item)
            self.queue_listbox.selection_set(index + 1)

    def _play_selected(self) -> None:
        """Play the selected queue item."""
        selection = self.queue_listbox.curselection()
        if selection:
            self._play_queue_item(selection[0])
        elif self.queue:
            self._play_queue_item(0)

    def _play_queue_item(self, index: int) -> None:
        """Play a specific queue item by index."""
        if 0 <= index < len(self.queue):
            name, tokens = self.queue[index]
            self.current_queue_index = index
            self.displayer = RSVPTokenDisplayer(tokens, self.speed_var.get())
            self.file_label.config(text=name)
            self._update_display()
            self.queue_listbox.selection_clear(0, tk.END)
            self.queue_listbox.selection_set(index)
            self.queue_listbox.see(index)

    def _play_next_in_queue(self) -> None:
        """Advance to next item in queue if autoplay is enabled."""
        if self.autoplay_enabled.get() and self.current_queue_index >= 0:
            next_index = self.current_queue_index + 1
            if next_index < len(self.queue):
                self._play_queue_item(next_index)
                if not self.is_playing:
                    self._toggle_play()

    def _open_file(self) -> None:
        """
        Open a file dialog and load the selected file.
        """
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("All supported", "*.txt *.pdf *.epub *.pub"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("EPUB files", "*.epub *.pub"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                parser = FileParser(file_path)
                tokens = parser.parse()
                
                if not tokens:
                    messagebox.showwarning("Empty File", "The selected file is empty.")
                    return
                
                self.displayer = RSVPTokenDisplayer(tokens, self.speed_var.get())
                self.file_label.config(text=file_path.split('/')[-1])
                self._update_display()
                messagebox.showinfo(
                    "File Loaded",
                    f"Successfully loaded {len(tokens)} words from file."
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def _update_display(self) -> None:
        """
        Update the word display with the current token.
        """
        if not self.displayer:
            return
        
        token = self.displayer.get_current_token()
        if token:
            self.word_label.config(text=token)
        else:
            self.word_label.config(text="[End]")
            self.is_playing = False
            self.play_button.config(text="▶ Play")
        
        # Update progress
        progress = self.displayer.get_progress_percentage()
        self.progress_var.set(progress)
        
        current = self.displayer.get_current_index() + 1
        total = self.displayer.get_total_tokens()
        self.position_label.config(text=f"{current} / {total}")
    
    def _toggle_play(self) -> None:
        """
        Toggle play/pause state.
        """
        if not self.displayer:
            messagebox.showinfo("No File", "Please load a file first.")
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_button.config(text="⏸ Pause")
            self._play_next()
        else:
            self.play_button.config(text="▶ Play")
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
    
    def _play_next(self) -> None:
        """
        Play the next word in the sequence.
        """
        if not self.is_playing or not self.displayer:
            return
        
        token = self.displayer.get_current_token()
        if token:
            self._update_display()
            delay = int(self.displayer.get_delay() * 1000)  # Convert to milliseconds
            self.after_id = self.root.after(delay, self._advance_and_play)
        else:
            self.is_playing = False
            self.play_button.config(text="▶ Play")
            # Try to advance to next queue item if autoplay is enabled
            self._play_next_in_queue()
    
    def _advance_and_play(self) -> None:
        """
        Advance to next token and continue playing.
        """
        if not self.displayer:
            return
        
        self.displayer.next_token()
        self._play_next()
    
    def _previous_word(self) -> None:
        """
        Go to the previous word.
        """
        if not self.displayer:
            return
        
        self.displayer.previous_token()
        self._update_display()
    
    def _next_word(self) -> None:
        """
        Go to the next word.
        """
        if not self.displayer:
            return
        
        self.displayer.next_token()
        self._update_display()
    
    def _reset(self) -> None:
        """
        Reset to the beginning.
        """
        if not self.displayer:
            return
        
        if self.is_playing:
            self._toggle_play()
        
        self.displayer.reset()
        self._update_display()
    
    def _update_speed(self, value: str) -> None:
        """
        Update the playback speed.
        
        Args:
            value: Speed value from slider
        """
        wpm = int(float(value))
        self.speed_label.config(text=f"{wpm} WPM")
        
        if self.displayer:
            self.displayer.set_speed(wpm)
    
    def _search(self) -> None:
        """
        Search for the query string in tokens.
        """
        if not self.displayer:
            messagebox.showinfo("No File", "Please load a file first.")
            return
        
        query = self.search_var.get()
        if not query:
            return
        
        index = self.displayer.search(query, 0)
        if index is not None:
            self.displayer.seek(index)
            self._update_display()
        else:
            messagebox.showinfo("Not Found", f"'{query}' not found in the text.")
    
    def _search_next(self) -> None:
        """
        Search for the next occurrence of the query string.
        """
        if not self.displayer:
            messagebox.showinfo("No File", "Please load a file first.")
            return
        
        query = self.search_var.get()
        if not query:
            return
        
        # Search from the next position
        index = self.displayer.search(query, self.displayer.get_current_index() + 1)
        if index is not None:
            self.displayer.seek(index)
            self._update_display()
        else:
            messagebox.showinfo("Not Found", f"No more occurrences of '{query}' found.")


def main():
    """
    Main entry point for the RSVP Reader application.
    """
    root = tk.Tk()
    app = RSVPReaderUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
