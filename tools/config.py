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
    'meeting_naming': '{name} x {participants} - {context}',
    'preferred_meeting_duration': 30,
    'preferred_meeting_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'preferred_meeting_times': {'start': '09:00', 'end': '17:00'},
}


def load_config():
    """Load user config. Returns defaults merged with stored values."""
    config = {}
    # Deep copy defaults so nested dicts/lists aren't shared
    for k, v in DEFAULTS.items():
        if isinstance(v, dict):
            config[k] = dict(v)
        elif isinstance(v, list):
            config[k] = list(v)
        else:
            config[k] = v
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


def get_meeting_naming():
    """Return the meeting naming template string."""
    return load_config()['meeting_naming']


def get_meeting_preferences():
    """Return meeting preferences: duration, days, and time window."""
    config = load_config()
    return {
        'duration': config['preferred_meeting_duration'],
        'days': config['preferred_meeting_days'],
        'times': config['preferred_meeting_times'],
    }
