"""Dictionary API service for fetching word definitions."""

import requests
from typing import List, Dict, Optional


class DictionaryService:
    """Fetches word definitions from free dictionary APIs."""

    PRIMARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"
    BACKUP_API = "https://api.freedictionaryapi.com/v1/entries/en"

    def __init__(self, timeout=5):
        """
        Initialize dictionary service.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def get_definitions(self, word: str, max_definitions: int = 3) -> List[Dict[str, str]]:
        """
        Fetch definitions for a word.

        Args:
            word: The word to look up
            max_definitions: Maximum number of definitions to return

        Returns:
            List of definition dictionaries with keys:
            - part_of_speech: noun, verb, adjective, etc.
            - definition: The definition text
            - example: Example sentence (may be empty)
            - synonyms: List of synonyms (may be empty)
        """
        # Try primary API first
        definitions = self._fetch_from_primary_api(word, max_definitions)

        # Fallback to backup API if primary fails
        if not definitions:
            definitions = self._fetch_from_backup_api(word, max_definitions)

        return definitions

    def _fetch_from_primary_api(self, word: str, max_definitions: int) -> List[Dict[str, str]]:
        """
        Fetch from dictionaryapi.dev.

        Args:
            word: The word to look up
            max_definitions: Maximum number of definitions

        Returns:
            List of definition dictionaries
        """
        try:
            url = f"{self.PRIMARY_API}/{word}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            definitions = []
            for entry in data:
                for meaning in entry.get('meanings', []):
                    part_of_speech = meaning.get('partOfSpeech', 'unknown')

                    for defn in meaning.get('definitions', []):
                        definitions.append({
                            'part_of_speech': part_of_speech,
                            'definition': defn.get('definition', ''),
                            'example': defn.get('example', ''),
                            'synonyms': defn.get('synonyms', [])
                        })

                        if len(definitions) >= max_definitions:
                            return definitions[:max_definitions]

            return definitions[:max_definitions]

        except Exception as e:
            print(f"Primary API error: {e}")
            return []

    def _fetch_from_backup_api(self, word: str, max_definitions: int) -> List[Dict[str, str]]:
        """
        Fetch from freedictionaryapi.com as backup.

        Args:
            word: The word to look up
            max_definitions: Maximum number of definitions

        Returns:
            List of definition dictionaries
        """
        try:
            url = f"{self.BACKUP_API}/{word}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            definitions = []
            for entry in data:
                for meaning in entry.get('meanings', []):
                    part_of_speech = meaning.get('partOfSpeech', 'unknown')

                    for defn in meaning.get('definitions', []):
                        definitions.append({
                            'part_of_speech': part_of_speech,
                            'definition': defn.get('definition', ''),
                            'example': defn.get('example', ''),
                            'synonyms': []  # Backup API may not have synonyms
                        })

                        if len(definitions) >= max_definitions:
                            return definitions[:max_definitions]

            return definitions[:max_definitions]

        except Exception as e:
            print(f"Backup API error: {e}")
            return []
