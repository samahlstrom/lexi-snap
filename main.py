"""Dict-to-Anki: System-wide vocabulary capture tool."""

import sys
import argparse
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from text_capture import TextCapture
from dictionary_service import DictionaryService
from anki_service import AnkiService
from config_manager import ConfigManager
from gui_dialogs import DeckSelectionDialog, show_notification, show_error_dialog


class DictToAnkiApp:
    """Main application for Dict-to-Anki."""

    def __init__(self):
        """Initialize the application."""
        self.config = ConfigManager()
        self.text_capture = TextCapture(clipboard_delay=self.config.clipboard_delay)
        self.dict_service = DictionaryService(timeout=self.config.timeout_seconds)
        self.anki_service = AnkiService(url=self.config.ankiconnect_url)

    def run(self, deck_name=None, selected_text=None):
        """
        Run the vocabulary capture workflow.

        Args:
            deck_name: Optional pre-selected deck name
            selected_text: Optional pre-captured text (for stdin mode)
        """
        try:
            # Step 1: Check Anki connection
            if not self.anki_service.check_connection():
                error_msg = (
                    "Cannot connect to Anki!\n\n"
                    "Please ensure:\n"
                    "1. Anki is running\n"
                    "2. AnkiConnect add-on is installed (code: 2055492159)\n"
                    "3. Anki has been restarted after installing AnkiConnect"
                )
                show_error_dialog(error_msg, "Anki Connection Error")
                return

            # Step 2: Capture selected text
            if selected_text is None:
                selected_text = self.text_capture.get_selected_text()

            if not selected_text:
                show_error_dialog(
                    "No text is currently selected.\n\n"
                    "Please highlight a word and try again.",
                    "No Text Selected"
                )
                return

            # Step 3: Extract word
            word = self.text_capture.get_word_from_selection(selected_text)
            if not word:
                show_error_dialog(
                    "Could not extract a word from the selection.",
                    "Invalid Selection"
                )
                return

            # Step 4: Fetch definitions
            print(f"Looking up '{word}'...")
            definitions = self.dict_service.get_definitions(
                word,
                max_definitions=self.config.max_definitions
            )

            if not definitions:
                show_error_dialog(
                    f"No definitions found for '{word}'.\n\n"
                    f"This could mean:\n"
                    f"1. The word is misspelled\n"
                    f"2. It's not in the dictionary\n"
                    f"3. No internet connection",
                    "Definition Not Found"
                )
                return

            # Step 6: Select deck
            if not deck_name:
                decks = self.anki_service.get_deck_names()
                if not decks:
                    show_error_dialog(
                        "No Anki decks found.\n\n"
                        "Please create at least one deck in Anki first.",
                        "No Decks Available"
                    )
                    return

                deck_name = DeckSelectionDialog(decks).show()
                if not deck_name:
                    # User cancelled
                    return

            # Step 6: Add to Anki
            print(f"Adding '{word}' to deck '{deck_name}'...")
            note_id = self.anki_service.add_note(deck_name, word, definitions)

            # Step 7: Show success notification
            if self.config.show_notifications:
                show_notification(
                    "Card Created!",
                    f"Added '{word}' to '{deck_name}'"
                )

            print(f"Success! Note ID: {note_id}")

        except Exception as e:
            error_msg = str(e)
            show_error_dialog(error_msg, "Error")
            print(f"Error: {error_msg}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Dict-to-Anki: Capture vocabulary from anywhere'
    )
    parser.add_argument(
        '--deck',
        help='Target deck name (skips deck selection dialog)'
    )
    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read selected text from stdin (for macOS service)'
    )
    parser.add_argument(
        '--text',
        help='Provide text directly instead of capturing from clipboard'
    )

    args = parser.parse_args()

    # Get selected text from stdin if requested (macOS service mode)
    selected_text = None
    if args.stdin:
        selected_text = sys.stdin.read().strip()
    elif args.text:
        selected_text = args.text

    # Run the application
    app = DictToAnkiApp()
    app.run(deck_name=args.deck, selected_text=selected_text)


if __name__ == '__main__':
    main()
