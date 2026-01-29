"""Lexi Snap - Simple Desktop Application
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
from datetime import datetime

import customtkinter as ctk
import requests
from pynput import keyboard
import pyperclip
import pystray
from PIL import Image, ImageDraw, ImageFont


VERSION = "1.1.0"


class SettingsManager:
    """Manage application settings."""

    def __init__(self):
        self.settings_file = Path.home() / '.lexi_snap_settings.json'
        self.settings = self.load_settings()

    def load_settings(self):
        defaults = {
            'hotkey': 'ctrl+alt+d',
            'default_deck': None,
            'start_on_startup': False,
            'notification_badge_enabled': True,
            'notification_toast_enabled': False,
            'card_history': [],  # List of {word, definition, timestamp}
            'cached_decks': [],  # Cached Anki deck list for faster startup
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

    def add_to_history(self, word, definition):
        """Add a card to history, keeping only the 10 most recent."""
        history = self.settings.get('card_history', [])
        history.insert(0, {
            'word': word,
            'definition': definition,
            'timestamp': datetime.now().isoformat()
        })
        # Keep only 10 most recent
        self.settings['card_history'] = history[:10]
        self.save_settings()


class LexiSnapApp:
    """Main application."""

    COLORS = {
        'bg': '#1a1a1a',
        'sidebar': '#141414',
        'card': '#2a2a2a',
        'primary': '#154785',        # Navy blue (main)
        'primary_hover': '#1a5299',  # Lighter blue on hover
        'accent': '#e84057',         # Pinkish red (notifications)
        'text': '#ffffff',
        'text_secondary': '#9ca3af',
        'border': '#404040',
        'input': '#1f1f1f',
        'success': '#22c55e',
        'error': '#ef4444',
    }

    STARTUP_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    STARTUP_APP_NAME = "lexi-snap"

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
        
        # Session card counter for badge
        self.session_card_count = 0
        
        # Anki status label reference
        self.anki_status_label = None
        
        # Deck dropdown reference for async updates
        self.deck_dropdown = None
        self.deck_dropdown_values = []
        
        # Anki connection monitoring
        self._anki_connected = False
        self._anki_monitor_running = False
        
        # Current active tab
        self.current_tab = "general"
        self.tab_frames = {}
        self.tab_buttons = {}
        self.content_frame = None
        
        # Icon paths - ICO for tray, PNG for display
        self.icon_path = self._get_icon_path(prefer_ico=False)  # PNG for UI display
        self.icon_path_ico = self._get_icon_path(prefer_ico=True)  # ICO for system tray
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _get_icon_path(self, prefer_ico=False):
        """Get the path to the icon file."""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Check for ICO first if preferred (better for Windows system tray)
        if prefer_ico:
            ico_path = os.path.join(base_path, 'assets', 'icon.ico')
            if os.path.exists(ico_path):
                return ico_path
        
        # Check for PNG
        png_path = os.path.join(base_path, 'assets', 'icon.png')
        if os.path.exists(png_path):
            return png_path
        
        # Fallback to ICO if PNG not found
        ico_path = os.path.join(base_path, 'assets', 'icon.ico')
        if os.path.exists(ico_path):
            return ico_path
            
        return None

    def get_app_path(self):
        """Get the appropriate path for startup - exe or script."""
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}" --minimized'
        else:
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            pythonw = python_exe.replace('python.exe', 'pythonw.exe')
            if os.path.exists(pythonw):
                return f'"{pythonw}" "{script_path}" --minimized'
            return f'"{python_exe}" "{script_path}" --minimized'

    def create_tray_icon_image(self, with_badge=False):
        """Create icon for the system tray, optionally with badge counter."""
        size = 64
        
        # Try to load custom icon - prefer ICO for system tray
        icon_to_load = self.icon_path_ico or self.icon_path
        if icon_to_load and os.path.exists(icon_to_load):
            try:
                image = Image.open(icon_to_load).convert('RGBA')
                image = image.resize((size, size), Image.Resampling.LANCZOS)
            except:
                # Fallback to generated icon
                image = self._create_fallback_icon(size)
        else:
            image = self._create_fallback_icon(size)
        
        # Add badge if enabled and there are cards added
        if with_badge and self.session_card_count > 0:
            image = self._add_badge_to_icon(image, self.session_card_count)
        
        return image

    def _create_fallback_icon(self, size):
        """Create a simple fallback icon."""
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Draw a filled circle with the primary color
        draw.ellipse([4, 4, size-4, size-4], fill='#154785')
        # Draw a letter 'L' in white
        draw.text((size//2 - 8, size//2 - 12), "L", fill='white')
        return image

    def _add_badge_to_icon(self, image, count):
        """Add a notification badge with count to the icon."""
        draw = ImageDraw.Draw(image)
        size = image.size[0]
        
        # Badge size and position (top-right corner)
        badge_size = 24
        badge_x = size - badge_size - 2
        badge_y = 2
        
        # Draw pinkish-red badge circle
        draw.ellipse(
            [badge_x, badge_y, badge_x + badge_size, badge_y + badge_size],
            fill='#e84057'
        )
        
        # Draw white number
        count_text = str(count) if count < 100 else "99+"
        # Center the text in the badge
        text_x = badge_x + badge_size // 2
        text_y = badge_y + badge_size // 2
        
        # Use a simple approach for text centering
        draw.text(
            (text_x - len(count_text) * 3, text_y - 6),
            count_text,
            fill='white'
        )
        
        return image

    def update_tray_icon(self):
        """Update the tray icon with or without badge."""
        if self.tray_icon:
            badge_enabled = self.settings_manager.get('notification_badge_enabled', True)
            new_icon = self.create_tray_icon_image(with_badge=badge_enabled)
            self.tray_icon.icon = new_icon

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
        
        badge_enabled = self.settings_manager.get('notification_badge_enabled', True)
        self.tray_icon = pystray.Icon(
            "lexi-snap",
            self.create_tray_icon_image(with_badge=badge_enabled),
            "Lexi Snap",
            menu
        )
        
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def quit_application(self):
        """Properly quit the application."""
        self.quitting = True
        self._stop_anki_monitor()
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
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None
        
        hotkey_str = self.settings_manager.get('hotkey', '')
        if not hotkey_str:
            print("No hotkey configured")
            return
        
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
            self.hotkey_button.configure(text="Press keys...", fg_color=self.COLORS['accent'])
        
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None
        
        def on_press(key):
            if not self.recording_hotkey:
                return False
            
            key_name = self._get_key_name(key)
            if key_name:
                if self.first_key_time is None:
                    self.first_key_time = time.time()
                
                self.recorded_keys.add(key_name)
                self.currently_pressed.add(key_name)
                self._update_recording_display()
        
        def on_release(key):
            if not self.recording_hotkey:
                return False
            
            key_name = self._get_key_name(key)
            if key_name:
                self.currently_pressed.discard(key_name)
            
            if self.first_key_time is None:
                return
            
            elapsed = time.time() - self.first_key_time
            
            if len(self.currently_pressed) == 0 and len(self.recorded_keys) >= 2 and elapsed > 0.5:
                modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
                has_modifier = any(k in modifiers for k in self.recorded_keys)
                has_regular = any(k not in modifiers for k in self.recorded_keys)
                
                if has_modifier and has_regular:
                    self.gui_queue.put(('finalize_hotkey', None, None))
                    return False
        
        self.hotkey_record_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_record_listener.start()

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
            if hasattr(key, 'name') and key.name:
                name = key.name.lower()
                name_map = {
                    'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
                    'alt_l': 'alt', 'alt_r': 'alt', 'alt_gr': 'alt',
                    'shift_l': 'shift', 'shift_r': 'shift',
                    'cmd': 'win', 'cmd_l': 'win', 'cmd_r': 'win',
                }
                return name_map.get(name, name)
            
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            if hasattr(key, 'vk') and key.vk:
                vk = key.vk
                if 65 <= vk <= 90:
                    return chr(vk).lower()
                if 48 <= vk <= 57:
                    return chr(vk)
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
            modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
            mod_keys = sorted([k for k in self.recorded_keys if k in modifiers])
            other_keys = sorted([k for k in self.recorded_keys if k not in modifiers])
            
            if mod_keys and other_keys:
                hotkey_str = '+'.join(mod_keys + other_keys)
                self.settings_manager.set('hotkey', hotkey_str)
                valid_hotkey = True
                
                if self.hotkey_button:
                    self.hotkey_button.configure(
                        text=hotkey_str.upper(),
                        fg_color=self.COLORS['input']
                    )
        
        if not valid_hotkey:
            current = self.settings_manager.get('hotkey', '')
            if self.hotkey_button:
                self.hotkey_button.configure(
                    text=current.upper() if current else "Click to set",
                    fg_color=self.COLORS['input']
                )
        
        self.recorded_keys = set()
        self.currently_pressed = set()
        self.setup_hotkey()

    def reset_hotkey(self):
        """Reset the hotkey to blank (disabled)."""
        self.settings_manager.set('hotkey', '')
        if self.hotkey_button:
            self.hotkey_button.configure(text="Click to set", fg_color=self.COLORS['input'])
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None

    def on_hotkey_pressed(self):
        """Handle hotkey press - runs in keyboard's thread."""
        print(">>> HOTKEY DETECTED <<<", flush=True)
        threading.Thread(target=self._process_hotkey, daemon=True).start()

    def _process_hotkey(self):
        """Process the hotkey in a background thread, then queue GUI work."""
        try:
            time.sleep(0.15)
            pyperclip.copy("")
            
            kb = keyboard.Controller()
            for key in [keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.shift]:
                try:
                    kb.release(key)
                except:
                    pass
            time.sleep(0.05)
            with kb.pressed(keyboard.Key.ctrl):
                kb.tap('c')
            
            time.sleep(0.2)
            text = pyperclip.paste().strip()

            if not text:
                self.gui_queue.put(('toast', "No text selected", None))
                return

            definition = self.get_definition(text)
            default_deck = self.settings_manager.get('default_deck')
            
            if default_deck and default_deck != "None (Ask every time)":
                if self.add_to_anki(default_deck, text, definition):
                    # Add to history
                    self.settings_manager.add_to_history(text, definition)
                    # Increment session counter
                    self.session_card_count += 1
                    # Update tray icon badge
                    self.update_tray_icon()
                    # Show toast notification if enabled
                    if self.settings_manager.get('notification_toast_enabled', False):
                        self.gui_queue.put(('toast', f"Added: {text}", None))
                    # Refresh history tab if visible
                    self.gui_queue.put(('refresh_history', None, None))
                else:
                    self.gui_queue.put(('toast', "Failed to add card", None))
            else:
                self.gui_queue.put(('deck_selector', text, definition))

        except Exception as e:
            self.gui_queue.put(('toast', f"Error: {str(e)}", None))

    def process_gui_queue(self):
        """Check the queue and process GUI operations in main thread."""
        try:
            while True:
                item = self.gui_queue.get_nowait()
                if item[0] == 'toast':
                    self._show_toast(item[1])
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
                        self.hotkey_button.configure(text=item[1], fg_color=self.COLORS['accent'])
                elif item[0] == 'refresh_history':
                    if self.current_tab == 'history':
                        self._refresh_history_content()
                elif item[0] == 'update_anki_status':
                    self._update_anki_status()
                elif item[0] == 'set_anki_status':
                    self._set_anki_status_label(item[1])
                elif item[0] == 'update_deck_dropdown':
                    self._update_deck_dropdown(item[1])
        except queue.Empty:
            pass
        
        if not self.quitting and self.root:
            self.root.after(100, self.process_gui_queue)

    def _get_work_area(self):
        """Get the work area (screen area excluding taskbar) using Windows API."""
        import ctypes
        from ctypes import wintypes
        
        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)
            ]
        
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA
        return rect.left, rect.top, rect.right, rect.bottom

    def _show_toast(self, message):
        """Show a semi-transparent toast notification at bottom center of current monitor."""
        if not self.settings_manager.get('notification_toast_enabled', False):
            return
            
        toast = ctk.CTkToplevel(self.root)
        toast.title("")
        toast.overrideredirect(True)  # Remove window decorations
        toast.attributes('-topmost', True)
        toast.attributes('-alpha', 0.9)  # Semi-transparent
        
        # Toast dimensions - fixed size, supports up to 2 lines
        toast_width = 280
        toast_height = 70
        
        # Padding from bottom edge
        padding = 24
        
        # Get monitor info where the mouse cursor is located
        try:
            import ctypes
            from ctypes import wintypes
            
            class POINT(ctypes.Structure):
                _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
            
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_ulong),
                    ('rcMonitor', wintypes.RECT),
                    ('rcWork', wintypes.RECT),
                    ('dwFlags', ctypes.c_ulong)
                ]
            
            # Get cursor position
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            
            # Get monitor from cursor position
            MONITOR_DEFAULTTONEAREST = 2
            hMonitor = ctypes.windll.user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)
            
            # Get monitor info
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            ctypes.windll.user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
            
            # Use work area (excludes taskbar)
            mon_left = mi.rcWork.left
            mon_top = mi.rcWork.top
            mon_right = mi.rcWork.right
            mon_bottom = mi.rcWork.bottom
            mon_width = mon_right - mon_left
            mon_height = mon_bottom - mon_top
            
            # Position at bottom center of this monitor
            x = mon_left + (mon_width - toast_width) // 2
            y = mon_bottom - toast_height - padding
            
        except Exception:
            # Fallback: use tkinter screen dimensions
            toast.update_idletasks()
            screen_width = toast.winfo_screenwidth()
            screen_height = toast.winfo_screenheight()
            x = (screen_width - toast_width) // 2
            y = screen_height - toast_height - padding
        
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        toast.update_idletasks()  # Ensure geometry is applied
        
        # Use a chroma key color to make window background transparent
        # This allows the rounded corners to show properly
        chroma_key = "#010101"  # Nearly black, unlikely to be used elsewhere
        toast.wm_attributes("-transparentcolor", chroma_key)
        
        # Outer frame fills window with the transparent color
        outer = ctk.CTkFrame(toast, fg_color=chroma_key, corner_radius=0)
        outer.pack(fill="both", expand=True)
        
        # Inner frame with rounded corners - this is the visible toast
        frame = ctk.CTkFrame(
            outer, 
            fg_color=self.COLORS['card'], 
            corner_radius=20,
            border_width=1,
            border_color=self.COLORS['border']
        )
        frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Toast text - bold, larger, with word wrap for 2 lines max
        ctk.CTkLabel(
            frame, 
            text=message, 
            font=("Segoe UI Semibold", 14),
            text_color=self.COLORS['text'],
            wraplength=240,
            justify="center"
        ).pack(expand=True, pady=12, padx=16)
        
        # Ensure window is fully rendered before starting dismiss timer
        toast.update()
        
        # Auto-dismiss after 1 second
        def safe_destroy():
            try:
                if toast.winfo_exists():
                    toast.destroy()
            except:
                pass
        
        toast.after(1000, safe_destroy)

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
                'tags': ['lexi-snap']
            }
            response = requests.post(
                self.anki_url,
                json={'action': 'addNote', 'version': 6, 'params': {'note': note}},
                timeout=2
            )
            success = response.status_code == 200 and response.json().get('error') is None
            # Update Anki status after operation
            self.gui_queue.put(('update_anki_status', None, None))
            return success
        except:
            # Update Anki status after failed operation
            self.gui_queue.put(('update_anki_status', None, None))
            return False

    def _ping_anki(self):
        """Quick check if Anki is responding (short timeout for status checks)."""
        try:
            response = requests.post(
                self.anki_url,
                json={'action': 'version', 'version': 6},
                timeout=0.3
            )
            return response.status_code == 200
        except:
            return False

    def _update_anki_status(self):
        """Update the Anki connection status label (runs check in background thread)."""
        def check_and_update():
            is_connected = self._ping_anki()
            self.gui_queue.put(('set_anki_status', is_connected, None))
        
        threading.Thread(target=check_and_update, daemon=True).start()

    def _set_anki_status_label(self, is_connected):
        """Set the Anki status label (called from GUI thread)."""
        if self.anki_status_label:
            status_text = "Anki connected" if is_connected else "Anki not detected"
            status_color = self.COLORS['success'] if is_connected else self.COLORS['error']
            self.anki_status_label.configure(text=status_text, text_color=status_color)

    def _fetch_decks_async(self):
        """Fetch Anki decks in background thread and update UI."""
        def fetch():
            decks = self.get_anki_decks()
            is_connected = bool(decks)
            self._anki_connected = is_connected
            # Cache the deck list for faster startup next time
            if decks:
                self.settings_manager.set('cached_decks', decks)
            # Update UI via queue
            self.gui_queue.put(('update_deck_dropdown', decks, None))
            self.gui_queue.put(('set_anki_status', is_connected, None))
        
        threading.Thread(target=fetch, daemon=True).start()

    def _start_anki_monitor(self):
        """Start background monitoring of Anki connection."""
        if self._anki_monitor_running:
            return
        self._anki_monitor_running = True
        
        def monitor():
            while self._anki_monitor_running and not self.quitting:
                try:
                    is_connected = self._ping_anki()
                    was_connected = self._anki_connected
                    
                    if is_connected != was_connected:
                        self._anki_connected = is_connected
                        if is_connected:
                            # Just connected - fetch full deck list
                            decks = self.get_anki_decks()
                            if decks:
                                self.settings_manager.set('cached_decks', decks)
                            self.gui_queue.put(('update_deck_dropdown', decks, None))
                        else:
                            # Just disconnected - show cached decks (grayed out via status)
                            cached = self.settings_manager.get('cached_decks', [])
                            self.gui_queue.put(('update_deck_dropdown', cached, None))
                        self.gui_queue.put(('set_anki_status', is_connected, None))
                except:
                    pass
                
                # Poll every 2 seconds
                time.sleep(2)
        
        threading.Thread(target=monitor, daemon=True).start()

    def _stop_anki_monitor(self):
        """Stop the Anki connection monitor."""
        self._anki_monitor_running = False

    def _quick_anki_check(self):
        """Quick check of Anki status using fast ping, fetch decks only if state changed."""
        def check():
            is_connected = self._ping_anki()
            was_connected = self._anki_connected
            
            if is_connected != was_connected:
                self._anki_connected = is_connected
                if is_connected:
                    # Just connected - fetch full deck list
                    decks = self.get_anki_decks()
                    if decks:
                        self.settings_manager.set('cached_decks', decks)
                    self.gui_queue.put(('update_deck_dropdown', decks, None))
                else:
                    # Just disconnected - show cached decks
                    cached = self.settings_manager.get('cached_decks', [])
                    self.gui_queue.put(('update_deck_dropdown', cached, None))
            
            self.gui_queue.put(('set_anki_status', is_connected, None))
        
        threading.Thread(target=check, daemon=True).start()

    def _update_deck_dropdown(self, decks):
        """Update the deck dropdown with fetched decks (called from GUI thread)."""
        self.deck_dropdown_values = ["None (Ask every time)"] + decks
        if self.deck_dropdown:
            current_deck = self.settings_manager.get('default_deck') or "None (Ask every time)"
            self.deck_dropdown.configure(values=self.deck_dropdown_values)
            # Restore selection if it exists in new list
            if current_deck in self.deck_dropdown_values:
                self.deck_dropdown.set(current_deck)
            else:
                self.deck_dropdown.set("None (Ask every time)")

    def _show_deck_selector(self, word, definition):
        """Show deck selector dialog."""
        decks = self.get_anki_decks()
        if not decks:
            self._show_toast("Anki not running or no decks found")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add to Anki")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        dialog.focus_force()
        
        # Set dialog icon
        if self.icon_path_ico and os.path.exists(self.icon_path_ico):
            try:
                dialog.iconbitmap(self.icon_path_ico)
            except:
                pass

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
                self.settings_manager.add_to_history(word, definition)
                self.session_card_count += 1
                self.update_tray_icon()
                if self.settings_manager.get('notification_toast_enabled', False):
                    self._show_toast(f"Added: {word}")
                self.gui_queue.put(('refresh_history', None, None))
            else:
                self._show_toast("Failed to add card")

        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy,
                     fg_color=self.COLORS['input'], width=120).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Add Card", command=add_card,
                     fg_color=self.COLORS['primary'], width=120).pack(side="right")

    # ==================== UI CREATION ====================

    def create_main_window(self):
        """Create the main settings window with sidebar navigation."""
        # Set AppUserModelID for Windows taskbar grouping and icon
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('lexi-snap.App.1.0')
        except:
            pass
        
        self.root = ctk.CTk()
        self.root.title("Lexi Snap")
        self.root.geometry("700x480")
        self.root.resizable(False, False)
        
        # Set window icon (shows in taskbar and title bar)
        if self.icon_path_ico and os.path.exists(self.icon_path_ico):
            try:
                self.root.iconbitmap(self.icon_path_ico)
            except Exception as e:
                print(f"Could not set window icon: {e}")

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 350
        y = (self.root.winfo_screenheight() // 2) - 240
        self.root.geometry(f"+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.COLORS['bg'])
        main_container.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(main_container, fg_color=self.COLORS['sidebar'], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # App icon and title in sidebar
        self._create_sidebar_header(sidebar)

        # Navigation buttons
        self._create_nav_buttons(sidebar)

        # Content area
        self.content_frame = ctk.CTkFrame(main_container, fg_color=self.COLORS['bg'])
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Create all tab frames
        self._create_general_tab()
        self._create_notifications_tab()
        self._create_history_tab()

        # Show default tab
        self.switch_tab("general")

        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)

    def _create_sidebar_header(self, sidebar):
        """Create the sidebar header with icon and app name."""
        header_frame = ctk.CTkFrame(sidebar, fg_color=self.COLORS['sidebar'])
        header_frame.pack(fill="x", padx=15, pady=(20, 30))

        # Try to load and display the icon
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                icon_img = Image.open(self.icon_path)
                icon_img = icon_img.resize((40, 40), Image.Resampling.LANCZOS)
                icon_ctk = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(40, 40))
                icon_label = ctk.CTkLabel(header_frame, image=icon_ctk, text="")
                icon_label.pack(side="left", padx=(0, 10))
            except:
                pass

        ctk.CTkLabel(
            header_frame, 
            text="Lexi Snap", 
            font=("Segoe UI", 16, "bold"),
            text_color=self.COLORS['text']
        ).pack(side="left")

    def _create_nav_buttons(self, sidebar):
        """Create navigation buttons in sidebar."""
        nav_items = [
            ("general", "General"),
            ("notifications", "Notifications"),
            ("history", "History"),
        ]

        for tab_id, label in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                font=("Segoe UI", 13),
                fg_color="transparent",
                text_color=self.COLORS['text_secondary'],
                hover_color=self.COLORS['card'],
                anchor="w",
                height=40,
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.tab_buttons[tab_id] = btn

    def switch_tab(self, tab_id):
        """Switch to a different tab."""
        # Update button styles
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color=self.COLORS['primary'],
                    text_color=self.COLORS['text']
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.COLORS['text_secondary']
                )

        # Hide all tabs, show selected
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True, padx=20, pady=20)
            else:
                frame.pack_forget()

        # Clear badge when switching to history tab
        if tab_id == "history":
            self.session_card_count = 0
            self.update_tray_icon()
            self._refresh_history_content()
        
        # Quick status check when switching to general tab
        if tab_id == "general":
            self._quick_anki_check()

        self.current_tab = tab_id

    def _create_general_tab(self):
        """Create the General settings tab."""
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['bg'])
        self.tab_frames["general"] = frame

        # Tab title
        ctk.CTkLabel(
            frame, 
            text="General Settings", 
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORS['text']
        ).pack(anchor="w", pady=(0, 20))

        # Settings card
        card = ctk.CTkFrame(frame, fg_color=self.COLORS['card'], corner_radius=10)
        card.pack(fill="x")

        # Hotkey setting
        hotkey_frame = ctk.CTkFrame(card, fg_color=self.COLORS['card'])
        hotkey_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            hotkey_frame, 
            text="Hotkey Shortcut", 
            font=("Segoe UI", 13),
            text_color=self.COLORS['text']
        ).pack(side="left")

        # Hotkey buttons container
        hotkey_btns = ctk.CTkFrame(hotkey_frame, fg_color=self.COLORS['card'])
        hotkey_btns.pack(side="right")

        # Reset button
        reset_btn = ctk.CTkButton(
            hotkey_btns,
            text="Reset",
            font=("Segoe UI", 11),
            fg_color=self.COLORS['input'],
            hover_color=self.COLORS['border'],
            width=60,
            height=32,
            command=self.reset_hotkey
        )
        reset_btn.pack(side="right", padx=(10, 0))

        # Hotkey button
        current_hotkey = self.settings_manager.get('hotkey', '')
        self.hotkey_button = ctk.CTkButton(
            hotkey_btns,
            text=current_hotkey.upper() if current_hotkey else "Click to set",
            font=("Segoe UI", 11),
            command=self.start_hotkey_recording,
            fg_color=self.COLORS['input'],
            hover_color=self.COLORS['border'],
            width=140,
            height=32
        )
        self.hotkey_button.pack(side="right")

        # Hotkey hint
        ctk.CTkLabel(
            card, 
            text="Click the button and press your desired key combination",
            font=("Segoe UI", 11),
            text_color=self.COLORS['text_secondary']
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Divider
        ctk.CTkFrame(card, fg_color=self.COLORS['border'], height=1).pack(fill="x", padx=20)

        # Default deck setting
        deck_frame = ctk.CTkFrame(card, fg_color=self.COLORS['card'])
        deck_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            deck_frame, 
            text="Default Deck", 
            font=("Segoe UI", 13),
            text_color=self.COLORS['text']
        ).pack(side="left")

        # Use cached decks for instant display, will be updated async
        cached_decks = self.settings_manager.get('cached_decks', [])
        self.deck_dropdown_values = ["None (Ask every time)"] + cached_decks
        current_deck = self.settings_manager.get('default_deck') or "None (Ask every time)"

        def update_deck(choice):
            self.settings_manager.set('default_deck', None if choice == "None (Ask every time)" else choice)

        self.deck_dropdown = ctk.CTkComboBox(
            deck_frame, 
            values=self.deck_dropdown_values, 
            command=update_deck, 
            width=180,
            fg_color=self.COLORS['input'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['primary_hover']
        )
        self.deck_dropdown.set(current_deck)
        self.deck_dropdown.pack(side="right")

        # Divider
        ctk.CTkFrame(card, fg_color=self.COLORS['border'], height=1).pack(fill="x", padx=20)

        # Start on startup setting
        startup_frame = ctk.CTkFrame(card, fg_color=self.COLORS['card'])
        startup_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            startup_frame, 
            text="Start on Windows Startup", 
            font=("Segoe UI", 13),
            text_color=self.COLORS['text']
        ).pack(side="left")

        startup_var = ctk.BooleanVar(value=self.is_startup_enabled())

        def toggle_startup():
            enabled = startup_var.get()
            if not self.set_startup_enabled(enabled):
                startup_var.set(not enabled)
                self._show_toast("Failed to update startup setting")

        startup_switch = ctk.CTkSwitch(
            startup_frame,
            text="",
            variable=startup_var,
            command=toggle_startup,
            width=51,
            height=26,
            switch_width=48,
            switch_height=24,
            corner_radius=12,
            fg_color=("#d1d5db", "#4b5563"),  # Gray when OFF (light/dark mode)
            progress_color=self.COLORS['primary'],  # Blue when ON
            button_color=self.COLORS['text'],  # White button
            button_hover_color=("#f3f4f6", "#e5e7eb"),  # Slight hover effect
        )
        startup_switch.pack(side="right")

        # Status indicator - shows "Checking..." until async check completes
        status_frame = ctk.CTkFrame(frame, fg_color=self.COLORS['bg'])
        status_frame.pack(fill="x", pady=(20, 0))

        self.anki_status_label = ctk.CTkLabel(
            status_frame,
            text="Checking Anki...",
            font=("Segoe UI", 12),
            text_color=self.COLORS['text_secondary']
        )
        self.anki_status_label.pack(side="left")

    def _create_notifications_tab(self):
        """Create the Notifications settings tab."""
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['bg'])
        self.tab_frames["notifications"] = frame

        # Tab title
        ctk.CTkLabel(
            frame, 
            text="Notifications", 
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORS['text']
        ).pack(anchor="w", pady=(0, 20))

        # Settings card
        card = ctk.CTkFrame(frame, fg_color=self.COLORS['card'], corner_radius=10)
        card.pack(fill="x")

        # Badge counter setting
        badge_frame = ctk.CTkFrame(card, fg_color=self.COLORS['card'])
        badge_frame.pack(fill="x", padx=20, pady=(20, 10))

        badge_text_frame = ctk.CTkFrame(badge_frame, fg_color=self.COLORS['card'])
        badge_text_frame.pack(side="left")

        ctk.CTkLabel(
            badge_text_frame, 
            text="Card Counter Badge", 
            font=("Segoe UI", 13),
            text_color=self.COLORS['text']
        ).pack(anchor="w")

        ctk.CTkLabel(
            badge_text_frame, 
            text="Shows count on taskbar icon. Clears when viewing History.",
            font=("Segoe UI", 11),
            text_color=self.COLORS['text_secondary']
        ).pack(anchor="w")

        badge_var = ctk.BooleanVar(value=self.settings_manager.get('notification_badge_enabled', True))

        def toggle_badge():
            self.settings_manager.set('notification_badge_enabled', badge_var.get())
            self.update_tray_icon()

        badge_switch = ctk.CTkSwitch(
            badge_frame,
            text="",
            variable=badge_var,
            command=toggle_badge,
            width=51,
            height=26,
            switch_width=48,
            switch_height=24,
            corner_radius=12,
            fg_color=("#d1d5db", "#4b5563"),  # Gray when OFF (light/dark mode)
            progress_color=self.COLORS['primary'],  # Blue when ON
            button_color=self.COLORS['text'],  # White button
            button_hover_color=("#f3f4f6", "#e5e7eb"),  # Slight hover effect
        )
        badge_switch.pack(side="right")

        # Divider
        ctk.CTkFrame(card, fg_color=self.COLORS['border'], height=1).pack(fill="x", padx=20, pady=10)

        # Toast notification setting
        toast_frame = ctk.CTkFrame(card, fg_color=self.COLORS['card'])
        toast_frame.pack(fill="x", padx=20, pady=(10, 20))

        toast_text_frame = ctk.CTkFrame(toast_frame, fg_color=self.COLORS['card'])
        toast_text_frame.pack(side="left")

        ctk.CTkLabel(
            toast_text_frame, 
            text="Toast Notification", 
            font=("Segoe UI", 13),
            text_color=self.COLORS['text']
        ).pack(anchor="w")

        ctk.CTkLabel(
            toast_text_frame, 
            text="Semi-transparent popup in bottom-right corner (1 second).",
            font=("Segoe UI", 11),
            text_color=self.COLORS['text_secondary']
        ).pack(anchor="w")

        toast_var = ctk.BooleanVar(value=self.settings_manager.get('notification_toast_enabled', False))

        def toggle_toast():
            self.settings_manager.set('notification_toast_enabled', toast_var.get())

        toast_switch = ctk.CTkSwitch(
            toast_frame,
            text="",
            variable=toast_var,
            command=toggle_toast,
            width=51,
            height=26,
            switch_width=48,
            switch_height=24,
            corner_radius=12,
            fg_color=("#d1d5db", "#4b5563"),  # Gray when OFF (light/dark mode)
            progress_color=self.COLORS['primary'],  # Blue when ON
            button_color=self.COLORS['text'],  # White button
            button_hover_color=("#f3f4f6", "#e5e7eb"),  # Slight hover effect
        )
        toast_switch.pack(side="right")

    def _create_history_tab(self):
        """Create the History tab."""
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.COLORS['bg'])
        self.tab_frames["history"] = frame

        # Tab title
        ctk.CTkLabel(
            frame, 
            text="Recent Cards", 
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORS['text']
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            frame, 
            text="Your 10 most recently created flashcards",
            font=("Segoe UI", 12),
            text_color=self.COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 15))

        # Scrollable frame for cards
        self.history_scroll = ctk.CTkScrollableFrame(
            frame, 
            fg_color=self.COLORS['bg'],
            scrollbar_button_color=self.COLORS['border'],
            scrollbar_button_hover_color=self.COLORS['primary']
        )
        self.history_scroll.pack(fill="both", expand=True)

    def _refresh_history_content(self):
        """Refresh the history tab content."""
        # Clear existing content
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        history = self.settings_manager.get('card_history', [])

        if not history:
            ctk.CTkLabel(
                self.history_scroll,
                text="No cards created yet.\nUse the hotkey to capture words!",
                font=("Segoe UI", 12),
                text_color=self.COLORS['text_secondary']
            ).pack(pady=50)
            return

        # Create card tiles
        for i, card in enumerate(history):
            tile = ctk.CTkFrame(
                self.history_scroll, 
                fg_color=self.COLORS['card'], 
                corner_radius=8
            )
            tile.pack(fill="x", pady=(0, 8))

            # Word (front)
            ctk.CTkLabel(
                tile,
                text=card.get('word', 'Unknown'),
                font=("Segoe UI", 14, "bold"),
                text_color=self.COLORS['text']
            ).pack(anchor="w", padx=15, pady=(12, 2))

            # Definition (back) - truncated if too long
            definition = card.get('definition', '')
            if len(definition) > 100:
                definition = definition[:100] + "..."

            ctk.CTkLabel(
                tile,
                text=definition,
                font=("Segoe UI", 11),
                text_color=self.COLORS['text_secondary'],
                wraplength=420,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 12))

    def run(self, start_minimized=False):
        """Start the application."""
        self.setup_hotkey()
        self.create_main_window()
        self.setup_tray_icon()
        
        if start_minimized:
            self.root.withdraw()
        
        self.root.after(100, self.process_gui_queue)
        
        # Fetch Anki decks asynchronously after window is shown
        self.root.after(200, self._fetch_decks_async)
        
        # Start background Anki connection monitoring
        self.root.after(500, self._start_anki_monitor)
        
        print("Lexi Snap running!")
        hotkey = self.settings_manager.get('hotkey', '')
        if hotkey:
            print(f"Hotkey: {hotkey.upper()}")
        else:
            print("No hotkey configured - open settings to set one")
        
        if start_minimized:
            print("Started minimized to system tray.")
        else:
            print("Minimize the window - it keeps running in the system tray.")
        
        self.root.mainloop()


def main():
    start_minimized = '--minimized' in sys.argv
    
    import ctypes
    from ctypes import wintypes
    
    kernel32 = ctypes.windll.kernel32
    mutex_name = "lexi-snap_SingleInstance_Mutex"
    
    handle = kernel32.CreateMutexW(None, True, mutex_name)
    last_error = kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(
            0, 
            "Lexi Snap is already running!\n\nCheck your system tray.", 
            "Lexi Snap", 
            0x40
        )
        if handle:
            kernel32.CloseHandle(handle)
        sys.exit(0)

    app = LexiSnapApp()
    app.run(start_minimized=start_minimized)


if __name__ == '__main__':
    main()
