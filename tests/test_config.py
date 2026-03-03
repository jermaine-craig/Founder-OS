"""
Tests for tools/config.py.
Verifies configuration loading, saving, and default fallback behaviour.
"""

import json
import pytest
from unittest.mock import patch


@pytest.mark.unit
class TestLoadConfig:
    """Tests for load_config and related helpers."""

    def test_load_config_returns_defaults_when_no_file(self, tmp_config):
        """When config.json does not exist, defaults should be returned."""
        from tools.config import load_config, DEFAULTS

        # tmp_config fixture patches CONFIG_PATH but does not create the file
        config = load_config()

        assert config['timezone'] == DEFAULTS['timezone']
        assert config['name'] == DEFAULTS['name']
        assert config['perplexity_api_key'] == DEFAULTS['perplexity_api_key']

    def test_save_and_load_config(self, tmp_config):
        """Saving then loading should round-trip correctly."""
        from tools.config import load_config, save_config

        custom = {
            'name': 'Jermaine',
            'timezone': 'Africa/Johannesburg',
            'perplexity_api_key': 'pplx-test-key',
        }
        save_config(custom)

        loaded = load_config()

        assert loaded['name'] == 'Jermaine'
        assert loaded['timezone'] == 'Africa/Johannesburg'
        assert loaded['perplexity_api_key'] == 'pplx-test-key'

    def test_get_timezone_returns_configured_value(self, tmp_config):
        """get_timezone should return the timezone from the saved config."""
        from tools.config import get_timezone, save_config

        save_config({'timezone': 'America/New_York'})

        assert get_timezone() == 'America/New_York'

    def test_get_name_returns_configured_value(self, tmp_config):
        """get_name should return the name from the saved config."""
        from tools.config import get_name, save_config

        save_config({'name': 'Jermaine'})

        assert get_name() == 'Jermaine'

    def test_defaults_used_for_missing_keys(self, tmp_config):
        """Saved config with partial keys should be merged with defaults."""
        from tools.config import load_config, save_config, DEFAULTS

        # Only save name, omit timezone and api key
        save_config({'name': 'Jermaine'})

        loaded = load_config()

        assert loaded['name'] == 'Jermaine'
        assert loaded['timezone'] == DEFAULTS['timezone']
        assert loaded['perplexity_api_key'] == DEFAULTS['perplexity_api_key']
