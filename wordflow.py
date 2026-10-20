import tkinter as tk
from tkinter import messagebox
import threading
import time

try:
    import pyautogui
    import pyperclip
except ImportError:
    pyautogui = None
    pyperclip = None

BG = "#171a21"
PANEL = "#222733"
KEY = "#303847"
KEY_HOVER = "#414d61"
ACCENT = "#6ea8fe"
TEXT = "#f2f5fa"
MUTED = "#aab4c5"


class WordFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WordFlow Keyboard")
        self.root.geometry("1000x570")
        self.root.minsize(760, 500)
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)

        self.source_text = ""
        self.words = []
        self.word_index = 0
        self.char_index = 0
        self.character_mode = False
        self.shifted = False
        self.symbol_page = 0
        self.speed = 0
        self.target_window = None
        self.running = False
        self.stop_event = threading.Event()

        self.build_ui()
        self.refresh_status()

    def button(self, parent, label, command, *, bg=KEY, fg=TEXT, height=1):
        b = tk.Button(parent, text=label, command=command, bg=bg, fg=fg,
                      activebackground=KEY_HOVER, activeforeground=TEXT,
                      relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10),
                      padx=8, pady=7, height=height)
        b.bind("<Enter>", lambda _e: b.configure(bg=KEY_HOVER) if bg == KEY else None)
        b.bind("<Leave>", lambda _e: b.configure(bg=bg))
        return b

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=14, pady=(12, 5))
        tk.Label(header, text="WordFlow", bg=BG, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(side="left")
        tk.Label(header, text="WINDOWS KEYBOARD", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=12, pady=(8, 0))
        self.target_label = tk.Label(header, text="Target: not armed", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 9))
        self.target_label.pack(side="right", padx=6)

        controls = tk.Frame(self.root, bg=PANEL)
        controls.pack(fill="x", padx=14, pady=5)
        self.button(controls, "Arm target (select app)", self.arm_target, bg=ACCENT, fg="#101722").pack(side="left", padx=5, pady=6)
        self.button(controls, "Load clipboard", self.load_clipboard).pack(side="left", padx=4, pady=6)
        self.mode_button = self.button(controls, "Mode: Word", self.toggle_mode)
        self.mode_button.pack(side="left", padx=4, pady=6)
        self.button(controls, "Previous", self.previous).pack(side="left", padx=4, pady=6)
        self.button(controls, "Next", self.next_item).pack(side="left", padx=4, pady=6)
        self.button(controls, "Skip", self.skip).pack(side="left", padx=4, pady=6)
        self.button(controls, "Reset", self.reset).pack(side="left", padx=4, pady=6)
        self.write_button = self.button(controls, "▶ Write All", self.start_stop, bg="#315f50")
        self.write_button.pack(side="left", padx=4, pady=6)
        self.speed_button = self.button(controls, "Speed: Fast", self.cycle_speed)
        self.speed_button.pack(side="left", padx=4, pady=6)

        preview = tk.Frame(self.root, bg=PANEL)
        preview.pack(fill="x", padx=14, pady=(5, 8))
        self.status = tk.Label(preview, text="Ready. Arm a target app, then load text.", bg=PANEL, fg=MUTED,
                               anchor="w", font=("Segoe UI", 10))
        self.status.pack(fill="x", padx=10, pady=(8, 2))
        self.preview = tk.Label(preview, text="Clipboard preview appears here.", bg=PANEL, fg=TEXT,
                                anchor="w", justify="left", wraplength=930, font=("Consolas", 11))
        self.preview.pack(fill="x", padx=10, pady=(2, 9))

        self.keyboard = tk.Frame(self.root, bg=BG)
        self.keyboard.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.render_keyboard()

        tk.Label(self.root, text="Text stays on this device • Use only where normal input/paste is permitted",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(pady=(0, 7))

    def render_keyboard(self):
        for child in self.keyboard.winfo_children():
            child.destroy()
        if self.symbol_page == 0:
            rows = ["qwertyuiop", "asdfghjkl", "⇧zxcvbnm⌫"]
            for row_index, row in enumerate(rows):
                frame = tk.Frame(self.keyboard, bg=BG)
                frame.pack(fill="x", pady=3)
                if row_index == 1:
                    frame.pack_configure(padx=32)
                for ch in row:
                    if ch == "⇧":
                        label, action, width = "⇧ Shift", self.toggle_shift, 1.5
                    elif ch == "⌫":
                        label, action, width = "⌫", self.backspace, 1.5
                    else:
                        label = ch.upper() if self.shifted else ch
                        action, width = (lambda c=ch: self.insert_text(c.upper() if self.shifted else c)), 1
                    b = self.button(frame, label, action)
                    b.pack(side="left", fill="both", expand=True, padx=2)
            frame = tk.Frame(self.keyboard, bg=BG)
            frame.pack(fill="x", pady=3)
            keys = [
                ("?123", self.show_numbers, 1.2), (",", lambda: self.insert_text(","), .7),
                ("☺", lambda: self.insert_text("😊"), .7), ("Space", lambda: self.insert_text(" "), 4),
                (".", lambda: self.insert_text("."), .7), ("Enter", lambda: self.insert_text("\n"), 1.2)
            ]
        elif self.symbol_page == 1:
            rows = ["1234567890", "@#$%&-+()/", "*\"':;!?"]
            for row in rows:
                frame = tk.Frame(self.keyboard, bg=BG)
                frame.pack(fill="x", pady=3)
                for ch in row:
                    b = self.button(frame, ch, lambda c=ch: self.insert_text(c))
                    b.pack(side="left", fill="both", expand=True, padx=2)
            frame = tk.Frame(self.keyboard, bg=BG)
            frame.pack(fill="x", pady=3)
            keys = [("ABC", self.show_letters, 1.2), ("More symbols", self.show_extra, 1.5),
                    (",", lambda: self.insert_text(","), .7), ("Space", lambda: self.insert_text(" "), 4),
                    (".", lambda: self.insert_text("."), .7), ("Enter", lambda: self.insert_text("\n"), 1.2)]
        else:
            rows = ["~`|•√π÷×§∆", "€¥$¢^°={}\\", "%©®™✓[]<>"]
            for row in rows:
                frame = tk.Frame(self.keyboard, bg=BG)
                frame.pack(fill="x", pady=3)
                for ch in row:
                    b = self.button(frame, ch, lambda c=ch: self.insert_text(c))
                    b.pack(side="left", fill="both", expand=True, padx=2)
            frame = tk.Frame(self.keyboard, bg=BG)
            frame.pack(fill="x", pady=3)
            keys = [("ABC", self.show_letters, 1.2), ("123", self.show_numbers, 1.2),
                    (",", lambda: self.insert_text(","), .7), ("Space", lambda: self.insert_text(" "), 4),
                    (".", lambda: self.insert_text("."), .7), ("Enter", lambda: self.insert_text("\n"), 1.2)]
        for label, action, weight in keys:
            b = self.button(frame, label, action)
            b.pack(side="left", fill="both", expand=True, padx=2)

    def arm_target(self):
        if pyautogui is None:
            messagebox.showerror("Missing dependency", "Install requirements.txt first.")
            return
        self.root.iconify()
        self.status.configure(text="Click the destination app now. Capturing active window in 4 seconds…")
        self.root.after(4000, self.capture_target)

    def capture_target(self):
        try:
            win = pyautogui.getActiveWindow()
            if win is None or not win.title:
                raise RuntimeError("No active window detected.")
            self.target_window = win
            self.target_label.configure(text="Target: " + win.title[:36], fg="#8ee0b6")
            self.root.deiconify()
            self.root.attributes("-topmost", True)
            self.status.configure(text="Target armed. Use keyboard buttons or Next/Write All.")
        except Exception as exc:
            self.root.deiconify()
            self.status.configure(text="Could not capture target. Try Arm target again.")
            messagebox.showwarning("Target not captured", str(exc))

    def load_clipboard(self):
        try:
            self.source_text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("Clipboard empty", "Copy some text first, then click Load clipboard.")
            return
        self.words = self.source_text.split()
        self.word_index = 0
        self.char_index = 0
        self.refresh_status("Clipboard loaded")

    def refresh_status(self, message=None):
        total = len(self.source_text)
        if self.character_mode:
            progress = f"Character {min(self.char_index + 1, total)}/{total}"
            current = self.source_text[self.char_index:self.char_index + 1] if self.char_index < total else "—"
        else:
            progress = f"Word {min(self.word_index + 1, len(self.words))}/{len(self.words)}"
            current = self.words[self.word_index] if self.word_index < len(self.words) else "—"
        self.status.configure(text=(message + " • " if message else "") + progress)
        self.preview.configure(text=f"Next: {current!r}     |     Preview: {self.source_text[:180]!r}")
        self.mode_button.configure(text="Mode: Character" if self.character_mode else "Mode: Word")

    def insert_text(self, text):
        if not text:
            return
        if pyautogui is None or pyperclip is None:
            messagebox.showerror("Missing dependency", "Install requirements.txt first.")
            return
        if self.target_window is None:
            messagebox.showinfo("Arm target first", "Click Arm target, then select the app where text should be inserted.")
            return
        try:
            self.target_window.activate()
            time.sleep(0.12)
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            self.root.after(0, self.refresh_status)
        except Exception as exc:
            self.status.configure(text=f"Insert failed: {exc}")

    def next_item(self):
        if self.character_mode:
            if self.char_index >= len(self.source_text):
                self.refresh_status("End of text")
                return
            self.insert_text(self.source_text[self.char_index])
            self.char_index += 1
        else:
            if self.word_index >= len(self.words):
                self.refresh_status("End of text")
                return
            word = self.words[self.word_index]
            # Preserve original separators by locating the next token from the cursor.
            self.insert_text(word + " ")
            self.word_index += 1
        self.refresh_status()

    def previous(self):
        if self.character_mode:
            self.char_index = max(0, self.char_index - 1)
        else:
            self.word_index = max(0, self.word_index - 1)
        self.refresh_status("Previous item selected")

    def skip(self):
        if self.character_mode:
            self.char_index = min(len(self.source_text), self.char_index + 1)
        else:
            self.word_index = min(len(self.words), self.word_index + 1)
        self.refresh_status("Skipped")

    def reset(self):
        self.word_index = 0
        self.char_index = 0
        self.refresh_status("Reset")

    def toggle_mode(self):
        self.character_mode = not self.character_mode
        self.refresh_status()

    def toggle_shift(self):
        self.shifted = not self.shifted
        self.render_keyboard()

    def backspace(self):
        if pyautogui and self.target_window:
            try:
                self.target_window.activate()
                time.sleep(.1)
                pyautogui.press("backspace")
            except Exception as exc:
                self.status.configure(text=f"Backspace failed: {exc}")

    def show_letters(self):
        self.symbol_page = 0
        self.render_keyboard()

    def show_numbers(self):
        self.symbol_page = 1
        self.render_keyboard()

    def show_extra(self):
        self.symbol_page = 2
        self.render_keyboard()

    def cycle_speed(self):
        self.speed = (self.speed + 1) % 3
        self.speed_button.configure(text=["Speed: Fast", "Speed: Normal", "Speed: Slow"][self.speed])

    def start_stop(self):
        if self.running:
            self.stop_event.set()
            self.write_button.configure(text="▶ Write All")
            self.status.configure(text="Stopping…")
            return
        if not self.source_text:
            messagebox.showinfo("No text loaded", "Copy text and click Load clipboard first.")
            return
        if not self.target_window:
            messagebox.showinfo("Arm target first", "Arm the target app before writing.")
            return
        self.running = True
        self.stop_event.clear()
        self.write_button.configure(text="■ Stop")
        threading.Thread(target=self.write_all_worker, daemon=True).start()

    def write_all_worker(self):
        delay = [0.18, 0.5, 1.0][self.speed]
        try:
            if self.character_mode:
                while self.char_index < len(self.source_text) and not self.stop_event.is_set():
                    self.insert_text(self.source_text[self.char_index])
                    self.char_index += 1
                    time.sleep(delay)
            else:
                while self.word_index < len(self.words) and not self.stop_event.is_set():
                    self.insert_text(self.words[self.word_index] + " ")
                    self.word_index += 1
                    self.root.after(0, self.refresh_status)
                    time.sleep(delay)
        finally:
            self.running = False
            self.root.after(0, lambda: self.write_button.configure(text="▶ Write All"))
            self.root.after(0, self.refresh_status)

    def on_close(self):
        self.stop_event.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WordFlowApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
