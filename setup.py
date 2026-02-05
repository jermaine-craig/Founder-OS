#!/usr/bin/env python3
"""
Founder OS Setup Wizard
Interactive setup for Gmail and Calendar integration.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent
TOOLS_DIR = ROOT_DIR / '_tools'
CREDS_DIR = TOOLS_DIR / '.credentials'
CLAUDE_MD_PATH = ROOT_DIR / '.claude' / 'CLAUDE.md'
GCAL_PATH = TOOLS_DIR / 'gcal.py'

# Required packages
REQUIRED_PACKAGES = [
    'google-auth',
    'google-auth-oauthlib',
    'google-api-python-client',
]


def print_header(text):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print('=' * 50)


def print_step(num, text):
    """Print a step header."""
    print(f"\nStep {num}: {text}")
    print('-' * 40)


def check_python_version():
    """Ensure Python 3.8+."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"You have: Python {sys.version}")
        sys.exit(1)


def check_packages():
    """Check if required packages are installed."""
    missing = []
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.replace('-', '_').split('[')[0])
        except ImportError:
            missing.append(package)

    if missing:
        print("\nMissing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")

        install = input("\nInstall them now? [y/n]: ").strip().lower()
        if install == 'y':
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("\nPackages installed successfully!")
        else:
            print("\nPlease install manually:")
            print(f"  pip install {' '.join(missing)}")
            sys.exit(1)


def setup_google_cloud():
    """Guide user through Google Cloud setup."""
    print_step(1, "Google Cloud Project")

    print("""
To use Gmail and Calendar, you need a Google Cloud project.

1. Go to: https://console.cloud.google.com/projectcreate
   - Create a new project (name it anything, e.g., "Founder OS")

2. Enable APIs:
   - Go to: https://console.cloud.google.com/apis/library
   - Search for and enable:
     * Gmail API
     * Google Calendar API

3. Configure OAuth consent screen:
   - Go to: https://console.cloud.google.com/apis/credentials/consent
   - Choose "External" user type
   - Fill in app name (e.g., "Founder OS")
   - Add your email as a test user

4. Create OAuth credentials:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Download the JSON file

5. Rename the downloaded file to 'client_secret.json'
""")

    while True:
        ready = input("Have you downloaded client_secret.json? [y/n]: ").strip().lower()
        if ready == 'y':
            break
        elif ready == 'n':
            print("\nPlease complete the steps above, then run this wizard again.")
            sys.exit(0)

    # Get path to client_secret.json
    while True:
        path = input("\nEnter path to client_secret.json: ").strip()
        path = os.path.expanduser(path)

        if os.path.exists(path):
            # Copy to credentials folder
            CREDS_DIR.mkdir(parents=True, exist_ok=True)
            dest = CREDS_DIR / 'client_secret.json'
            shutil.copy(path, dest)
            print(f"\n✓ Copied to {dest}")
            break
        else:
            print(f"  File not found: {path}")
            print("  Please check the path and try again.")


def setup_gmail():
    """Authenticate with Gmail."""
    print_step(2, "Gmail Authentication")

    print("\nAuthenticating with Gmail...")
    print("A browser window will open. Sign in with your Google account.")
    input("\nPress Enter to continue...")

    # Import and run auth
    sys.path.insert(0, str(TOOLS_DIR))
    from gmail import get_gmail_service

    service = get_gmail_service()
    if service:
        print("\n✓ Gmail authenticated successfully!")
        return True
    else:
        print("\n✗ Gmail authentication failed.")
        return False


def setup_calendar():
    """Authenticate with Calendar."""
    print_step(3, "Calendar Authentication")

    print("\nAuthenticating with Google Calendar...")
    print("A browser window will open. Sign in with the same Google account.")
    input("\nPress Enter to continue...")

    sys.path.insert(0, str(TOOLS_DIR))
    from gcal import get_calendar_service

    service = get_calendar_service()
    if service:
        print("\n✓ Calendar authenticated successfully!")
        return True
    else:
        print("\n✗ Calendar authentication failed.")
        return False


def setup_user_details():
    """Get user details and update CLAUDE.md."""
    print_step(4, "Your Details")

    name = input("\nYour name: ").strip()

    print("\nCommon timezones:")
    print("  - Europe/London")
    print("  - America/New_York")
    print("  - America/Los_Angeles")
    print("  - Asia/Tokyo")
    print("  - Australia/Sydney")

    timezone = input("\nYour timezone (e.g., Europe/London): ").strip()

    # Update CLAUDE.md
    if CLAUDE_MD_PATH.exists():
        content = CLAUDE_MD_PATH.read_text()
        content = content.replace('{{NAME}}', name)
        content = content.replace('{{TIMEZONE}}', timezone)
        CLAUDE_MD_PATH.write_text(content)
        print(f"\n✓ Updated {CLAUDE_MD_PATH}")

    # Update gcal.py default timezone
    if GCAL_PATH.exists():
        content = GCAL_PATH.read_text()
        content = content.replace("DEFAULT_TZ = 'Europe/London'", f"DEFAULT_TZ = '{timezone}'")
        GCAL_PATH.write_text(content)
        print(f"✓ Updated default timezone in gcal.py")

    return name, timezone


def test_connections():
    """Test Gmail and Calendar connections."""
    print_step(5, "Test Connections")

    sys.path.insert(0, str(TOOLS_DIR))

    # Test Gmail
    print("\nTesting Gmail...")
    try:
        from gmail import get_gmail_service
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', maxResults=5, q='is:unread').execute()
        count = len(results.get('messages', []))
        print(f"✓ Gmail working - found {count} unread emails")
    except Exception as e:
        print(f"✗ Gmail test failed: {e}")

    # Test Calendar
    print("\nTesting Calendar...")
    try:
        from gcal import get_calendar_service
        from datetime import datetime, timedelta
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        results = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=10,
            singleEvents=True
        ).execute()
        count = len(results.get('items', []))
        print(f"✓ Calendar working - found {count} events this week")
    except Exception as e:
        print(f"✗ Calendar test failed: {e}")


def print_success():
    """Print success message and next steps."""
    print_header("Setup Complete!")

    print("""
Your Founder OS is ready!

Try these commands:
  python3 _tools/gmail.py fetch
  python3 _tools/gcal.py list
  python3 _tools/gcal.py availability $(date +%Y-%m-%d)

Open Claude Code and try:
  /triage    - Process your inbox
  /calendar  - Check your schedule

Need help? See README.md for documentation.
""")


def main():
    print_header("Founder OS Setup Wizard")

    # Checks
    check_python_version()
    check_packages()

    # Setup steps
    setup_google_cloud()
    setup_gmail()
    setup_calendar()
    setup_user_details()
    test_connections()

    # Done
    print_success()


if __name__ == '__main__':
    main()
