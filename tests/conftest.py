"""
Shared fixtures for the Founder OS test suite.
All fixtures mock external services so tests never hit the network.
"""

import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# ── Fixture data loaders ──────────────────────────────────────────────

def _load_fixture(name):
    """Load a JSON fixture file from the fixtures directory."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


# ── Shared fixtures ───────────────────────────────────────────────────

@pytest.fixture
def mock_credentials():
    """Patch tools.auth.get_credentials to return a MagicMock.

    Prevents any real OAuth flow from running during tests.
    """
    creds = MagicMock()
    creds.valid = True
    creds.expired = False
    creds.token = 'fake-token'
    with patch('tools.auth.get_credentials', return_value=creds) as patched:
        yield patched


@pytest.fixture
def gmail_fixture_data():
    """Raw Gmail fixture data loaded from JSON."""
    return _load_fixture('gmail_messages.json')


@pytest.fixture
def calendar_fixture_data():
    """Raw Calendar fixture data loaded from JSON."""
    return _load_fixture('calendar_events.json')


@pytest.fixture
def drive_fixture_data():
    """Raw Drive fixture data loaded from JSON."""
    return _load_fixture('drive_files.json')


@pytest.fixture
def mock_gmail_service(gmail_fixture_data):
    """Mock Gmail API service pre-loaded with fixture data.

    Patches tools.gmail.get_gmail so every call returns this mock.
    Supports:
      - users().messages().list().execute()
      - users().messages().get().execute()
      - users().drafts().create().execute()
      - users().messages().modify().execute()
      - users().messages().attachments().get().execute()
    """
    service = MagicMock()
    data = gmail_fixture_data

    # messages().list()
    list_mock = MagicMock()
    list_mock.execute.return_value = data['list_response']
    service.users().messages().list.return_value = list_mock

    # messages().get() returns the matching full message
    def _get_message(**kwargs):
        msg_id = kwargs.get('id', '')
        result = MagicMock()
        result.execute.return_value = data['messages'].get(msg_id, {})
        return result

    service.users().messages().get.side_effect = _get_message

    # messages().modify()
    modify_mock = MagicMock()
    modify_mock.execute.return_value = {}
    service.users().messages().modify.return_value = modify_mock

    # drafts().create()
    draft_mock = MagicMock()
    draft_mock.execute.return_value = {'id': 'draft001', 'message': {'id': 'msg_new'}}
    service.users().drafts().create.return_value = draft_mock

    # attachments().get()
    def _get_attachment(**kwargs):
        att_id = kwargs.get('id', '')
        result = MagicMock()
        result.execute.return_value = data['attachment_data'].get(att_id, {})
        return result

    service.users().messages().attachments().get.side_effect = _get_attachment

    with patch('tools.gmail.get_gmail', return_value=service):
        yield service


@pytest.fixture
def mock_calendar_service(calendar_fixture_data):
    """Mock Calendar API service pre-loaded with fixture data.

    Patches tools.gcal.get_calendar so every call returns this mock.
    Supports:
      - events().list().execute()
      - events().insert().execute()
      - events().delete().execute()
    """
    service = MagicMock()
    data = calendar_fixture_data

    # events().list()
    list_mock = MagicMock()
    list_mock.execute.return_value = data['list_response']
    service.events().list.return_value = list_mock

    # events().insert()
    insert_mock = MagicMock()
    insert_mock.execute.return_value = {
        'id': 'evt_new',
        'htmlLink': 'https://calendar.google.com/event?eid=evt_new',
        'summary': 'New Event',
    }
    service.events().insert.return_value = insert_mock

    # events().delete()
    delete_mock = MagicMock()
    delete_mock.execute.return_value = {}
    service.events().delete.return_value = delete_mock

    with patch('tools.gcal.get_calendar', return_value=service):
        yield service


@pytest.fixture
def mock_drive_service(drive_fixture_data):
    """Mock Drive API service pre-loaded with fixture data.

    Patches tools.gdrive.get_drive so every call returns this mock.
    Supports:
      - files().list().execute()
      - files().get().execute()
      - files().export().execute()
      - files().get_media()
    """
    service = MagicMock()
    data = drive_fixture_data

    # files().list()
    list_mock = MagicMock()
    list_mock.execute.return_value = data['list_response']
    service.files().list.return_value = list_mock

    # files().get() returns matching metadata
    def _get_file(**kwargs):
        file_id = kwargs.get('fileId', '')
        result = MagicMock()
        result.execute.return_value = data['file_metadata'].get(file_id, {
            'id': file_id,
            'name': 'unknown.txt',
            'mimeType': 'text/plain',
        })
        return result

    service.files().get.side_effect = _get_file

    # files().export()
    export_mock = MagicMock()
    export_mock.execute.return_value = b'Exported document content'
    service.files().export.return_value = export_mock

    # files().get_media()
    media_mock = MagicMock()
    service.files().get_media.return_value = media_mock

    with patch('tools.gdrive.get_drive', return_value=service):
        yield service


@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config.json for testing, yield its path, then clean up.

    Patches tools.config paths so load/save use the temporary file.
    """
    config_dir = tmp_path / '.credentials'
    config_dir.mkdir()
    config_path = config_dir / 'config.json'

    with patch('tools.config.CONFIG_PATH', config_path), \
         patch('tools.config.CREDS_DIR', config_dir):
        yield config_path


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Provide a temporary output directory and patch tools that use OUTPUT_DIR."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    yield output_dir
