"""Dict-to-Anki - Simple Desktop App (No Admin Required)"""
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import pystray
from PIL import Image, ImageDraw
import pyperclip
import requests
import json


class DictToAnkiApp:
    """Main application - runs in system tray with optional settings window."""

    def __init__(self):
        # Anki connection
        self.anki_url = "http://localhost:8765"

        # Hotkey
        self.hotkey = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+d': self.on_hotkey_pressed
        })

        # Settings window (hidden by default)
        self.settings_window = None

        # System tray icon
        self.tray_icon = None

    def create_icon_image(self):
        """Create a simple tray icon."""
        img = Image.new('RGB', (64, 64), color='#4CAF50')
        draw = ImageDraw.Draw(img)
        draw.text((10, 20), 'D→A', fill='white')
        return img

    def on_hotkey_pressed(self):
        """Handle Ctrl+Alt+D - capture selection and create card."""
        try:
            # Get selected text
            old_clipboard = pyperclip.paste()

            # Copy selection
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')
            import time
            time.sleep(0.1)

            text = pyperclip.paste()

            # Restore clipboard
            pyperclip.copy(old_clipboard)

            if not text or text == old_clipboard:
                self.show_notification("No text selected")
                return

            # Get definition
            definition = self.get_definition(text)

            # Show deck selection
            self.show_deck_selector(text, definition)

        except Exception as e:
            self.show_notification(f"Error: {e}")

    def get_definition(self, word):
        """Get dictionary definition."""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()[0]
                meaning = data['meanings'][0]['definitions'][0]['definition']
                return meaning
            return "No definition found"
        except:
            return "No definition found"

    def show_deck_selector(self, word, definition):
        """Show simple deck selector dialog."""
        # Get Anki decks
        decks = self.get_anki_decks()

        if not decks:
            self.show_notification("Anki not running or no decks found")
            return

        # Create selection dialog
        dialog = tk.Tk()
        dialog.title("Add to Anki")
        dialog.geometry("400x300")

        tk.Label(dialog, text=f"Word: {word}", font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Label(dialog, text=f"Definition: {definition}", wraplength=350).pack(pady=5)

        tk.Label(dialog, text="Select deck:").pack(pady=10)

        deck_var = tk.StringVar(value=decks[0] if decks else "")
        deck_dropdown = ttk.Combobox(dialog, textvariable=deck_var, values=decks, state='readonly')
        deck_dropdown.pack(pady=5)

        def add_card():
            deck = deck_var.get()
            if self.add_to_anki(deck, word, definition):
                self.show_notification(f"Added '{word}' to {deck}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add card to Anki")

        tk.Button(dialog, text="Add Card", command=add_card, bg='#4CAF50', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

        dialog.mainloop()

    def get_anki_decks(self):
        """Get list of Anki decks."""
        try:
            response = requests.post(
                self.anki_url,
                json={'action': 'deckNames', 'version': 6},
                timeout=2
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('result', [])
        except:
            pass
        return []

    def add_to_anki(self, deck, word, definition):
        """Add card to Anki."""
        try:
            note = {
                'deckName': deck,
                'modelName': 'Basic',
                'fields': {
                    'Front': word,
                    'Back': definition
                },
                'tags': ['dict-to-anki']
            }

            response = requests.post(
                self.anki_url,
                json={'action': 'addNote', 'version': 6, 'params': {'note': note}},
                timeout=2
            )

            return response.status_code == 200
        except:
            return False

    def show_notification(self, message):
        """Show system notification."""
        if self.tray_icon:
            self.tray_icon.notify(message, "Dict-to-Anki")

    def show_settings(self):
        """Show settings window."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Tk()
        self.settings_window.title("Dict-to-Anki Settings")
        self.settings_window.geometry("500x400")

        # Header
        header = tk.Frame(self.settings_window, bg='#4CAF50', height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Dict-to-Anki", font=('Arial', 18, 'bold'),
                bg='#4CAF50', fg='white').pack(pady=15)

        # Content
        content = tk.Frame(self.settings_window, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text="Status", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0,10))

        # Check Anki connection
        decks = self.get_anki_decks()
        if decks:
            status_text = f"✓ Connected to Anki\n✓ {len(decks)} decks available\n✓ Hotkey: Ctrl+Alt+D"
            color = 'green'
        else:
            status_text = "✗ Anki not running\n  Please start Anki with AnkiConnect add-on"
            color = 'red'

        tk.Label(content, text=status_text, font=('Arial', 10), fg=color, justify='left').pack(anchor='w')

        tk.Label(content, text="\nHow to use:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(20,10))
        instructions = """1. Make sure Anki is running
2. Highlight any text in any application
3. Press Ctrl+Alt+D
4. Select a deck
5. Done!"""
        tk.Label(content, text=instructions, font=('Arial', 10), justify='left').pack(anchor='w')

        # Quit button
        tk.Button(content, text="Quit App", command=self.quit_app,
                 bg='#f44336', fg='white').pack(side=tk.BOTTOM, pady=20)

        # Handle close button
        self.settings_window.protocol("WM_DELETE_WINDOW", self.hide_settings)

        self.settings_window.mainloop()

    def hide_settings(self):
        """Hide settings window instead of closing."""
        if self.settings_window:
            self.settings_window.withdraw()

    def quit_app(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit Dict-to-Anki?"):
            self.hotkey.stop()
            if self.tray_icon:
                self.tray_icon.stop()
            if self.settings_window:
                self.settings_window.destroy()
            sys.exit(0)

    def run(self):
        """Start the application."""
        # Start hotkey listener
        self.hotkey.start()

        # Create tray menu
        menu = pystray.Menu(
            pystray.MenuItem("Settings", lambda: threading.Thread(target=self.show_settings, daemon=True).start(), default=True),
            pystray.MenuItem("Quit", self.quit_app)
        )

        # Create tray icon
        self.tray_icon = pystray.Icon(
            "dict-to-anki",
            self.create_icon_image(),
            "Dict-to-Anki (Ctrl+Alt+D)",
            menu
        )

        # Show notification
        self.show_notification("Dict-to-Anki started! Press Ctrl+Alt+D on any selected text")

        # Run (this blocks)
        self.tray_icon.run()


if __name__ == '__main__':
    # Check if already running
    import psutil
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and 'dict_to_anki_app.py' in ' '.join(proc.info.get('cmdline', [])):
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, "Dict-to-Anki is already running!", "Dict-to-Anki", 0x30)
                sys.exit(0)
        except:
            pass

    # Start app
    app = DictToAnkiApp()
    app.run()
