# Release Checklist (lexi-snap)

Use this when cutting a new version or replacing existing GitHub releases with the lexi-snap build.

## Build and package

1. **Build executable**
   ```bash
   pip install pyinstaller
   python build_installer.py
   ```
   Output: `dist/lexi-snap.exe`

2. **Build installer**
   ```bash
   iscc installer.iss
   ```
   Output: `Output/lexi-snap-Setup.exe`

## Publish to GitHub

3. **Tag and push**
   ```bash
   git tag -a v1.1.0 -m "Release 1.1.0 (lexi-snap)"
   git push origin v1.1.0
   ```

4. **Create or edit release**
   - Go to GitHub: Repo -> Releases -> "Draft a new release" (or edit existing).
   - Choose tag `v1.1.0`.
   - Title example: `v1.1.0 - Lexi Snap (lexi-snap)`.
   - In release notes, tell users to download `lexi-snap-Setup.exe`.

5. **Attach installer**
   - Upload `Output/lexi-snap-Setup.exe` as the release asset.
   - Do not attach old `LexiSnap-Setup.exe`; the canonical file is `lexi-snap-Setup.exe`.

## Replacing old releases

- For old releases (e.g. v1.0.0) that had `LexiSnap-Setup.exe`: either delete those releases or add a note that new installs should use the latest release and `lexi-snap-Setup.exe`.
- New releases from this repo use the name **lexi-snap** and the filename **lexi-snap-Setup.exe** only.

## Version bump

Before the next release, update version in:
- `app.py`: `VERSION = "x.y.z"`
- `installer.iss`: `AppVersion=x.y.z`
- `README.md`: version badge URL (e.g. `version-1.1.0`).
