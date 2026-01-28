# Dict-to-Anki

Create Anki flashcards from any selected text with a simple hotkey. Works system-wide - no admin required!

## Features

✓ **System-wide hotkey** (Ctrl+Alt+D) - works in any app
✓ **No admin required** - installs and runs as regular user
✓ **System tray app** - runs silently in background
✓ **Auto definitions** - fetches from dictionary API
✓ **Simple UI** - just select deck and go

## Installation

1. **Install dependencies:**
   ```
   Double-click install.bat
   ```

2. **Make sure you have:**
   - Anki installed and running
   - AnkiConnect add-on (code: 2055492159)

## Usage

1. **Start the app:**
   ```
   Double-click start.bat
   ```
   Look for the icon in your system tray (bottom-right)

2. **Create a card:**
   - Highlight any word
   - Press **Ctrl+Alt+D**
   - Select a deck
   - Done!

3. **Settings:**
   - Double-click the tray icon
   - Or right-click → Settings

## How It Works

One simple file: `dict_to_anki_app.py`

- Uses `pynput` for global hotkeys (no admin needed!)
- Runs in system tray with `pystray`
- Optional settings window
- Connects to Anki via AnkiConnect

## Auto-Start (Optional)

To start automatically on Windows login:

1. Press Win+R
2. Type: `shell:startup`
3. Create shortcut to `start.bat` in that folder

## Requirements

- Python 3.8+
- Anki with AnkiConnect add-on
- Windows (macOS support coming)

## Files

- `dict_to_anki_app.py` - Main application (one file!)
- `start.bat` - Launch script
- `install.bat` - Install dependencies

That's it. No complex installer, no build process, no BS.

## Troubleshooting

**"Anki not running"**
- Start Anki before using the app
- Install AnkiConnect add-on from Anki

**"Hotkey not working"**
- Check system tray - is the app running?
- Try restarting the app

**"No text selected"**
- Make sure to highlight text first
- Press Ctrl+Alt+D while text is selected

## License

MIT
