#!/usr/bin/env python3
"""
Founder OS Setup Wizard
Interactive setup for Gmail, Calendar, and Drive integration.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent
CREDS_DIR = ROOT_DIR / '.credentials'
CLIENT_SECRET_PATH = CREDS_DIR / 'client_secret.json'
CLAUDE_MD_PATH = ROOT_DIR / '.claude' / 'CLAUDE.md'

# Required packages (checked before importing anything optional)
REQUIRED_PACKAGES = {
    'google-auth': 'google.auth',
    'google-auth-oauthlib': 'google_auth_oauthlib',
    'google-api-python-client': 'googleapiclient',
    'questionary': 'questionary',
}

TIMEZONES = [
    'Europe/London',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Kolkata',
    'Australia/Sydney',
    'Pacific/Auckland',
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header(text):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print('=' * 50)


def print_step(num, total, text):
    """Print a numbered step."""
    print(f"\n[{num}/{total}] {text}")
    print('-' * 40)


def print_ok(text):
    """Print a success line."""
    print(f"  [ok] {text}")


def print_fail(text):
    """Print a failure line."""
    print(f"  [FAIL] {text}")


def print_skip(text):
    """Print a skipped line."""
    print(f"  [skip] {text}")


# ---------------------------------------------------------------------------
# Step 1: Python version check
# ---------------------------------------------------------------------------

def check_python_version():
    """Ensure Python 3.9+. Exit if not met."""
    if sys.version_info < (3, 9):
        print(f"\nPython 3.9 or higher is required. You have Python {sys.version}.")
        print("Please upgrade Python and try again.")
        sys.exit(1)
    print_ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


# ---------------------------------------------------------------------------
# Step 2: Package check and install
# ---------------------------------------------------------------------------

def check_and_install_packages():
    """Check for required packages and install any that are missing."""
    missing = []
    for pip_name, import_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        print_ok("All required packages installed")
        return

    print(f"\n  Missing packages: {', '.join(missing)}")
    print("  Installing now...\n")

    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--quiet'] + missing
        )
        print_ok("Packages installed successfully")
    except subprocess.CalledProcessError:
        print_fail("Could not install packages automatically")
        print(f"\n  Please install manually:\n    pip install {' '.join(missing)}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Step 3: Google Cloud setup guide
# ---------------------------------------------------------------------------

def setup_google_cloud():
    """Guide the user through Google Cloud project setup and collect client_secret.json."""
    import questionary

    # If client_secret.json already exists, offer to skip
    if CLIENT_SECRET_PATH.exists():
        reuse = questionary.confirm(
            "client_secret.json already exists. Use the existing file?",
            default=True
        ).ask()
        if reuse:
            print_ok("Using existing client_secret.json")
            return

    print("""
To connect Gmail, Calendar, and Drive you need a Google Cloud project.

  1. Create a project
     https://console.cloud.google.com/projectcreate
     Name it anything you like (e.g. "Founder OS").

  2. Enable APIs
     https://console.cloud.google.com/apis/library
     Search for and enable each of these:
       - Gmail API
       - Google Calendar API
       - Google Drive API

  3. Configure OAuth consent screen
     https://console.cloud.google.com/apis/credentials/consent
     - Choose "External" user type
     - Fill in app name (e.g. "Founder OS")
     - Add your email as a test user

  4. Create OAuth credentials
     https://console.cloud.google.com/apis/credentials
     - Click "Create Credentials" > "OAuth client ID"
     - Choose "Desktop app"
     - Download the JSON file

  5. Note the path where you saved the file.
""")

    ready = questionary.confirm(
        "Have you downloaded the credentials JSON file?",
        default=False
    ).ask()

    if not ready:
        print("\nComplete the steps above, then run this wizard again.")
        sys.exit(0)

    # Ask for file path
    while True:
        path = questionary.text(
            "Path to the downloaded JSON file:",
            validate=lambda p: True if p.strip() else "Please enter a path"
        ).ask()

        if path is None:
            sys.exit(0)

        path = os.path.expanduser(path.strip())

        if not os.path.isfile(path):
            print(f"  File not found: {path}")
            retry = questionary.confirm("Try again?", default=True).ask()
            if not retry:
                sys.exit(0)
            continue

        # Copy to .credentials/
        CREDS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, CLIENT_SECRET_PATH)
        print_ok(f"Copied to {CLIENT_SECRET_PATH}")
        break


# ---------------------------------------------------------------------------
# Step 4: OAuth authentication
# ---------------------------------------------------------------------------

def run_oauth_flow():
    """Run a single OAuth flow covering Gmail, Calendar, and Drive scopes."""
    import questionary

    # Check if token already exists
    token_path = CREDS_DIR / 'token.json'
    if token_path.exists():
        reuse = questionary.confirm(
            "Authentication token already exists. Re-authenticate?",
            default=False
        ).ask()
        if not reuse:
            print_ok("Using existing authentication token")
            return

    if not CLIENT_SECRET_PATH.exists():
        print_fail("client_secret.json not found. Please complete the Google Cloud setup first.")
        sys.exit(1)

    print("\n  A browser window will open. Sign in with your Google account")
    print("  and grant all requested permissions.\n")

    input("  Press Enter to continue...")

    # Import and run auth from tools package
    sys.path.insert(0, str(ROOT_DIR))
    from tools.auth import get_credentials
    get_credentials()

    print_ok("Authenticated successfully (Gmail, Calendar, Drive)")


# ---------------------------------------------------------------------------
# Step 5: User details
# ---------------------------------------------------------------------------

def collect_user_details():
    """Collect name, timezone, and optional Perplexity API key."""
    import questionary

    # Load existing config if re-running
    sys.path.insert(0, str(ROOT_DIR))
    from tools.config import load_config
    existing = load_config()

    # Name
    default_name = existing.get('name', '')
    name = questionary.text(
        "Your name:",
        default=default_name,
        validate=lambda n: True if n.strip() else "Name is required"
    ).ask()

    if name is None:
        sys.exit(0)
    name = name.strip()

    # Timezone
    default_tz = existing.get('timezone', 'Europe/London')
    default_index = TIMEZONES.index(default_tz) if default_tz in TIMEZONES else 0

    timezone = questionary.select(
        "Your timezone:",
        choices=TIMEZONES,
        default=TIMEZONES[default_index]
    ).ask()

    if timezone is None:
        sys.exit(0)

    # Perplexity API key (optional)
    default_key = existing.get('perplexity_api_key', '')
    has_key_prompt = " (leave blank to skip)" if not default_key else " (Enter to keep existing)"

    perplexity_key = questionary.text(
        f"Perplexity API key{has_key_prompt}:",
        default=default_key
    ).ask()

    if perplexity_key is None:
        perplexity_key = ''
    perplexity_key = perplexity_key.strip()

    return name, timezone, perplexity_key


# ---------------------------------------------------------------------------
# Step 6: Save config
# ---------------------------------------------------------------------------

def save_user_config(name, timezone, perplexity_key):
    """Save user config to .credentials/config.json and update CLAUDE.md."""
    sys.path.insert(0, str(ROOT_DIR))
    from tools.config import save_config

    config = {
        'name': name,
        'timezone': timezone,
        'perplexity_api_key': perplexity_key,
    }
    save_config(config)
    print_ok(f"Config saved to {CREDS_DIR / 'config.json'}")

    # Update CLAUDE.md placeholders
    if CLAUDE_MD_PATH.exists():
        content = CLAUDE_MD_PATH.read_text()
        if '{{NAME}}' in content or '{{TIMEZONE}}' in content:
            content = content.replace('{{NAME}}', name)
            content = content.replace('{{TIMEZONE}}', timezone)
            CLAUDE_MD_PATH.write_text(content)
            print_ok("Updated CLAUDE.md with your details")


# ---------------------------------------------------------------------------
# Step 7: Connection tests
# ---------------------------------------------------------------------------

def test_connections():
    """Test Gmail, Calendar, and Drive connections."""
    sys.path.insert(0, str(ROOT_DIR))

    results = {'gmail': False, 'calendar': False, 'drive': False}

    # Gmail
    print("\n  Testing Gmail...")
    try:
        from tools.auth import get_service
        service = get_service('gmail', 'v1')
        result = service.users().messages().list(
            userId='me', maxResults=1
        ).execute()
        count = len(result.get('messages', []))
        print_ok(f"Gmail connected ({count} message{'s' if count != 1 else ''} found)")
        results['gmail'] = True
    except Exception as e:
        print_fail(f"Gmail: {e}")

    # Calendar
    print("\n  Testing Calendar...")
    try:
        from datetime import datetime, timedelta
        service = get_service('calendar', 'v3')
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=1,
            singleEvents=True
        ).execute()
        count = len(result.get('items', []))
        print_ok(f"Calendar connected ({count} event{'s' if count != 1 else ''} this week)")
        results['calendar'] = True
    except Exception as e:
        print_fail(f"Calendar: {e}")

    # Drive
    print("\n  Testing Drive...")
    try:
        service = get_service('drive', 'v3')
        result = service.files().list(
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        count = len(result.get('files', []))
        print_ok(f"Drive connected ({count} file{'s' if count != 1 else ''} found)")
        results['drive'] = True
    except Exception as e:
        print_fail(f"Drive: {e}")

    return results


# ---------------------------------------------------------------------------
# Step 8: Success message
# ---------------------------------------------------------------------------

def print_success(name):
    """Print success message and next steps."""
    print_header("Setup Complete!")

    print(f"""
Welcome, {name}. Your Founder OS is ready.

Try these commands in the terminal:
  python3 tools/gmail.py fetch
  python3 tools/gcal.py list
  python3 tools/gcal.py availability $(date +%Y-%m-%d)
  python3 tools/gdrive.py list

Or open Claude Code and try:
  /email           Process your inbox
  /calendar        Check your schedule
  /meeting         Prepare for a meeting
  /research        Research a topic

Need help? See README.md for documentation.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOTAL_STEPS = 7


def main():
    print_header("Founder OS Setup Wizard")

    # Step 1: Python version
    print_step(1, TOTAL_STEPS, "Checking Python version")
    check_python_version()

    # Step 2: Packages
    print_step(2, TOTAL_STEPS, "Checking required packages")
    check_and_install_packages()

    # Step 3: Google Cloud project
    print_step(3, TOTAL_STEPS, "Google Cloud setup")
    setup_google_cloud()

    # Step 4: OAuth
    print_step(4, TOTAL_STEPS, "Authenticating with Google")
    run_oauth_flow()

    # Step 5: User details
    print_step(5, TOTAL_STEPS, "Your details")
    name, timezone, perplexity_key = collect_user_details()

    # Step 6: Save config
    print_step(6, TOTAL_STEPS, "Saving configuration")
    save_user_config(name, timezone, perplexity_key)

    # Step 7: Test connections
    print_step(7, TOTAL_STEPS, "Testing connections")
    results = test_connections()

    # Summary
    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"\n  Some connections failed: {', '.join(failed)}")
        print("  You can re-run this wizard at any time: python3 setup.py")

    print_success(name)


if __name__ == '__main__':
    main()
