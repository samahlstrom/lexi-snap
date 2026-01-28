@echo off
echo ================================================
echo Dict-to-Anki Installer
echo ================================================
echo.
echo Installing dependencies...
pip install pyperclip pyautogui requests pynput pystray Pillow psutil
echo.
echo ================================================
echo Installation complete!
echo.
echo To start: Double-click start.bat
echo          or run: pythonw dict_to_anki_app.py
echo.
echo The app will run in your system tray.
echo Press Ctrl+Alt+D on any selected text!
echo ================================================
pause
