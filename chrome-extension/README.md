# WordFlow Browser Extension

A Chrome/Edge Manifest V3 companion for the existing WordFlow Windows app. It adds a **WordFlow** submenu to the browser's normal right-click menu when you right-click an editable webpage field.

## Keyboard shortcut

- Default shortcut: **Ctrl + Shift + Y** (starts Write All using the selected default mode and speed).
- If this shortcut conflicts with another app or browser feature, open `chrome://extensions/shortcuts` (or `edge://extensions/shortcuts`) and assign a different shortcut to **WordFlow Browser**.
- Focus the destination webpage text field, copy the text, then press the shortcut. You do not need to use right-click.

## Right-click commands

- **Write All (current mode)** — uses the default mode selected in the extension popup.
- **Write All in Character Mode**
- **Write All in Word Mode**
- **Stop Writing**

Choose **Fast**, **Normal**, or **Slow** in the WordFlow toolbar popup. Character mode writes one character at a time. Word mode writes word-sized chunks while preserving attached punctuation and whitespace.

## Install in Chrome or Edge

1. Download this repository as a ZIP and extract it, or clone the repository.
2. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
3. Enable **Developer mode**.
4. Click **Load unpacked** and select the repository's `chrome-extension` folder.
5. Copy the text you want to type, focus a webpage text field, and press **Ctrl + Shift + Y** to start writing. Or use the right-click menu.
6. Right-click inside a normal webpage text field and choose **WordFlow → Write All in Character Mode** (or Word Mode).
7. Click the WordFlow toolbar icon to configure the default mode and speed. If clipboard reading is unavailable on a particular setup, paste the text into the popup's fallback box and save it first.

## Permissions and privacy

The extension requests context-menu access, local settings storage, clipboard reading, and access to regular HTTP/HTTPS pages so it can detect editable fields and insert text. Clipboard text is read only after you explicitly invoke WordFlow through the shortcut or a right-click command. Text and settings are stored locally by the browser; there is no backend or account.

## Limitations

- Browser menus are managed by Chrome/Edge. WordFlow appears as a submenu in the context menu, typically below the browser's built-in actions; the extension cannot guarantee an exact position relative to Copy/Paste.
- It only works in editable fields on regular webpages. Browser UI, extension pages, the Chrome Web Store, some embedded frames, and secure or custom editors may block input.
- Some complex web apps may not respond to synthetic input the same way as native typing.
- This extension is separate from the Python desktop app; it reproduces the Write All workflow in the browser and does not control the desktop app's current session.
- It has been committed to the repository but has not yet been verified in a live Chrome/Edge session.