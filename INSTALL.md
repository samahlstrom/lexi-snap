# Installation Guide

## For End Users

### Windows

1. **Prerequisites:**
   - Python 3.8 or higher ([Download](https://www.python.org/downloads/))
   - Anki Desktop ([Download](https://apps.ankiweb.net/))

2. **Install AnkiConnect:**
   - Open Anki
   - Tools → Add-ons → Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki

3. **Install Dict-to-Anki:**
   - Download `DictToAnki-Installer.exe` from [Releases](https://github.com/yourusername/dict-to-anki/releases)
   - Run the installer (right-click → Run as Administrator for auto-start)
   - Follow the wizard steps

4. **Start Using:**
   - Make sure Anki is running
   - Open PowerShell as Administrator
   - Navigate to installation directory
   - Run: `python platform_integration/windows_menu.py --start`
   - Highlight any word and press **Ctrl+Alt+D**

### macOS

1. **Prerequisites:**
   - Python 3.8 or higher ([Download](https://www.python.org/downloads/))
   - Anki Desktop ([Download](https://apps.ankiweb.net/))

2. **Install AnkiConnect:**
   - Open Anki
   - Tools → Add-ons → Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki

3. **Install Dict-to-Anki:**
   - Download the repository or release
   - Run: `python3 installer_gui.py`
   - Follow the wizard steps

4. **Set up Automator (macOS only):**
   - Open Automator
   - Create new Quick Action
   - Follow instructions shown in installer

5. **Start Using:**
   - Make sure Anki is running
   - Highlight any word
   - Right-click → Services → Send to Anki

## For Developers

### Building the Installer

**Windows:**
```bash
python build_windows_installer.py
```

This creates `dist/DictToAnki-Installer.exe`

**Requirements for building:**
- PyInstaller: `pip install pyinstaller`
- All project dependencies installed

### Running from Source

See [QUICKSTART.md](QUICKSTART.md) for development setup.

## Troubleshooting

### Windows: "Python not found"
Install Python from python.org and make sure "Add to PATH" is checked during installation.

### "Cannot connect to Anki"
1. Make sure Anki is running
2. Verify AnkiConnect is installed (Tools → Add-ons)
3. Restart Anki

### Windows: Hotkey not working
1. Make sure you ran PowerShell as Administrator
2. Check service status: `python platform_integration/windows_menu.py --status`
3. Restart service: `python platform_integration/windows_menu.py --restart`

### macOS: Service not appearing
1. Check System Settings → Keyboard → Keyboard Shortcuts → Services
2. Make sure "Send to Anki" is enabled
3. Grant Accessibility permissions

## Support

For issues and questions:
- GitHub Issues: [yourusername/dict-to-anki/issues](https://github.com/yourusername/dict-to-anki/issues)
- Documentation: [README.md](README.md)
