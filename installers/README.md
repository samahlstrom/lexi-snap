# Installers

This directory contains pre-built installers for distribution.

## Building Installers

### Windows

```bash
python build_windows_installer.py
```

Output: `dist/DictToAnki-Installer.exe`

### macOS

```bash
# Create distributable zip
zip -r DictToAnki-macOS.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "build/*" -x "dist/*"
```

## Distribution

Upload the built installers to GitHub Releases:

1. Tag a version: `git tag -a v1.0.0 -m "Version 1.0.0"`
2. Push tag: `git push origin v1.0.0`
3. Create release on GitHub
4. Upload installers as release assets

See [RELEASE.md](../RELEASE.md) for full release process.
