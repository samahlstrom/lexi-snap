"""Build standalone executable with PyInstaller."""

import PyInstaller.__main__
import os
import sys

def build():
    """Build the executable."""
    print("=" * 60)
    print("Building Lexi Snap (lexi-snap) standalone executable...")
    print("=" * 60)

    # Check for icon
    icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

    args = [
        'app.py',
        '--name=lexi-snap',
        '--onefile',
        '--windowed',  # No console window
        '--noconfirm',
        '--clean',
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
    ]

    if icon_path:
        args.append(f'--icon={icon_path}')
        print(f"Using icon: {icon_path}")
    else:
        print("No icon found (optional)")

    # Add assets if they exist
    if os.path.exists('assets'):
        args.append('--add-data=assets;assets')
        print("Including assets folder")

    print("\nBuilding... This may take a few minutes.\n")

    try:
        PyInstaller.__main__.run(args)

        print("\n" + "=" * 60)
        print("Build successful!")
        print(f"\nExecutable: dist\\lexi-snap.exe")
        print("\nNext steps:")
        print("  1. Test: dist\\lexi-snap.exe")
        print("  2. Create installer: iscc installer.iss")
        print("=" * 60)

    except Exception as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    build()
