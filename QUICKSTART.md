# Quick Start Guide

## What Lexi Snap Does

A **modern desktop application** for creating Anki flashcards:
- Beautiful CustomTkinter dark UI with sidebar navigation
- Global hotkey (Ctrl+Alt+D) - works WITHOUT admin
- System tray app - runs silently
- Auto-start on Windows login
- Professional Windows installer
- Card history and notification options

## Run It Now

```bash
cd C:\Users\Sam\Documents\GitHub\dict-to-anki
python app.py
```

The app will:
1. Start in your system tray (look bottom-right)
2. Double-click the tray icon to open settings

## Test the Workflow

1. Make sure Anki is running with AnkiConnect installed
2. Highlight any word in your browser
3. Press **Ctrl+Alt+D**
4. Dialog appears - select deck - click "Add Card"
5. Badge counter updates on tray icon!

**Pro tip:** Set a default deck in settings for instant adds (no dialog!)

## Build Installer (For Distribution)

### Step 1: Build Executable

```bash
pip install pyinstaller
python build_installer.py
```

This creates: `dist/lexi-snap.exe` (30-40MB standalone)

### Step 2: Create Windows Installer

Download [Inno Setup](https://jrsoftware.org/isdl.php) (free), then:

```powershell
cd C:\Users\Sam\Documents\GitHub\dict-to-anki
iscc installer.iss
```

This creates: `Output/lexi-snap-Setup.exe`

## File Structure

```
lexi-snap/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── build_installer.py     # PyInstaller build script
├── lexi-snap.spec         # PyInstaller spec file
├── installer.iss          # Inno Setup configuration
├── README.md              # User documentation
└── assets/                # App icons
    ├── icon.ico
    └── icon.png
```

## Features

- **Sidebar Navigation** - General, Notifications, History tabs
- **CustomTkinter** - smooth, anti-aliased, professional
- **No admin** - uses pynput (official Windows APIs)
- **Fast workflow** - <1 second to add cards
- **Modern dark theme** - Navy blue primary, pinkish-red accents

## Customization

Users can customize in settings:

**General Tab:**
- **Hotkey** - Change from Ctrl+Alt+D to anything (or reset to disable)
- **Default Deck** - Set for instant adds (skip dialog)
- **Auto-Start** - Toggle Windows startup

**Notifications Tab:**
- **Card Counter Badge** - Shows on tray icon
- **Toast Notification** - Semi-transparent corner popup

**History Tab:**
- View 10 most recent cards
- Clicking clears the badge counter

All settings saved to: `~/.lexi_snap_settings.json`

## Publishing to GitHub

When ready to release:

1. **Tag a release:**
   ```bash
   git tag -a v1.0.0 -m "First release"
   git push origin v1.0.0
   ```

2. **Upload installer:**
   - Go to GitHub -> Releases -> Create Release
   - Upload `Output/lexi-snap-Setup.exe`
   - Users download and double-click - done!

## Success!

You now have a **professional desktop app** that:
- Looks modern (CustomTkinter)
- Requires no admin
- Installs like Discord/Spotify
- Auto-starts on login
- Fast workflow (<1s)
- Beautiful dark UI
- Sidebar navigation with tabs
