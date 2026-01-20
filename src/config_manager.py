"""Configuration management for Dict-to-Anki."""

import configparser
import os
import platform


class ConfigManager:
    """Manages application configuration."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_path = self._get_config_path()
        self.config = configparser.ConfigParser()
        self.load_or_create_default()

    def _get_config_path(self) -> str:
        """
        Get the configuration file path based on OS.

        Returns:
            Full path to config.ini
        """
        if platform.system() == 'Windows':
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        else:  # macOS/Linux
            base_dir = os.path.expanduser('~/.config')

        config_dir = os.path.join(base_dir, 'dict-to-anki')
        os.makedirs(config_dir, exist_ok=True)

        return os.path.join(config_dir, 'config.ini')

    def load_or_create_default(self):
        """Load existing config or create default configuration."""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            self._create_default_config()
            self.save()

    def _create_default_config(self):
        """Create default configuration."""
        self.config['anki'] = {
            'ankiconnect_url': 'http://localhost:8765',
            'max_definitions': '3'
        }

        self.config['dictionary'] = {
            'timeout_seconds': '5'
        }

        self.config['capture'] = {
            'clipboard_delay_ms': '100',
            'restore_clipboard': 'true'
        }

        self.config['ui'] = {
            'show_notifications': 'true'
        }

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def get(self, section: str, key: str, fallback=None):
        """
        Get a configuration value.

        Args:
            section: Config section name
            key: Config key name
            fallback: Default value if not found

        Returns:
            Configuration value or fallback
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get an integer configuration value."""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a boolean configuration value."""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def set(self, section: str, key: str, value: str):
        """
        Set a configuration value.

        Args:
            section: Config section name
            key: Config key name
            value: Value to set
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))

    @property
    def ankiconnect_url(self) -> str:
        """Get AnkiConnect URL."""
        return self.get('anki', 'ankiconnect_url', 'http://localhost:8765')

    @property
    def max_definitions(self) -> int:
        """Get maximum number of definitions."""
        return self.get_int('anki', 'max_definitions', 3)

    @property
    def timeout_seconds(self) -> int:
        """Get dictionary API timeout."""
        return self.get_int('dictionary', 'timeout_seconds', 5)

    @property
    def clipboard_delay(self) -> float:
        """Get clipboard delay in seconds."""
        delay_ms = self.get_int('capture', 'clipboard_delay_ms', 100)
        return delay_ms / 1000.0

    @property
    def show_notifications(self) -> bool:
        """Check if notifications should be shown."""
        return self.get_bool('ui', 'show_notifications', True)
