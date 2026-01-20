@echo off
REM Dict-to-Anki Service Stopper

echo ================================================
echo Dict-to-Anki Service Stopper
echo ================================================
echo.

echo Stopping Dict-to-Anki hotkey service...
echo.

python platform_integration\windows_menu.py --stop

echo.
echo ================================================
echo Service stopped!
echo ================================================
echo.
pause
