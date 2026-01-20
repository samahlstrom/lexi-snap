# Dict-to-Anki

A cross-platform tool that lets you highlight any word anywhere on your computer (browsers, PDFs, documents, etc.), right-click, and instantly create an Anki flashcard with definitions and context.

## Features

✨ **System-Wide Text Capture** - Works in browsers, PDFs, Word, any application
📚 **Automatic Definitions** - Fetches top definitions from free dictionary API
🗂️ **Deck Selection** - Choose which Anki deck to add cards to
🖥️ **Cross-Platform** - Works on both Windows and macOS
⚡ **Fast Workflow** - Highlight → Right-click → Done!

## Prerequisites

Before installing Dict-to-Anki, you need:

1. **Anki Desktop** - Download from [ankiweb.net](https://apps.ankiweb.net/)
2. **AnkiConnect Add-on** - Install in Anki:
   - Open Anki
   - Tools → Add-ons → Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki
3. **Python 3.8+** - For running from source (not needed if using compiled executable)

## Installation

### Quick Install (Recommended)

**Download the installer from [Releases](https://github.com/yourusername/dict-to-anki/releases)**

- **Windows**: `DictToAnki-Installer.exe` 
- **macOS**: `DictToAnki-macOS.zip`

See [INSTALL.md](INSTALL.md) for detailed instructions.

### Advanced: Install from Source

#### Windows

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dict-to-anki.git
   cd dict-to-anki
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the hotkey service **(requires administrator)**:
   - Open PowerShell as Administrator (right-click → Run as Administrator)
   - Navigate to project: `cd C:\Users\YourName\Documents\GitHub\dict-to-anki`
   - Run: `python platform_integration/windows_menu.py --start`

4. Done! Press **Ctrl+Alt+D** on any selected text to send to Anki.

**Optional:** Install auto-start to run on Windows startup (requires administrator):
```bash
python platform_integration/windows_menu.py --install
```


### macOS

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dict-to-anki.git
   cd dict-to-anki
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Set up Automator Quick Action:
   ```bash
   python3 platform_integration/macos_service.py --show-instructions
   ```

4. Follow the displayed instructions to create the Automator workflow.

5. Grant Accessibility permissions:
   - System Settings → Privacy & Security → Accessibility
   - Enable for "Automator" or "System Events"

## Usage

### Basic Workflow

1. **Start Anki** - Make sure Anki is running with AnkiConnect installed

2. **Start the service** (Windows only, first time):
   ```bash
   python platform_integration/windows_menu.py --start
   ```

3. **Highlight a word** - Select the word you want to look up

4. **Press hotkey**:
   - **Windows**: Press **Ctrl+Alt+D**
   - **macOS**: Services → Send to Anki (or use keyboard shortcut)

5. **Select deck** - Choose which Anki deck to add the card to

6. **Done!** - The card is created automatically with:
   - **Front**: The word
   - **Back**: Top 3 definitions with examples

### Example

You're reading an article and see: *"The serendipitous discovery changed everything."*

1. Highlight "serendipitous"
2. Press **Ctrl+Alt+D** (Windows) or use Services menu (macOS)
3. Select "English Vocabulary" deck
4. Card created! ✓

The card will look like:

**Front:**
```
serendipitous
```

**Back:**
```
1. (adjective) Occurring or discovered by chance in a happy or beneficial way
Example: A serendipitous encounter

2. (adjective) Having the faculty of making fortunate discoveries by accident
Example: A serendipitous find
```

## Configuration

Configuration file is located at:
- **Windows**: `%APPDATA%\dict-to-anki\config.ini`
- **macOS/Linux**: `~/.config/dict-to-anki/config.ini`

### Settings

```ini
[anki]
ankiconnect_url = http://localhost:8765
max_definitions = 3

[dictionary]
timeout_seconds = 5

[capture]
clipboard_delay_ms = 100
restore_clipboard = true

[ui]
show_notifications = true
```

### Customization

- **max_definitions**: Number of definitions to include (default: 3)
- **clipboard_delay_ms**: Delay for clipboard capture in milliseconds
- **show_notifications**: Show desktop notifications for success/errors

## Command Line Usage

You can also use Dict-to-Anki from the command line:

```bash
# Capture from clipboard
python main.py

# Specify deck directly (skip dialog)
python main.py --deck "English Vocabulary"

# Provide text directly
python main.py --text "serendipity"

# Read from stdin (for scripts)
echo "serendipity" | python main.py --stdin
```

## Troubleshooting

### "Cannot connect to Anki"

**Solution:**
1. Make sure Anki is running
2. Verify AnkiConnect is installed: Tools → Add-ons → check for "AnkiConnect"
3. Restart Anki after installing AnkiConnect
4. Check that AnkiConnect is running on port 8765

### "No text selected"

**Solution:**
1. Make sure text is highlighted before right-clicking
2. Try selecting text again
3. On macOS, ensure Accessibility permissions are granted

### "No definitions found"

**Solution:**
1. Check internet connection (dictionary API requires internet)
2. Verify the word is spelled correctly
3. Try a simpler or more common word to test

### Windows: Hotkey not working

**Solution:**
1. Check if service is running: `python platform_integration/windows_menu.py --status`
2. Start the service: `python platform_integration/windows_menu.py --start`
3. Make sure no other application is using Ctrl+Alt+D
4. Try restarting the service: `python platform_integration/windows_menu.py --restart`

### macOS: Service not showing

**Solution:**
1. Verify the Automator workflow was saved correctly
2. Check System Settings → Keyboard → Keyboard Shortcuts → Services
3. Make sure "Send to Anki" is enabled
4. Grant Accessibility permissions

### Duplicate card error

**Solution:**
- The word already exists in that deck
- Anki's duplicate detection prevents adding the same word twice
- Edit the existing card in Anki or add to a different deck

## Architecture

### Components

- **main.py** - Application entry point and workflow orchestration
- **src/text_capture.py** - Cross-platform text capture using clipboard
- **src/dictionary_service.py** - Dictionary API client (dictionaryapi.dev)
- **src/anki_service.py** - AnkiConnect API integration
- **src/gui_dialogs.py** - Deck selection dialog and notifications
- **src/config_manager.py** - Configuration file management
- **platform_integration/windows_menu.py** - Windows hotkey service manager
- **platform_integration/windows_hotkey_service.py** - Background service for global hotkey
- **platform_integration/macos_service.py** - macOS Automator service helper

### How It Works

1. **Text Capture**: Simulates Ctrl+C (or Cmd+C on Mac) to copy selected text to clipboard
2. **API Call**: Fetches definitions from free dictionary API
3. **Deck Selection**: Shows GUI dialog with available Anki decks
4. **Card Creation**: Formats and creates card via AnkiConnect
5. **Notification**: Shows success/error notification

## Development

### Running from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run directly
python main.py

# Run tests (coming soon)
pytest tests/
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build for Windows
pyinstaller --onefile --windowed --name=DictToAnki main.py

# Build for macOS
pyinstaller --onefile --windowed --name=DictToAnki main.py
```

## API Reference

### Dictionary API

- **Primary**: [dictionaryapi.dev](https://dictionaryapi.dev/)
  - Free, no API key required
  - Comprehensive definitions, examples, synonyms
  - No rate limits

- **Backup**: [freedictionaryapi.com](https://freedictionaryapi.com/)
  - Wiktionary-based
  - Fallback if primary fails

### AnkiConnect API

- **Documentation**: [AnkiConnect GitHub](https://github.com/FooSoft/anki-connect)
- **Port**: 8765 (localhost only)
- **Version**: 6

## Limitations

1. **Anki Must Be Running**: AnkiConnect only works when Anki is open
2. **Internet Required**: Dictionary API needs active connection
3. **Basic Note Type**: Currently only supports Anki's "Basic" card type
4. **macOS Setup**: Requires manual Automator workflow creation

## Future Enhancements

- [ ] Global hotkey option (Ctrl+Shift+A)
- [ ] Offline dictionary fallback
- [ ] Support for custom Anki note types
- [ ] Multi-language dictionaries
- [ ] Browser extension for better web integration
- [ ] Image OCR for text in images
- [ ] Pronunciation audio on cards
- [ ] Batch processing multiple words

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/dict-to-anki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/dict-to-anki/discussions)

## Acknowledgments

- [AnkiConnect](https://github.com/FooSoft/anki-connect) - Anki API integration
- [Free Dictionary API](https://dictionaryapi.dev/) - Dictionary definitions
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard
- [pyautogui](https://github.com/asweigart/pyautogui) - Keyboard simulation

---

**Happy learning! 📚**
