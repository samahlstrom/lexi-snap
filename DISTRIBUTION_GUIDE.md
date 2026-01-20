# Distribution Guide for Dict-to-Anki

This guide explains how to package and distribute Dict-to-Anki to end users.

## Overview

Dict-to-Anki is distributed as:
- **Windows**: Single `.exe` installer (requires Python pre-installed)
- **macOS**: `.zip` package with GUI installer script

## For Users

Users download from GitHub Releases and run the installer which:
1. Checks prerequisites (Python, Anki, AnkiConnect)
2. Installs Python dependencies automatically
3. Sets up the hotkey service (Windows) or Automator (macOS)
4. Provides usage instructions

**User Requirements:**
- Python 3.8+ (must be pre-installed)
- Anki Desktop
- AnkiConnect add-on

## Building Installers

### Windows Installer

```bash
# Install PyInstaller if needed
pip install pyinstaller

# Build the installer
python build_windows_installer.py

# Output: dist/DictToAnki-Installer.exe
```

**What it includes:**
- GUI installer wizard (`installer_gui.py`)
- All source code (src/, platform_integration/)
- requirements.txt
- main.py
- README.md

**What users need:**
- Python 3.8+ installed on their system
- The installer will use their Python to install dependencies

### macOS Package

```bash
# Create distributable zip
zip -r DictToAnki-macOS.zip \
  installer_gui.py \
  main.py \
  requirements.txt \
  src/ \
  platform_integration/ \
  README.md \
  INSTALL.md \
  QUICKSTART.md \
  -x "*.pyc" -x "__pycache__/*"
```

Users extract and run: `python3 installer_gui.py`

## Creating a GitHub Release

### Step 1: Prepare

```bash
# Make sure everything is committed
git status

# Update version in README if needed
# Test on clean machines

# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Step 2: Build Installers

```bash
# Windows
python build_windows_installer.py

# macOS
zip -r DictToAnki-macOS.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "build/*" -x "dist/*"
```

### Step 3: Create Release on GitHub

1. Go to: https://github.com/yourusername/dict-to-anki/releases
2. Click "Create a new release"
3. Choose tag: `v1.0.0`
4. Release title: `Dict-to-Anki v1.0.0`
5. Add release notes (see template below)
6. Upload files:
   - `DictToAnki-Installer.exe`
   - `DictToAnki-macOS.zip`
7. Publish release

### Release Notes Template

```markdown
# Dict-to-Anki v1.0.0

Create Anki flashcards instantly from any selected text!

## Downloads

- **Windows**: [DictToAnki-Installer.exe](link) - Requires Python 3.8+
- **macOS**: [DictToAnki-macOS.zip](link) - Requires Python 3.8+

## Installation

See [INSTALL.md](INSTALL.md) for detailed instructions.

**Quick Start:**
1. Install Python 3.8+ and Anki
2. Install AnkiConnect add-on (code: 2055492159)
3. Run the installer
4. Follow the wizard

## Features

- System-wide text capture (works in any app)
- Automatic dictionary definitions
- Fast hotkey workflow (Ctrl+Alt+D on Windows)
- Seamless Anki integration

## Requirements

- Python 3.8 or higher
- Anki Desktop with AnkiConnect add-on
- Internet connection

## What's New in v1.0.0

- Initial release
- Windows global hotkey support
- macOS Automator service support
- GUI installer wizard
- Automatic dependency installation

## Known Issues

- Windows: Requires Administrator privileges for global hotkey
- macOS: Requires manual Automator workflow setup

## Support

- Documentation: [README.md](README.md)
- Issues: [GitHub Issues](https://github.com/yourusername/dict-to-anki/issues)
```

## Testing Before Release

### Windows Testing

1. Test on clean Windows VM or machine
2. Install Python 3.8+ fresh
3. Run installer as normal user
4. Run installer as Administrator
5. Verify hotkey works
6. Test with Anki

### macOS Testing

1. Test on clean macOS machine
2. Extract zip
3. Run installer
4. Complete Automator setup
5. Test service

## Troubleshooting Distribution

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" in built .exe
Add missing module to `build_windows_installer.py`:
```python
'--hidden-import=module_name',
```

### Large .exe file size
This is normal - PyInstaller bundles Python interpreter and all dependencies.
Typical size: 20-50 MB

### Users report "Python not found"
Users must install Python first. Update INSTALL.md to emphasize this.

## Updating Releases

For bug fixes or new features:

1. Fix code and test
2. Update version number
3. Create new tag: `v1.0.1`, `v1.1.0`, etc.
4. Build new installers
5. Create new release on GitHub
6. Users download new version

## Support After Release

- Monitor GitHub Issues
- Respond to questions
- Fix critical bugs quickly
- Plan feature updates based on feedback

## Marketing

After release, announce on:
- Reddit: r/Anki, r/languagelearning
- Anki Forums
- Twitter/X
- Your blog/website

Include:
- Screenshot/GIF of it working
- Link to releases
- Brief description
- Installation requirements
