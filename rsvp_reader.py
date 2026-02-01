"""
Part Three: RSVP Reader UI
A graphical user interface for the RSVP reader with search bar and speed controls.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from file_parser import FileParser
from token_displayer import RSVPTokenDisplayer


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
        self.root.geometry("800x600")
        
        self.displayer: Optional[RSVPTokenDisplayer] = None
        self.is_playing = False
        self.after_id = None
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """
        Set up the user interface components.
        """
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Button(file_frame, text="Open File", command=self._open_file).grid(
            row=0, column=0, sticky=tk.W
        )
        
        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # RSVP display section
        display_frame = ttk.LabelFrame(main_frame, text="RSVP Display", padding="20")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
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
        progress_frame = ttk.Frame(main_frame)
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
        control_frame = ttk.LabelFrame(main_frame, text="Playback Controls", padding="10")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.play_button = ttk.Button(
            control_frame, text="▶ Play", command=self._toggle_play
        )
        self.play_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(control_frame, text="⏮ Previous", command=self._previous_word).grid(
            row=0, column=1, padx=5
        )
        
        ttk.Button(control_frame, text="⏭ Next", command=self._next_word).grid(
            row=0, column=2, padx=5
        )
        
        ttk.Button(control_frame, text="⏹ Reset", command=self._reset).grid(
            row=0, column=3, padx=5
        )
        
        # Speed control section
        speed_frame = ttk.LabelFrame(main_frame, text="Speed Control", padding="10")
        speed_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        speed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(speed_frame, text="WPM:").grid(row=0, column=0, sticky=tk.W)
        
        self.speed_var = tk.IntVar(value=300)
        speed_slider = ttk.Scale(
            speed_frame,
            from_=100,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._update_speed
        )
        speed_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        
        self.speed_label = ttk.Label(speed_frame, text="300 WPM")
        self.speed_label.grid(row=0, column=2, sticky=tk.E)
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="10")
        search_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Find:").grid(row=0, column=0, sticky=tk.W)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        search_entry.bind('<Return>', lambda e: self._search())
        
        ttk.Button(search_frame, text="Search", command=self._search).grid(
            row=0, column=2, padx=(0, 5)
        )
        
        ttk.Button(search_frame, text="Find Next", command=self._search_next).grid(
            row=0, column=3
        )
        
    def _open_file(self) -> None:
        """
        Open a file dialog and load the selected file.
        """
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
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
