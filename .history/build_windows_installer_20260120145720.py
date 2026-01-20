"""Build Windows installer executable using PyInstaller."""

import subprocess
import sys
import os
import shutil

def build_installer():
    """Build the Windows installer .exe."""
    
    print("Building Dict-to-Anki Windows Installer...")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable
        '--windowed',                   # No console window
        '--name=DictToAnki-Installer',  # Output name
        '--icon=assets/icon.ico' if os.path.exists('assets/icon.ico') else '',
        '--add-data=requirements.txt;.',  # Include requirements.txt
        '--add-data=README.md;.',         # Include README
        '--add-data=src;src',             # Include src directory
        '--add-data=platform_integration;platform_integration',  # Include platform_integration
        '--add-data=main.py;.',           # Include main.py
        'installer_gui.py'
    ]
    
    # Remove empty icon parameter if no icon exists
    cmd = [arg for arg in cmd if arg]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd)
        
        print("\n" + "=" * 60)
        print("Build successful!")
        print(f"Installer created: dist/DictToAnki-Installer.exe")
        print("\nYou can now distribute this .exe file to users.")
        print("Users will need Python 3.8+ installed.")
        print("=" * 60)
        
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    build_installer()
