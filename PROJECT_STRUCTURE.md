# Project Structure

```
dict-to-anki/
│
├── main.py                           # Application entry point
├── test_basic.py                     # Basic functionality tests
├── requirements.txt                  # Python dependencies
├── README.md                         # Full documentation
├── QUICKSTART.md                     # Quick start guide
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
│
├── src/                              # Core application modules
│   ├── __init__.py
│   ├── text_capture.py               # Cross-platform text capture
│   ├── dictionary_service.py         # Dictionary API client
│   ├── anki_service.py               # AnkiConnect integration
│   ├── gui_dialogs.py                # Deck selection & notifications
│   └── config_manager.py             # Configuration management
│
├── platform_integration/             # Platform-specific integrations
│   ├── __init__.py
│   ├── windows_menu.py               # Windows context menu setup
│   └── macos_service.py              # macOS Automator service helper
│
├── tests/                            # Unit tests (future)
│   └── (test files will go here)
│
├── assets/                           # Images, icons, etc.
│   └── (assets will go here)
│
└── installers/                       # Distribution packages
    └── (compiled executables will go here)
```

## Key Files

### Core Application

- **main.py** (5.3 KB)
  - Entry point for the application
  - Orchestrates the entire workflow
  - Command-line argument parsing
  - Error handling and user feedback

### Source Modules (src/)

- **text_capture.py** (2.1 KB)
  - TextCapture class for getting highlighted text
  - Cross-platform clipboard simulation (Ctrl+C / Cmd+C)
  - Word extraction from selection

- **dictionary_service.py** (4.2 KB)
  - DictionaryService class for API calls
  - Primary API: dictionaryapi.dev
  - Backup API: freedictionaryapi.com
  - Parses and formats definitions

- **anki_service.py** (4.6 KB)
  - AnkiService class for AnkiConnect integration
  - Fetches deck names
  - Creates flashcards
  - Formats HTML card content

- **gui_dialogs.py** (5.9 KB)
  - DeckSelectionDialog with search functionality
  - Desktop notifications (plyer)
  - Error dialogs with tkinter

- **config_manager.py** (4.2 KB)
  - ConfigManager class for settings
  - Platform-specific config location
  - Default configuration generation

### Platform Integration (platform_integration/)

- **windows_menu.py** (3.6 KB)
  - Windows registry context menu integration
  - Requires administrator privileges
  - Install/uninstall functions

- **macos_service.py** (4.7 KB)
  - macOS Automator Quick Action helper
  - Creates helper script for Automator
  - Detailed setup instructions

### Testing

- **test_basic.py** (4.0 KB)
  - Tests configuration manager
  - Tests dictionary API connection
  - Tests AnkiConnect connection
  - Provides diagnostic output

## Configuration

User configuration is stored at:
- **Windows**: `%APPDATA%\dict-to-anki\config.ini`
- **macOS**: `~/.config/dict-to-anki/config.ini`

## Dependencies

### Required (cross-platform)
- pyperclip - Clipboard access
- pyautogui - Keyboard simulation
- requests - HTTP requests for Dictionary API
- plyer - Desktop notifications

### Windows-specific
- pywin32 - Windows API access
- (context-menu library removed due to complexity)

### macOS-specific
- pyobjc-core - Objective-C bridge
- pyobjc-framework-Cocoa - macOS Cocoa framework

## Data Flow

```
[User highlights text]
        ↓
[Right-click menu / Service]
        ↓
[main.py]
        ↓
[TextCapture] → Copy to clipboard → Extract word
        ↓
[DictionaryService] → API call → Parse definitions
        ↓
[GUI Dialog] → User selects deck
        ↓
[AnkiService] → Format card → AnkiConnect API
        ↓
[Card created in Anki]
        ↓
[Success notification]
```

## Build Process (Future)

1. PyInstaller to create executables:
   - Windows: DictToAnki.exe
   - macOS: DictToAnki.app

2. Platform-specific installers:
   - Windows: Inno Setup (.exe installer)
   - macOS: DMG with app bundle

## Total Lines of Code

- Core modules: ~700 lines
- Platform integration: ~300 lines
- Testing: ~130 lines
- Documentation: ~500 lines
- **Total: ~1,630 lines**

## Development Status

✓ Core functionality implemented
✓ Cross-platform text capture
✓ Dictionary API integration
✓ AnkiConnect integration
✓ GUI deck selection
✓ Configuration management
✓ Windows context menu
✓ macOS service helper
✓ Documentation complete
✓ Basic testing implemented

## Future Additions

- [ ] Unit tests with pytest
- [ ] PyInstaller build scripts
- [ ] Platform-specific installers
- [ ] Global hotkey support
- [ ] Custom Anki note types
- [ ] Multi-language support
