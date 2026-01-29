# Dict-to-Anki

Create Anki flashcards from any selected text with a simple hotkey. Works system-wide - no admin required!

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010/11-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Global Hotkey** - Press `Ctrl+Alt+D` on any selected text (customizable)
- **Auto Dictionary Lookup** - Fetches definitions automatically
- **Modern UI** - Beautiful dark theme with CustomTkinter
- **No Admin Required** - Installs and runs as regular user
- **System Tray** - Runs silently in background
- **Fast Workflow** - Set default deck for instant card creation (<1 second!)
- **Auto-Start** - Optionally launch on Windows startup

## 📥 Installation

### For Normal Users (Recommended)

1. **Download the installer:**
   - Go to [Releases](https://github.com/yourusername/dict-to-anki/releases)
   - Download `DictToAnki-Setup.exe` (latest version)

2. **Run the installer:**
   - Double-click `DictToAnki-Setup.exe`
   - Click "Next" → "Install" → "Finish"
   - App launches automatically

3. **Install AnkiConnect:**
   - Open Anki
   - Go to: Tools → Add-ons → Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki

That's it! No Python, no terminal commands required.

### For Developers

```bash
# Clone repository
git clone https://github.com/yourusername/dict-to-anki
cd dict-to-anki

# Install dependencies
pip install -r requirements.txt

# Run from source
python app.py
```

## 🚀 Usage

### First Time Setup

1. Make sure Anki is running
2. Look for Dict-to-Anki icon in system tray (bottom-right)
3. Double-click the tray icon to open settings
4. (Optional) Set a default deck for faster workflow
5. (Optional) Customize the hotkey

### Creating Cards

**Fast Method (with default deck):**
1. Highlight any word in any application
2. Press `Ctrl+Alt+D`
3. Card added instantly!
4. Notification confirms

**Manual Method (no default deck):**
1. Highlight any word
2. Press `Ctrl+Alt+D`
3. Modern dialog appears with:
   - The word
   - Auto-fetched definition
   - Deck selector
4. Click "Add Card"
5. Done!

### Settings

Double-click the tray icon to access settings:

- **Keyboard Shortcut** - Change the hotkey (e.g., `ctrl+shift+a`)
- **Default Deck** - Select deck for instant adds (or "Ask every time")
- **Launch on Startup** - Toggle auto-start on Windows login

## 🛠️ Requirements

- **Windows 10 or 11**
- **Anki** with **AnkiConnect** add-on (code: 2055492159)
- No Python installation needed (for normal users)

## 🔧 Building from Source

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
python build_installer.py
```

Output: `dist/DictToAnki.exe`

### Create Installer

Requires [Inno Setup](https://jrsoftware.org/isdl.php) (free):

```bash
iscc installer.iss
```

Output: `Output/DictToAnki-Setup.exe`

## 📋 Troubleshooting

### "Anki not running or no decks found"
- Make sure Anki is running
- Install AnkiConnect add-on: Tools → Add-ons → Get Add-ons → Code: `2055492159`
- Restart Anki

### "No text selected"
- Make sure to highlight text before pressing the hotkey
- Try selecting text again and press hotkey while text is highlighted

### Hotkey not working
- Check if another app is using the same hotkey
- Try changing to a different key combination in settings
- Restart the app after changing hotkey

### Windows SmartScreen Warning
- This is normal for apps without code signing ($200/year certificate)
- Click "More info" → "Run anyway"
- The app is safe and open-source

## 🎨 Screenshots

_Coming soon_

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- Dictionary API: [Free Dictionary API](https://dictionaryapi.dev/)
- Anki Integration: [AnkiConnect](https://foosoft.net/projects/anki-connect/)
- UI Framework: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

## ⭐ Star History

If you find this useful, please star the repo!

---

**Made with ❤️ for Anki users**
