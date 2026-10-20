# WordFlow for Windows

A Windows desktop companion to the WordFlow Android keyboard, built with Python and Tkinter.

## Features
- On-screen QWERTY keyboard with Shift, Backspace, Space, Enter, numbers and symbol pages.
- Extra symbols page: `~ ` | • √ π ÷ × § ∆ € ¥ $ ¢ ^ ° = { } % © ® ™ ✓ [ ] < >`.
- Load clipboard text, then insert the next word or character.
- Previous, Skip, Reset and Write All controls.
- Fast, Normal and Slow automatic insertion speeds.
- Dark, resizable desktop UI.

## Run
1. Install Python 3.10 or newer from https://www.python.org/downloads/windows/ (enable **Add Python to PATH**).
2. Open this folder in Command Prompt or PowerShell.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python wordflow.py`.

Or double-click `run-wordflow.bat`.

## How text insertion works
Click **Arm target**, then switch to the application where you want to type within 5 seconds. WordFlow remembers that target window. Clicking a keyboard key or using Next/Write All pastes text into that target using the Windows clipboard and Ctrl+V. The target application must allow normal paste/input.

**Privacy:** Clipboard text is processed locally by the app and is not uploaded to a server. Loading clipboard text is explicit. Do not load sensitive clipboard contents unless you intend to type them.

## Notes
- This is a desktop typing companion, not a replacement for the Windows system-wide keyboard or a signed Windows IME.
- Some elevated/admin apps, secure fields, games, or applications that block simulated input may not accept insertion.
- Use Stop to cancel Write All. Avoid switching target windows during automatic insertion.
- The app uses standard Python libraries plus PyAutoGUI for keyboard shortcut automation.
