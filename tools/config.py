#!/usr/bin/env python3
"""
Shared configuration for Founder OS tools.
Reads user settings from .credentials/config.json, written by setup wizard.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CREDS_DIR = PROJECT_ROOT / '.credentials'
OUTPUT_DIR = PROJECT_ROOT / 'output'
TEMP_DIR = PROJECT_ROOT / '_temp'
CONFIG_PATH = CREDS_DIR / 'config.json'

DEFAULTS = {
    'name': '',
    'timezone': 'Europe/London',
    'perplexity_api_key': '',
}


def load_config():
    """Load user config. Returns defaults if file missing."""
    config = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            stored = json.load(f)
        config.update(stored)
    return config


def save_config(config):
    """Persist user config to .credentials/config.json."""
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def get_timezone():
    """Return configured timezone."""
    return load_config()['timezone']


def get_name():
    """Return configured user name."""
    return load_config()['name']
