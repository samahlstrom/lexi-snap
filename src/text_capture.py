"""Text capture module for getting highlighted text from any application."""

import pyperclip
import pyautogui
import time
import platform


class TextCapture:
    """Captures selected text from any application using clipboard simulation."""

    def __init__(self, clipboard_delay=0.1):
        """
        Initialize text capture.

        Args:
            clipboard_delay: Delay in seconds to wait for clipboard update
        """
        self.clipboard_delay = clipboard_delay
        self.is_macos = platform.system() == 'Darwin'

    def get_selected_text(self):
        """
        Capture currently selected text by simulating copy operation.

        Returns:
            str: The selected text, or empty string if nothing is selected
        """
        # Save current clipboard content
        old_clipboard = pyperclip.paste()

        # Clear clipboard to detect if copy was successful
        pyperclip.copy('')

        # Simulate copy command (Cmd+C on macOS, Ctrl+C on Windows/Linux)
        if self.is_macos:
            pyautogui.hotkey('command', 'c')
        else:
            pyautogui.hotkey('ctrl', 'c')

        # Wait for clipboard to update
        time.sleep(self.clipboard_delay)

        # Get new clipboard content
        selected_text = pyperclip.paste()

        # Restore original clipboard
        pyperclip.copy(old_clipboard)

        return selected_text.strip() if selected_text else ''

    def get_word_from_selection(self, selected_text):
        """
        Extract the first word from selected text.

        Args:
            selected_text: The full selected text

        Returns:
            str: The first word, cleaned of punctuation
        """
        if not selected_text:
            return ''

        # Get first word
        words = selected_text.split()
        if not words:
            return ''

        first_word = words[0]

        # Remove common punctuation from start and end
        punctuation = '.,;:!?"\'()[]{}«»""''`'
        first_word = first_word.strip(punctuation)

        return first_word.lower()
