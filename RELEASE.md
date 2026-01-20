# Release Checklist

This document is for maintainers creating new releases.

## Pre-Release

1. **Update version numbers:**
   - [ ] Update version in `README.md`
   - [ ] Update version in installer_gui.py (if version is shown)
   - [ ] Create version tag

2. **Test thoroughly:**
   - [ ] Test on clean Windows machine
   - [ ] Test on clean macOS machine
   - [ ] Test all features work
   - [ ] Test installer wizard

3. **Update documentation:**
   - [ ] README.md is up to date
   - [ ] INSTALL.md is accurate
   - [ ] QUICKSTART.md is current

## Building Releases

### Windows

```bash
# Build installer
python build_windows_installer.py

# Test the installer
dist/DictToAnki-Installer.exe

# Verify it works on a clean machine
```

### macOS

```bash
# For macOS, create a .zip of the project
zip -r DictToAnki-macOS.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"

# Or create a .dmg (requires additional tools)
```

## Creating GitHub Release

1. **Tag the release:**
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create release on GitHub:**
   - Go to Releases → Create new release
   - Choose the tag
   - Release title: "Dict-to-Anki v1.0.0"
   - Add release notes (see template below)

3. **Upload assets:**
   - [ ] `DictToAnki-Installer.exe` (Windows)
   - [ ] `DictToAnki-macOS.zip` (macOS)
   - [ ] `Source-Code.zip` (GitHub auto-generates)

## Release Notes Template

```markdown
# Dict-to-Anki v1.0.0

Create Anki flashcards from any selected text with automatic dictionary definitions!

## Installation

### Windows
1. Download `DictToAnki-Installer.exe`
2. Install Python 3.8+ if not already installed
3. Install Anki and AnkiConnect add-on (code: 2055492159)
4. Run the installer
5. Follow setup instructions

### macOS
1. Download `DictToAnki-macOS.zip`
2. Extract and run `python3 installer_gui.py`
3. Follow setup instructions

Full installation guide: [INSTALL.md](INSTALL.md)

## What's New

- Initial release
- Windows global hotkey support (Ctrl+Alt+D)
- macOS Automator service support
- Automatic dictionary definitions from free API
- GUI deck selection
- Desktop notifications

## Requirements

- Python 3.8+
- Anki Desktop with AnkiConnect add-on
- Internet connection (for dictionary API)

## Known Issues

- Windows: Requires Administrator privileges for global hotkey
- macOS: Requires manual Automator setup

## Support

Report issues: [GitHub Issues](https://github.com/yourusername/dict-to-anki/issues)
```

## Post-Release

1. **Announce:**
   - [ ] Reddit (r/Anki, r/languagelearning)
   - [ ] Twitter/X
   - [ ] Anki forums

2. **Monitor:**
   - [ ] Watch for GitHub issues
   - [ ] Respond to questions
   - [ ] Fix critical bugs

## Versioning

We use Semantic Versioning (SemVer):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

Example: v1.2.3
- 1 = Major version
- 2 = Minor version  
- 3 = Patch version
