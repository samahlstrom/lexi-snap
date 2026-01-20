"""Basic test script to verify core functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dictionary_service import DictionaryService
from anki_service import AnkiService
from config_manager import ConfigManager


def test_dictionary_service():
    """Test dictionary API."""
    print("Testing Dictionary Service...")
    print("-" * 50)

    dict_service = DictionaryService()

    # Test with a common word
    test_word = "example"
    print(f"Looking up '{test_word}'...")

    definitions = dict_service.get_definitions(test_word, max_definitions=3)

    if definitions:
        print(f"[OK] Found {len(definitions)} definition(s):\n")
        for i, defn in enumerate(definitions, 1):
            print(f"{i}. [{defn['part_of_speech']}] {defn['definition']}")
            if defn['example']:
                print(f"   Example: {defn['example']}")
            print()
    else:
        print("[FAIL] No definitions found!")
        return False

    return True


def test_anki_connection():
    """Test AnkiConnect connection."""
    print("\nTesting AnkiConnect Service...")
    print("-" * 50)

    anki_service = AnkiService()

    print("Checking connection to Anki...")
    if anki_service.check_connection():
        print("[OK] Connected to Anki successfully!")

        # Get deck names
        decks = anki_service.get_deck_names()
        print(f"[OK] Found {len(decks)} deck(s):")
        for deck in decks:
            print(f"  - {deck}")

        return True
    else:
        print("[FAIL] Could not connect to Anki")
        print("\nMake sure:")
        print("1. Anki is running")
        print("2. AnkiConnect add-on is installed (code: 2055492159)")
        print("3. Anki has been restarted after installing AnkiConnect")
        return False


def test_config():
    """Test configuration manager."""
    print("\nTesting Configuration Manager...")
    print("-" * 50)

    config = ConfigManager()

    print(f"[OK] Config file location: {config.config_path}")
    print(f"[OK] AnkiConnect URL: {config.ankiconnect_url}")
    print(f"[OK] Max definitions: {config.max_definitions}")
    print(f"[OK] Clipboard delay: {config.clipboard_delay}s")
    print(f"[OK] Show notifications: {config.show_notifications}")

    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Dict-to-Anki Basic Functionality Test")
    print("=" * 50)
    print()

    results = []

    # Test 1: Config
    results.append(("Configuration", test_config()))

    # Test 2: Dictionary
    results.append(("Dictionary API", test_dictionary_service()))

    # Test 3: Anki (only if Anki is running)
    results.append(("AnkiConnect", test_anki_connection()))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for test_name, passed in results:
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{test_name:20s} {status}")

    print()

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("[OK] All tests passed!")
        print("\nYou can now use Dict-to-Anki:")
        print("  python main.py --text 'serendipity'")
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
