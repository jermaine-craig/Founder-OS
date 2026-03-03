#!/usr/bin/env python3
"""
Shared Google OAuth authentication for Founder OS.
Handles token acquisition, caching, and refresh for all Google APIs.
Single token file covers Gmail, Calendar, and Drive.
"""

import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# All scopes requested in a single OAuth flow
ALL_SCOPES = [
    # Gmail
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    # Calendar
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    # Drive
    'https://www.googleapis.com/auth/drive.readonly',
]

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CREDS_DIR = PROJECT_ROOT / '.credentials'
CLIENT_SECRET_PATH = CREDS_DIR / 'client_secret.json'
TOKEN_PATH = CREDS_DIR / 'token.json'


def get_credentials(scopes=None):
    """
    Get valid Google OAuth credentials.

    Uses a single token file for all services. Triggers browser-based
    auth flow if no valid token exists or if scopes have expanded.

    Args:
        scopes: List of OAuth scopes. Defaults to ALL_SCOPES.

    Returns:
        google.oauth2.credentials.Credentials object.

    Raises:
        FileNotFoundError: If client_secret.json is missing.
    """
    scopes = scopes or ALL_SCOPES
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)

        # Check if saved token is missing any required scopes
        if creds and creds.scopes and set(scopes) - set(creds.scopes):
            print("\nNew permissions needed. Re-authenticating...")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_PATH.exists():
                print(f"ERROR: Client secret not found at {CLIENT_SECRET_PATH}")
                print("\nRun 'python3 setup.py' to configure your credentials.")
                sys.exit(1)

            print("\nOpening browser for Google authorisation...")
            print("Sign in with your Google account.\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH), scopes
            )
            creds = flow.run_local_server(port=0)

        # Save token
        CREDS_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def get_service(api, version):
    """
    Build and return an authenticated Google API service.

    Args:
        api: API name ('gmail', 'calendar', 'drive')
        version: API version ('v1', 'v3', etc.)

    Returns:
        googleapiclient.discovery.Resource object.
    """
    creds = get_credentials()
    return build(api, version, credentials=creds)
