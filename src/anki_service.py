"""AnkiConnect service for interfacing with Anki."""

import requests
from typing import List, Dict, Optional


class AnkiService:
    """Communicates with Anki through AnkiConnect API."""

    def __init__(self, url="http://localhost:8765"):
        """
        Initialize AnkiConnect service.

        Args:
            url: AnkiConnect API URL (default: http://localhost:8765)
        """
        self.url = url

    def invoke(self, action: str, params: Optional[Dict] = None):
        """
        Invoke an AnkiConnect action.

        Args:
            action: The AnkiConnect action name
            params: Parameters for the action

        Returns:
            The result from AnkiConnect

        Raises:
            Exception: If AnkiConnect returns an error
        """
        payload = {
            'action': action,
            'version': 6,
            'params': params or {}
        }

        try:
            response = requests.post(self.url, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()

            if result.get('error'):
                raise Exception(f"AnkiConnect error: {result['error']}")

            return result.get('result')

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Anki: {e}")

    def check_connection(self) -> bool:
        """
        Check if AnkiConnect is available.

        Returns:
            True if connected, False otherwise
        """
        try:
            version = self.invoke('version')
            return version is not None
        except:
            return False

    def get_deck_names(self) -> List[str]:
        """
        Get list of all deck names.

        Returns:
            List of deck names
        """
        try:
            decks = self.invoke('deckNames')
            return decks if decks else []
        except:
            return []

    def add_note(self, deck_name: str, word: str, definitions: List[Dict[str, str]]) -> int:
        """
        Add a vocabulary card to Anki.

        Args:
            deck_name: Target deck name
            word: The vocabulary word (front of card)
            definitions: List of definition dictionaries

        Returns:
            Note ID of the created card

        Raises:
            Exception: If card creation fails
        """
        back_content = self._format_card_back(definitions)

        note = {
            'deckName': deck_name,
            'modelName': 'Basic',
            'fields': {
                'Front': word,
                'Back': back_content
            },
            'tags': ['dict-to-anki', 'vocabulary'],
            'options': {
                'allowDuplicate': False
            }
        }

        try:
            note_id = self.invoke('addNote', {'note': note})
            return note_id
        except Exception as e:
            # Check if it's a duplicate
            if 'duplicate' in str(e).lower():
                raise Exception(f"'{word}' already exists in deck '{deck_name}'")
            raise

    def _format_card_back(self, definitions: List[Dict[str, str]]) -> str:
        """
        Format the back of the card with HTML.

        Args:
            definitions: List of definition dictionaries

        Returns:
            HTML-formatted string for card back
        """
        content_parts = []

        # Add definitions
        for i, defn in enumerate(definitions, 1):
            pos = defn.get('part_of_speech', '')
            definition = defn.get('definition', '')
            example = defn.get('example', '')

            # Format definition with part of speech
            defn_html = f"<b>{i}. ({pos})</b> {definition}"
            content_parts.append(defn_html)

            # Add example if available
            if example:
                content_parts.append(f"<i>Example: {example}</i>")

        return '<br><br>'.join(content_parts)

    def ensure_basic_model_exists(self) -> bool:
        """
        Check if Basic note type exists.

        Returns:
            True if Basic model exists
        """
        try:
            models = self.invoke('modelNames')
            return 'Basic' in models
        except:
            return False
