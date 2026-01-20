"""Windows global hotkey service for Dict-to-Anki."""

import os
import sys
import subprocess
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, HotKey
import ctypes
import time

# Add parent directory to path to import main modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HotkeyService:
    """Background service that listens for global hotkey."""
    
    def __init__(self, hotkey_combo="<ctrl>+<alt>+d"):
        self.hotkey_combo = hotkey_combo
        self.listener = None
        self.running = False
        
        # Get path to main.py
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.main_script = os.path.join(script_dir, 'main.py')
        self.python_exe = sys.executable
        
    def on_activate(self):
        """Called when hotkey is pressed."""
        print(f"Hotkey activated: {self.hotkey_combo}")
        
        try:
            # Run main.py to capture and process text
            # Use CREATE_NO_WINDOW flag to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
            subprocess.Popen(
                [self.python_exe, self.main_script],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"Error activating hotkey: {e}")
    
    def start(self):
        """Start listening for hotkey."""
        print(f"Dict-to-Anki Hotkey Service")
        print(f"Hotkey: {self.hotkey_combo.replace('<', '').replace('>', '').replace('+', ' + ').upper()}")
        print("Press the hotkey after selecting text to send to Anki")
        print("Press Ctrl+C to stop the service\n")
        
        self.running = True
        
        # Create hotkey
        hotkey = HotKey(
            HotKey.parse(self.hotkey_combo),
            self.on_activate
        )
        
        # Start keyboard listener
        with keyboard.Listener(
            on_press=hotkey.press,
            on_release=hotkey.release
        ) as self.listener:
            try:
                self.listener.join()
            except KeyboardInterrupt:
                print("\nService stopped by user")
                self.stop()
    
    def stop(self):
        """Stop listening for hotkey."""
        self.running = False
        if self.listener:
            self.listener.stop()


def is_already_running():
    """Check if service is already running."""
    import psutil
    
    current_pid = os.getpid()
    script_name = os.path.basename(__file__)
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            
            cmdline = proc.info.get('cmdline', [])
            if cmdline and script_name in ' '.join(cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return False


def show_notification(title, message, timeout=3):
    """Show Windows notification."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=timeout
        )
    except Exception as e:
        print(f"Could not show notification: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dict-to-Anki Hotkey Service')
    parser.add_argument(
        '--hotkey',
        default='<ctrl>+<alt>+d',
        help='Hotkey combination (default: <ctrl>+<alt>+d)'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background (no console window)'
    )
    
    args = parser.parse_args()
    
    # Check if already running
    if is_already_running():
        print("ERROR: Hotkey service is already running!")
        print("Use --stop to stop the existing service first.")
        sys.exit(1)
    
    # Start service
    service = HotkeyService(hotkey_combo=args.hotkey)
    
    # Show startup notification
    show_notification(
        "Dict-to-Anki",
        f"Hotkey service started\nPress {args.hotkey.replace('<', '').replace('>', '').replace('+', ' + ').upper()} on selected text"
    )
    
    try:
        service.start()
    except KeyboardInterrupt:
        print("\nService stopped")
        show_notification("Dict-to-Anki", "Hotkey service stopped")
