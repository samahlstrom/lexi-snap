"""Dict-to-Anki - Simple Desktop Application
Create Anki flashcards from selected text with a global hotkey.
"""

import os
import sys
import json
import time
import threading
import queue
import winreg
from pathlib import Path

import customtkinter as ctk
import requests
from pynput import keyboard
import pyperclip
import pystray
from PIL import Image, ImageDraw


VERSION = "1.0.0"


class SettingsManager:
    """Manage application settings."""

    def __init__(self):
        self.settings_file = Path.home() / '.dict_to_anki_settings.json'
        self.settings = self.load_settings()

    def load_settings(self):
        defaults = {
            'hotkey': 'ctrl+alt+d',
            'default_deck': None,
            'start_on_startup': False,
        }
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    defaults.update(json.load(f))
            except:
                pass
        return defaults

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()


class DictToAnkiApp:
    """Main application."""

    COLORS = {
        'bg': '#1a1a1a',
        'card': '#2a2a2a',
        'primary': '#ec4899',
        'primary_hover': '#db2777',
        'text': '#ffffff',
        'text_secondary': '#9ca3af',
        'border': '#404040',
        'input': '#1f1f1f'
    }

    STARTUP_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    STARTUP_APP_NAME = "DictToAnki"

    def __init__(self):
        self.settings_manager = SettingsManager()
        self.anki_url = "http://localhost:8765"
        self.root = None
        self.gui_queue = queue.Queue()
        self.hotkey_listener = None
        self.recording_hotkey = False
        self.recorded_keys = set()
        self.currently_pressed = set()
        self.hotkey_button = None
        self.hotkey_record_listener = None
        self.tray_icon = None
        self.quitting = False
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def get_app_path(self):
        """Get the appropriate path for startup - exe or script."""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe - add --minimized flag for startup
            return f'"{sys.executable}" --minimized'
        else:
            # Running as script - use pythonw to avoid console window
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            # Use pythonw if available to avoid console
            pythonw = python_exe.replace('python.exe', 'pythonw.exe')
            if os.path.exists(pythonw):
                return f'"{pythonw}" "{script_path}" --minimized'
            return f'"{python_exe}" "{script_path}" --minimized'

    def create_tray_icon_image(self):
        """Create a simple icon for the system tray."""
        # Create a simple pink/magenta icon
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Draw a filled circle with the primary color
        draw.ellipse([4, 4, size-4, size-4], fill='#ec4899')
        # Draw a letter 'D' in white
        draw.text((size//2 - 8, size//2 - 12), "D", fill='white')
        return image

    def setup_tray_icon(self):
        """Setup the system tray icon."""
        def show_window(icon, item):
            self.gui_queue.put(('show_window', None, None))
        
        def quit_app(icon, item):
            self.gui_queue.put(('quit_app', None, None))
        
        menu = pystray.Menu(
            pystray.MenuItem("Show Settings", show_window, default=True),
            pystray.MenuItem("Quit", quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "DictToAnki",
            self.create_tray_icon_image(),
            "Dict-to-Anki",
            menu
        )
        
        # Run tray icon in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def quit_application(self):
        """Properly quit the application."""
        self.quitting = True
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        sys.exit(0)

    def is_startup_enabled(self):
        """Check if app is set to start on Windows startup."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.STARTUP_REG_KEY, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, self.STARTUP_APP_NAME)
                return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def set_startup_enabled(self, enabled):
        """Enable or disable starting on Windows startup."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.STARTUP_REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    app_path = self.get_app_path()
                    winreg.SetValueEx(key, self.STARTUP_APP_NAME, 0, winreg.REG_SZ, app_path)
                else:
                    try:
                        winreg.DeleteValue(key, self.STARTUP_APP_NAME)
                    except FileNotFoundError:
                        pass
            self.settings_manager.set('start_on_startup', enabled)
            return True
        except Exception as e:
            print(f"Failed to update startup setting: {e}")
            return False

    def setup_hotkey(self):
        """Setup global hotkey using pynput."""
        # Stop existing listener if any
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None
        
        hotkey_str = self.settings_manager.get('hotkey', 'ctrl+alt+d')
        
        # Convert to pynput format
        parts = hotkey_str.lower().split('+')
        pynput_parts = []
        modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
        for part in parts:
            part = part.strip()
            if part in modifiers:
                pynput_parts.append(f'<{part}>')
            else:
                pynput_parts.append(part)
        pynput_hotkey = '+'.join(pynput_parts)
        
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({
                pynput_hotkey: self.on_hotkey_pressed
            })
            self.hotkey_listener.start()
            print(f"Hotkey registered: {pynput_hotkey}")
        except Exception as e:
            print(f"Failed to setup hotkey: {e}")

    def start_hotkey_recording(self):
        """Start recording a new hotkey combination."""
        if self.recording_hotkey:
            return
        
        self.recording_hotkey = True
        self.recorded_keys = set()
        self.currently_pressed = set()
        self.first_key_time = None
        
        if self.hotkey_button:
            self.hotkey_button.configure(text="Press keys...", fg_color="#ef4444")
        
        # Stop the main hotkey listener while recording
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None
        
        # Start a listener to capture key presses
        def on_press(key):
            if not self.recording_hotkey:
                return False
            
            key_name = self._get_key_name(key)
            if key_name:
                # Record when first key is pressed
                if self.first_key_time is None:
                    self.first_key_time = time.time()
                
                self.recorded_keys.add(key_name)
                self.currently_pressed.add(key_name)
                print(f"Key pressed: {key_name}, recorded: {self.recorded_keys}")
                # Update button to show current combo
                self._update_recording_display()
        
        def on_release(key):
            if not self.recording_hotkey:
                return False
            
            key_name = self._get_key_name(key)
            if key_name:
                self.currently_pressed.discard(key_name)
                print(f"Key released: {key_name}, still pressed: {self.currently_pressed}")
            
            # Only finalize if:
            # 1. First key was pressed (recording actually started)
            # 2. At least 500ms since first key press
            # 3. All keys are now released
            # 4. We have at least 2 keys recorded
            if self.first_key_time is None:
                return  # No keys pressed yet, ignore
            
            elapsed = time.time() - self.first_key_time
            
            if len(self.currently_pressed) == 0 and len(self.recorded_keys) >= 2 and elapsed > 0.5:
                # Check we have at least one modifier and one regular key
                modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
                has_modifier = any(k in modifiers for k in self.recorded_keys)
                has_regular = any(k not in modifiers for k in self.recorded_keys)
                
                if has_modifier and has_regular:
                    print(f"Finalizing hotkey: {self.recorded_keys}")
                    self.gui_queue.put(('finalize_hotkey', None, None))
                    return False  # Stop listener
        
        # Start listener immediately in a thread
        self.hotkey_record_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_record_listener.start()
        print("Hotkey recording started - press your key combination")

    def _update_recording_display(self):
        """Update the button to show currently pressed keys."""
        if self.hotkey_button and self.recorded_keys:
            modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
            mod_keys = sorted([k for k in self.recorded_keys if k in modifiers])
            other_keys = sorted([k for k in self.recorded_keys if k not in modifiers])
            display = '+'.join(mod_keys + other_keys).upper()
            self.gui_queue.put(('update_hotkey_button', display, None))

    def _get_key_name(self, key):
        """Convert pynput key to readable name."""
        try:
            # First check if it's a special key (has a name attribute)
            if hasattr(key, 'name') and key.name:
                name = key.name.lower()
                # Map common key names
                name_map = {
                    'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
                    'alt_l': 'alt', 'alt_r': 'alt', 'alt_gr': 'alt',
                    'shift_l': 'shift', 'shift_r': 'shift',
                    'cmd': 'win', 'cmd_l': 'win', 'cmd_r': 'win',
                }
                return name_map.get(name, name)
            
            # Then check for character keys
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            # For keys pressed with modifiers, try to get the vk (virtual key code)
            if hasattr(key, 'vk') and key.vk:
                vk = key.vk
                # A-Z keys are VK codes 65-90
                if 65 <= vk <= 90:
                    return chr(vk).lower()
                # 0-9 keys are VK codes 48-57
                if 48 <= vk <= 57:
                    return chr(vk)
                # F1-F12 are VK codes 112-123
                if 112 <= vk <= 123:
                    return f'f{vk - 111}'
        except Exception as e:
            print(f"Key detection error: {e}")
        return None

    def finalize_hotkey_recording(self):
        """Finalize the recorded hotkey."""
        if not self.recording_hotkey:
            return
            
        self.recording_hotkey = False
        
        if self.hotkey_record_listener:
            try:
                self.hotkey_record_listener.stop()
            except:
                pass
            self.hotkey_record_listener = None
        
        valid_hotkey = False
        if len(self.recorded_keys) >= 2:
            # Sort keys: modifiers first, then regular keys
            modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
            mod_keys = sorted([k for k in self.recorded_keys if k in modifiers])
            other_keys = sorted([k for k in self.recorded_keys if k not in modifiers])
            
            if mod_keys and other_keys:
                hotkey_str = '+'.join(mod_keys + other_keys)
                self.settings_manager.set('hotkey', hotkey_str)
                valid_hotkey = True
                
                print(f"New hotkey saved: {hotkey_str}")
                
                if self.hotkey_button:
                    self.hotkey_button.configure(
                        text=hotkey_str.upper(),
                        fg_color=self.COLORS['input']
                    )
                
                # Update the subtitle label
                if hasattr(self, 'hotkey_label') and self.hotkey_label:
                    self.hotkey_label.configure(text=f"Press {hotkey_str.upper()} to capture selected text")
        
        if not valid_hotkey:
            # Reset button to show current hotkey
            current = self.settings_manager.get('hotkey', 'ctrl+alt+d')
            if self.hotkey_button:
                self.hotkey_button.configure(
                    text=current.upper(),
                    fg_color=self.COLORS['input']
                )
        
        # Clear recorded keys
        self.recorded_keys = set()
        self.currently_pressed = set()
        
        # Restart the main hotkey listener
        self.setup_hotkey()

    def on_hotkey_pressed(self):
        """Handle hotkey press - runs in keyboard's thread."""
        print(">>> HOTKEY DETECTED <<<", flush=True)
        # Do the clipboard/definition work in a thread
        threading.Thread(target=self._process_hotkey, daemon=True).start()

    def _process_hotkey(self):
        """Process the hotkey in a background thread, then queue GUI work."""
        try:
            print("1. Waiting for modifier keys to be released...", flush=True)
            time.sleep(0.15)  # Let user release Ctrl+Alt+D
            
            print("2. Clearing clipboard...", flush=True)
            pyperclip.copy("")
            
            print("3. Sending Ctrl+C via pynput...", flush=True)
            kb = keyboard.Controller()
            # Release any held modifiers first
            for key in [keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.shift]:
                try:
                    kb.release(key)
                except:
                    pass
            time.sleep(0.05)
            # Now send Ctrl+C
            with kb.pressed(keyboard.Key.ctrl):
                kb.tap('c')
            
            print("4. Waiting for copy...", flush=True)
            time.sleep(0.2)
            
            print("5. Getting clipboard...", flush=True)
            text = pyperclip.paste().strip()
            print(f"6. Got text: '{text[:30] if text else 'EMPTY'}'", flush=True)

            if not text:
                print("7. No text, showing popup...", flush=True)
                self.gui_queue.put(('popup', "No text selected", "Select some text first, then press the hotkey."))
                return

            definition = self.get_definition(text)
            default_deck = self.settings_manager.get('default_deck')
            
            if default_deck and default_deck != "None (Ask every time)":
                if self.add_to_anki(default_deck, text, definition):
                    self.gui_queue.put(('popup', "Success", f"Added '{text}' to {default_deck}"))
                else:
                    self.gui_queue.put(('popup', "Error", "Failed to add card. Is Anki running with AnkiConnect?"))
            else:
                # Queue deck selector to main thread
                self.gui_queue.put(('deck_selector', text, definition))

        except Exception as e:
            self.gui_queue.put(('popup', "Error", str(e)))

    def process_gui_queue(self):
        """Check the queue and process GUI operations in main thread."""
        try:
            while True:
                item = self.gui_queue.get_nowait()
                if item[0] == 'popup':
                    self._show_popup(item[1], item[2])
                elif item[0] == 'deck_selector':
                    self._show_deck_selector(item[1], item[2])
                elif item[0] == 'finalize_hotkey':
                    self.finalize_hotkey_recording()
                elif item[0] == 'show_window':
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                elif item[0] == 'quit_app':
                    self.quit_application()
                elif item[0] == 'update_hotkey_button':
                    if self.hotkey_button:
                        self.hotkey_button.configure(text=item[1], fg_color="#ef4444")
        except queue.Empty:
            pass
        
        # Schedule next check if not quitting
        if not self.quitting and self.root:
            self.root.after(100, self.process_gui_queue)

    def get_definition(self, word):
        """Get dictionary definition."""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()[0]
                return data['meanings'][0]['definitions'][0]['definition']
        except:
            pass
        return "No definition found"

    def get_anki_decks(self):
        """Get list of Anki decks."""
        try:
            response = requests.post(
                self.anki_url,
                json={'action': 'deckNames', 'version': 6},
                timeout=2
            )
            if response.status_code == 200:
                return response.json().get('result', [])
        except:
            pass
        return []

    def add_to_anki(self, deck, word, definition):
        """Add card to Anki."""
        try:
            note = {
                'deckName': deck,
                'modelName': 'Basic',
                'fields': {'Front': word, 'Back': definition},
                'tags': ['dict-to-anki']
            }
            response = requests.post(
                self.anki_url,
                json={'action': 'addNote', 'version': 6, 'params': {'note': note}},
                timeout=2
            )
            return response.status_code == 200 and response.json().get('error') is None
        except:
            return False

    def _show_popup(self, title, message):
        """Show a popup - must be called from main thread."""
        popup = ctk.CTkToplevel(self.root)
        popup.title(title)
        popup.geometry("400x150")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        popup.focus_force()
        
        # Center
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 75
        popup.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(popup, text=message, wraplength=360).pack(pady=30, padx=20)
        ctk.CTkButton(popup, text="OK", command=popup.destroy, 
                     fg_color=self.COLORS['primary']).pack(pady=10)
        
        popup.after(5000, popup.destroy)

    def _show_deck_selector(self, word, definition):
        """Show deck selector - must be called from main thread."""
        decks = self.get_anki_decks()
        if not decks:
            self._show_popup("Error", "Anki not running or no decks found")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add to Anki")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        dialog.focus_force()

        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        container = ctk.CTkFrame(dialog, fg_color=self.COLORS['card'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Add to Anki", font=("Segoe UI", 18, "bold")).pack(pady=(10, 20))

        ctk.CTkLabel(container, text="WORD", font=("Segoe UI", 10),
                    text_color=self.COLORS['text_secondary']).pack(anchor="w", padx=20)
        ctk.CTkLabel(container, text=word, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(2, 15))

        ctk.CTkLabel(container, text="DEFINITION", font=("Segoe UI", 10),
                    text_color=self.COLORS['text_secondary']).pack(anchor="w", padx=20)
        ctk.CTkLabel(container, text=definition, font=("Segoe UI", 11),
                    wraplength=440, justify="left").pack(anchor="w", padx=20, pady=(2, 15))

        ctk.CTkLabel(container, text="SELECT DECK", font=("Segoe UI", 10),
                    text_color=self.COLORS['text_secondary']).pack(anchor="w", padx=20, pady=(10, 5))

        deck_var = ctk.StringVar(value=decks[0])
        ctk.CTkComboBox(container, values=decks, variable=deck_var, width=440,
                       fg_color=self.COLORS['input']).pack(padx=20, pady=(0, 20))

        button_frame = ctk.CTkFrame(container, fg_color=self.COLORS['card'])
        button_frame.pack(fill="x", padx=20, pady=(0, 10))

        def add_card():
            deck = deck_var.get()
            dialog.destroy()
            if self.add_to_anki(deck, word, definition):
                self._show_popup("Success", f"Added '{word}' to {deck}")
            else:
                self._show_popup("Error", "Failed to add card")

        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy,
                     fg_color=self.COLORS['input'], width=120).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Add Card", command=add_card,
                     fg_color=self.COLORS['primary'], width=120).pack(side="right")

    def create_main_window(self):
        """Create the main settings window."""
        self.root = ctk.CTk()
        self.root.title("Dict-to-Anki")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        # Center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 250
        y = (self.root.winfo_screenheight() // 2) - 210
        self.root.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(self.root, text="Dict-to-Anki", font=("Segoe UI", 24, "bold"),
                    text_color=self.COLORS['primary']).pack(pady=(25, 5))
        
        self.hotkey_label = ctk.CTkLabel(
            self.root, 
            text=f"Press {self.settings_manager.get('hotkey', 'ctrl+alt+d').upper()} to capture selected text",
            text_color=self.COLORS['text_secondary']
        )
        self.hotkey_label.pack(pady=(0, 15))

        # Settings container
        settings_frame = ctk.CTkFrame(self.root, fg_color=self.COLORS['card'])
        settings_frame.pack(fill="x", padx=30, pady=10)

        # Hotkey setting
        hotkey_frame = ctk.CTkFrame(settings_frame, fg_color=self.COLORS['card'])
        hotkey_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(hotkey_frame, text="Hotkey:", font=("Segoe UI", 12)).pack(side="left")
        
        current_hotkey = self.settings_manager.get('hotkey', 'ctrl+alt+d')
        self.hotkey_button = ctk.CTkButton(
            hotkey_frame, 
            text=current_hotkey.upper(),
            command=self.start_hotkey_recording,
            fg_color=self.COLORS['input'],
            hover_color=self.COLORS['border'],
            width=180
        )
        self.hotkey_button.pack(side="right")

        ctk.CTkLabel(
            settings_frame, 
            text="Click the button and press your desired key combination",
            font=("Segoe UI", 10),
            text_color=self.COLORS['text_secondary']
        ).pack(pady=(0, 10))

        # Default deck setting
        deck_frame = ctk.CTkFrame(settings_frame, fg_color=self.COLORS['card'])
        deck_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(deck_frame, text="Default Deck:", font=("Segoe UI", 12)).pack(side="left")

        decks = ["None (Ask every time)"] + self.get_anki_decks()
        current_deck = self.settings_manager.get('default_deck') or "None (Ask every time)"

        def update_deck(choice):
            self.settings_manager.set('default_deck', None if choice == "None (Ask every time)" else choice)

        deck_dropdown = ctk.CTkComboBox(deck_frame, values=decks, command=update_deck, width=180)
        deck_dropdown.set(current_deck)
        deck_dropdown.pack(side="right")

        # Startup setting
        startup_frame = ctk.CTkFrame(settings_frame, fg_color=self.COLORS['card'])
        startup_frame.pack(fill="x", padx=20, pady=(10, 15))

        ctk.CTkLabel(startup_frame, text="Start on Windows startup:", font=("Segoe UI", 12)).pack(side="left")

        startup_var = ctk.BooleanVar(value=self.is_startup_enabled())
        
        def toggle_startup():
            enabled = startup_var.get()
            if not self.set_startup_enabled(enabled):
                # Revert if failed
                startup_var.set(not enabled)
                self._show_popup("Error", "Failed to update startup setting")

        startup_checkbox = ctk.CTkCheckBox(
            startup_frame, 
            text="",
            variable=startup_var,
            command=toggle_startup,
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['primary_hover'],
            width=24
        )
        startup_checkbox.pack(side="right")

        # Status
        status_text = "Ready - Anki connected" if self.get_anki_decks() else "Warning - Anki not detected"
        ctk.CTkLabel(self.root, text=status_text,
                    text_color="#22c55e" if "Ready" in status_text else "#ef4444").pack(pady=15)

        # Minimize button
        ctk.CTkButton(self.root, text="Minimize (keeps running)",
                     command=self.root.withdraw, fg_color=self.COLORS['input']).pack(pady=(5, 15))

        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)

    def run(self, start_minimized=False):
        """Start the application."""
        self.setup_hotkey()
        self.create_main_window()
        self.setup_tray_icon()
        
        # Start minimized to system tray if requested (e.g., on Windows startup)
        if start_minimized:
            self.root.withdraw()
        
        # Start processing GUI queue
        self.root.after(100, self.process_gui_queue)
        
        print("Dict-to-Anki running!")
        print(f"Hotkey: {self.settings_manager.get('hotkey', 'ctrl+alt+d').upper()}")
        if start_minimized:
            print("Started minimized to system tray.")
        else:
            print("Minimize the window - it keeps running in the system tray.")
        
        self.root.mainloop()


def main():
    # Check for --minimized flag (used when starting on Windows startup)
    start_minimized = '--minimized' in sys.argv
    
    # Use Windows mutex for reliable single-instance detection
    import ctypes
    from ctypes import wintypes
    
    kernel32 = ctypes.windll.kernel32
    mutex_name = "DictToAnki_SingleInstance_Mutex"
    
    # Try to create a named mutex
    handle = kernel32.CreateMutexW(None, True, mutex_name)
    last_error = kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        # Another instance is already running
        ctypes.windll.user32.MessageBoxW(
            0, 
            "Dict-to-Anki is already running!\n\nCheck your system tray.", 
            "Dict-to-Anki", 
            0x40  # MB_ICONINFORMATION
        )
        if handle:
            kernel32.CloseHandle(handle)
        sys.exit(0)
    
    # Keep mutex handle alive for the lifetime of the app
    # (it will be released automatically when the process exits)

    app = DictToAnkiApp()
    app.run(start_minimized=start_minimized)


if __name__ == '__main__':
    main()
