# Quick Release Guide

Fast reference for creating a new release.

## Prerequisites

```bash
pip install pyinstaller
```

## Build Installers

### Windows

```bash
python build_windows_installer.py
```

Output: `dist/DictToAnki-Installer.exe`

### macOS

```bash
zip -r DictToAnki-macOS.zip . \
  -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "build/*" -x "dist/*"
```

## Create Release

```bash
# 1. Tag version
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0

# 2. Go to GitHub → Releases → New Release

# 3. Upload:
#    - DictToAnki-Installer.exe
#    - DictToAnki-macOS.zip

# 4. Publish
```

## Release Notes Template

```markdown
# Dict-to-Anki v1.0.0

## Downloads
- Windows: DictToAnki-Installer.exe (requires Python 3.8+)
- macOS: DictToAnki-macOS.zip (requires Python 3.8+)

## Installation
See [INSTALL.md](INSTALL.md)

## What's New
- [List changes here]

## Requirements
- Python 3.8+
- Anki + AnkiConnect
```

## Testing Checklist

- [ ] Test on clean Windows machine
- [ ] Test on clean macOS machine  
- [ ] Verify installer works
- [ ] Test hotkey functionality
- [ ] Test Anki integration
- [ ] Check all docs are updated

## Done!

See `DISTRIBUTION_GUIDE.md` for full details.
