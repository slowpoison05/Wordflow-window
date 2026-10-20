import re
import tkinter as tk
from tkinter import messagebox

try:
    import pyautogui
    import pyperclip
except ImportError:
    pyautogui = None
    pyperclip = None

BG, PANEL, KEY = "#171a21", "#222733", "#303847"
HOVER, ACCENT, TEXT, MUTED = "#414d61", "#6ea8fe", "#f2f5fa", "#aab4c5"
SUCCESS = "#8ee0b6"


class WordFlowApp:
    """Windows desktop companion for the WordFlow Android keyboard."""

    def __init__(self, root):
        self.root = root
        root.title("WordFlow Keyboard")
        root.geometry("1080x650")
        root.minsize(800, 570)
        root.configure(bg=BG)
        root.attributes("-topmost", True)
        self.source_text = ""
        self.words = []
        self.word_index = self.char_index = 0
        self.character_mode = self.shifted = False
        self.symbol_page = self.speed = 0
        self.target_window = None
        self.write_job = None
        self.running = False
        self.build_ui()
        self.refresh_status("Ready. Arm a target app, then load text.")

    def button(self, parent, label, command, bg=KEY, fg=TEXT, size=10):
        b = tk.Button(parent, text=label, command=command, bg=bg, fg=fg,
                      activebackground=HOVER, activeforeground=TEXT, relief="flat",
                      bd=0, cursor="hand2", font=("Segoe UI", size), padx=9, pady=8)
        b.bind("<Enter>", lambda _e: b.configure(bg=HOVER) if bg == KEY else None)
        b.bind("<Leave>", lambda _e: b.configure(bg=bg))
        return b

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(header, text="WordFlow", bg=BG, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(side="left")
        tk.Label(header, text="WINDOWS KEYBOARD", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=12, pady=(9, 0))
        self.target_label = tk.Label(header, text="Target: not armed", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 9))
        self.target_label.pack(side="right", padx=6)

        controls = tk.Frame(self.root, bg=PANEL)
        controls.pack(fill="x", padx=16, pady=5)
        actions = [
            ("Arm target", self.arm_target, ACCENT, "#101722"),
            ("Load clipboard", self.load_clipboard, KEY, TEXT),
            ("Mode: Word", self.toggle_mode, KEY, TEXT),
            ("Previous", self.previous, KEY, TEXT), ("Next", self.next_item, KEY, TEXT),
            ("Skip", self.skip, KEY, TEXT), ("Reset", self.reset, KEY, TEXT),
            ("Write All", self.start_stop, "#315f50", TEXT),
            ("Speed: Fast", self.cycle_speed, KEY, TEXT),
        ]
        self.action_buttons = {}
        for label, command, bg, fg in actions:
            b = self.button(controls, label, command, bg, fg)
            b.pack(side="left", padx=3, pady=6)
            self.action_buttons[label] = b
        self.mode_button = self.action_buttons["Mode: Word"]
        self.write_button = self.action_buttons["Write All"]
        self.speed_button = self.action_buttons["Speed: Fast"]

        preview = tk.Frame(self.root, bg=PANEL)
        preview.pack(fill="x", padx=16, pady=(5, 8))
        self.status = tk.Label(preview, text="", bg=PANEL, fg=MUTED, anchor="w",
                               font=("Segoe UI", 10))
        self.status.pack(fill="x", padx=12, pady=(8, 2))
        self.preview = tk.Label(preview, text="Load clipboard text to begin.", bg=PANEL,
                                fg=TEXT, anchor="w", justify="left", wraplength=1000,
                                font=("Consolas", 11))
        self.preview.pack(fill="x", padx=12, pady=(2, 9))
        self.keyboard = tk.Frame(self.root, bg=BG)
        self.keyboard.pack(fill="both", expand=True, padx=16)
        self.render_keyboard()
        tk.Label(self.root, text="Text stays on this device • Use only where normal input/paste is permitted",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(pady=(5, 2))
        # Extra breathing room below the keys, matching the Android layout request.
        tk.Frame(self.root, bg=BG, height=20).pack(fill="x")

    def add_row(self, keys, inset=0):
        frame = tk.Frame(self.keyboard, bg=BG)
        frame.pack(fill="x", padx=inset, pady=3)
        for label, command in keys:
            self.button(frame, label, command, size=11).pack(
                side="left", fill="both", expand=True, padx=2, ipady=3)

    def render_keyboard(self):
        for child in self.keyboard.winfo_children():
            child.destroy()
        if self.symbol_page == 0:
            for i, letters in enumerate(("qwertyuiop", "asdfghjkl", "zxcvbnm")):
                keys = []
                if i == 2:
                    keys.append(("⇧ Shift", self.toggle_shift))
                for ch in letters:
                    keys.append((ch.upper() if self.shifted else ch,
                                 lambda c=ch: self.insert_text(c.upper() if self.shifted else c)))
                if i == 2:
                    keys.append(("⌫ Backspace", self.backspace))
                self.add_row(keys, inset=22 if i == 1 else 0)
            self.add_row([
                ("?123", self.show_numbers), (",", lambda: self.insert_text("<" if self.shifted else ",")),
                ("☺", lambda: self.insert_text("😊")), ("Space", lambda: self.insert_text(" ")),
                (".", lambda: self.insert_text(">" if self.shifted else ".")),
                ("Enter", lambda: self.insert_text("\n")),
            ])
        elif self.symbol_page == 1:
            for row in ("1234567890", "@#$%&-+()/", "*\\\"':;!?"):
                self.add_row([(ch, lambda c=ch: self.insert_text(c)) for ch in row])
            self.add_row([
                ("ABC", self.show_letters), ("More symbols", self.show_extra),
                (",", lambda: self.insert_text(",")), ("Space", lambda: self.insert_text(" ")),
                (".", lambda: self.insert_text(".")), ("Enter", lambda: self.insert_text("\n")),
            ])
        else:
            rows = ("~" + chr(96) + "|•√π÷×§∆", "€¥$¢^°={}\\", "%©®™✓[]<>")
            for row in rows:
                self.add_row([(ch, lambda c=ch: self.insert_text(c)) for ch in row])
            self.add_row([
                ("ABC", self.show_letters), ("123", self.show_numbers),
                (",", lambda: self.insert_text(",")), ("Space", lambda: self.insert_text(" ")),
                (".", lambda: self.insert_text(".")), ("Enter", lambda: self.insert_text("\n")),
            ])

    def arm_target(self):
        if pyautogui is None:
            messagebox.showerror("Missing dependency", "Run run-wordflow.bat to install requirements.")
            return
        self.root.iconify()
        self.refresh_status("Click the destination app now. Capturing active window in 4 seconds…")
        self.root.after(4000, self.capture_target)

    def capture_target(self):
        try:
            win = pyautogui.getActiveWindow()
            if win is None or not win.title:
                raise RuntimeError("No active window detected. Try again.")
            self.target_window = win
            self.target_label.configure(text="Target: " + win.title[:42], fg=SUCCESS)
            self.root.deiconify()
            self.root.attributes("-topmost", True)
            self.refresh_status("Target armed. Use keyboard buttons or Next / Write All.")
        except Exception as exc:
            self.root.deiconify()
            self.refresh_status("Could not capture target.")
            messagebox.showwarning("Target not captured", str(exc))

    def load_clipboard(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("Clipboard empty", "Copy text first, then click Load clipboard.")
            return
        self.source_text = text
        # Keep whitespace and punctuation with each word so output matches the source.
        self.words = re.findall(r"\S+\s*", text)
        if text and text[0].isspace() and self.words:
            self.words[0] = text[:len(text) - len(text.lstrip())] + self.words[0]
        self.word_index = self.char_index = 0
        self.refresh_status("Clipboard loaded")

    def refresh_status(self, message=None):
        total = len(self.source_text)
        if self.character_mode:
            progress = f"Character {min(self.char_index + 1, total)}/{total}"
            current = self.source_text[self.char_index:self.char_index + 1] if self.char_index < total else "—"
        else:
            progress = f"Word {min(self.word_index + 1, len(self.words))}/{len(self.words)}"
            current = self.words[self.word_index].strip() if self.word_index < len(self.words) else "—"
        self.status.configure(text=((message + " • ") if message else "") + progress)
        self.preview.configure(text=f"Next: {current!r}    |    Preview: {self.source_text[:180]!r}")
        self.mode_button.configure(text="Mode: Character" if self.character_mode else "Mode: Word")

    def insert_text(self, text):
        if not text:
            return
        if pyautogui is None or pyperclip is None:
            messagebox.showerror("Missing dependency", "Run run-wordflow.bat to install requirements.")
            return
        if self.target_window is None:
            messagebox.showinfo("Arm target first", "Click Arm target, then select the destination app.")
            return
        try:
            self.target_window.activate()
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
        except Exception as exc:
            self.refresh_status("Insert failed: " + str(exc))

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
            self.insert_text(self.words[self.word_index])
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
        self.word_index = self.char_index = 0
        self.refresh_status("Reset")

    def toggle_mode(self):
        self.character_mode = not self.character_mode
        self.refresh_status()

    def toggle_shift(self):
        self.shifted = not self.shifted
        self.render_keyboard()

    def backspace(self):
        if pyautogui is None or self.target_window is None:
            self.refresh_status("Arm a target app before using Backspace")
            return
        try:
            self.target_window.activate()
            pyautogui.press("backspace")
        except Exception as exc:
            self.refresh_status("Backspace failed: " + str(exc))

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
            if self.write_job is not None:
                self.root.after_cancel(self.write_job)
                self.write_job = None
            self.running = False
            self.write_button.configure(text="Write All")
            self.refresh_status("Stopped")
            return
        if not self.source_text:
            messagebox.showinfo("No text loaded", "Copy text and click Load clipboard first.")
            return
        if self.target_window is None:
            messagebox.showinfo("Arm target first", "Arm the destination app before writing.")
            return
        self.running = True
        self.write_button.configure(text="■ Stop")
        self.refresh_status("Writing…")
        self.write_step()

    def write_step(self):
        if not self.running:
            return
        if self.character_mode:
            if self.char_index >= len(self.source_text):
                self.finish_write("Finished")
                return
            text = self.source_text[self.char_index]
            self.char_index += 1
        else:
            if self.word_index >= len(self.words):
                self.finish_write("Finished")
                return
            text = self.words[self.word_index]
            self.word_index += 1
        self.insert_text(text)
        self.refresh_status("Writing…")
        self.write_job = self.root.after([180, 500, 1000][self.speed], self.write_step)

    def finish_write(self, message):
        self.running = False
        self.write_job = None
        self.write_button.configure(text="Write All")
        self.refresh_status(message)

    def on_close(self):
        if self.write_job is not None:
            self.root.after_cancel(self.write_job)
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WordFlowApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
