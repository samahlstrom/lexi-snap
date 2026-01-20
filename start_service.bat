@echo off
REM Dict-to-Anki Service Starter
REM Run this as Administrator to start the hotkey service

echo ================================================
echo Dict-to-Anki Service Starter
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Starting Dict-to-Anki hotkey service...
echo.

python platform_integration\windows_menu.py --start

echo.
echo ================================================
echo Service started!
echo.
echo Press Ctrl+Alt+D on any selected text to create
echo an Anki card.
echo.
echo To stop the service, run:
echo   python platform_integration\windows_menu.py --stop
echo ================================================
echo.
pause
