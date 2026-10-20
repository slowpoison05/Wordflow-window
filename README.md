# WordFlow for Windows

A Windows desktop companion to the WordFlow Android keyboard, built with Python and Tkinter. The Windows project is separate from the Android app.

## Features

- Resizable dark desktop interface with a large on-screen QWERTY keyboard.
- Shift, Backspace, Space, Enter, emoji shortcut, number page and extended symbol page.
- Extra symbols: ~, backtick, |, •, √, π, ÷, ×, §, ∆, €, ¥, $, ¢, ^, °, =, { }, %, ©, ®, ™, ✓, [ ], < >.
- Explicit Load clipboard action; choose Word or Character mode.
- Previous, Next, Skip, Reset, and Write All / Stop controls.
- Fast, Normal and Slow automatic insertion speeds.
- Word mode preserves punctuation and whitespace attached to words.
- Text is handled locally; no account, server, or network service is required.

## Run from source

1. Install Python 3.10 or newer from https://www.python.org/downloads/windows/ and enable Add Python to PATH.
2. Open this folder in Command Prompt or PowerShell.
3. Run: python -m pip install -r requirements.txt
4. Run: python wordflow.py

Or double-click run-wordflow.bat to install dependencies and start the app.

## Build a Windows executable

Double-click build-exe.bat. It installs PyInstaller and creates dist\WordFlow.exe. Build it on Windows; the generated executable is not committed to this repository.

## How text insertion works

1. Open the destination app and click Arm target in WordFlow.
2. WordFlow minimizes for four seconds. Click the destination app or its text field while it is minimized.
3. WordFlow captures the active window and restores itself.
4. Load clipboard text, then use the on-screen keys, Next, or Write All.

Text is inserted through the Windows clipboard and Ctrl+V. The destination must permit normal paste/input. Automatic insertion can be stopped with Stop.

## Privacy and limitations

- Clipboard text is read only after you explicitly choose Load clipboard. It stays on your device and is not uploaded.
- This is a desktop typing companion, not a replacement for the Windows system-wide keyboard or a signed Windows IME.
- Some elevated/admin apps, secure fields, games, or applications that block simulated input may reject insertion.
- Avoid switching target windows during automatic insertion. Test first in Notepad.
- PyAutoGUI and Pyperclip are the only runtime dependencies.


## Use WordFlow directly in Chrome or Edge

A browser extension is included in `chrome-extension/`. It adds a **WordFlow** submenu to the right-click menu on editable webpage fields, with Write All in Character Mode, Write All in Word Mode, current mode, and Stop commands.

1. Open `chrome://extensions` (Chrome) or `edge://extensions` (Edge).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select this repository's `chrome-extension` folder.
4. Copy your text, right-click in a webpage text field, then choose **WordFlow → Write All in Character Mode** or **Word Mode**.
5. Use the WordFlow toolbar icon to set the default mode and Fast / Normal / Slow speed.

The extension reads clipboard text only after you choose a WordFlow menu command. If clipboard reading is unavailable, paste text into the extension popup's fallback box and save it. See [the browser extension guide](chrome-extension/README.md).

**Limitations:** Chrome/Edge controls the context-menu layout, so WordFlow's exact position relative to Copy/Paste can vary. Some secure pages, browser UI, cross-origin frames, and custom editors may reject script-based input. The extension is separate from the Python desktop app and has not yet been verified in a live browser session.
