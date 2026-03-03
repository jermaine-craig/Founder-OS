"""
Tests for tools/gmail.py.
All Google API calls are mocked via the mock_gmail_service fixture.
"""

import json
import base64
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestFetchEmails:
    """Tests for the fetch_emails function."""

    def test_fetch_emails_returns_parsed_data(self, mock_gmail_service, tmp_path):
        """Fetched emails should be parsed into structured dicts."""
        from tools.gmail import fetch_emails

        with patch('tools.gmail.OUTPUT_DIR', tmp_path):
            emails = fetch_emails(max_results=3, query='is:unread')

        assert emails is not None
        assert len(emails) == 3

        first = emails[0]
        assert first['id'] == 'msg001'
        assert first['from'] == 'alice@example.com'
        assert first['subject'] == 'Project timeline update'
        assert 'body' in first
        assert 'labels' in first

    def test_fetch_emails_handles_empty_inbox(self, tmp_path):
        """When no messages are returned, fetch_emails should return None."""
        from tools.gmail import fetch_emails

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {'messages': [], 'resultSizeEstimate': 0}
        service.users().messages().list.return_value = list_mock

        with patch('tools.gmail.get_gmail', return_value=service), \
             patch('tools.gmail.OUTPUT_DIR', tmp_path):
            result = fetch_emails()

        assert result is None

    def test_fetch_emails_truncates_long_body(self, tmp_path):
        """Email bodies longer than 5000 characters should be truncated."""
        from tools.gmail import fetch_emails

        long_body = 'A' * 8000
        encoded = base64.urlsafe_b64encode(long_body.encode()).decode()

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {
            'messages': [{'id': 'long01', 'threadId': 'tlong01'}]
        }
        service.users().messages().list.return_value = list_mock

        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'long01',
            'threadId': 'tlong01',
            'snippet': 'Long email',
            'labelIds': ['INBOX'],
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'To', 'value': 'me@example.com'},
                    {'name': 'Subject', 'value': 'Long body'},
                    {'name': 'Date', 'value': 'Mon, 2 Mar 2026 12:00:00 +0000'},
                ],
                'mimeType': 'text/plain',
                'body': {'data': encoded},
            },
        }
        service.users().messages().get.return_value = get_mock

        with patch('tools.gmail.get_gmail', return_value=service), \
             patch('tools.gmail.OUTPUT_DIR', tmp_path):
            emails = fetch_emails(max_results=1)

        assert len(emails[0]['body']) <= 5000

    def test_fetch_emails_saves_to_output(self, mock_gmail_service, tmp_path):
        """Fetched emails should be written to a JSON file in the output directory."""
        from tools.gmail import fetch_emails

        with patch('tools.gmail.OUTPUT_DIR', tmp_path):
            fetch_emails(max_results=3, output_file='test-emails.json')

        output_file = tmp_path / 'test-emails.json'
        assert output_file.exists()

        with open(output_file) as f:
            saved = json.load(f)
        assert len(saved) == 3


@pytest.mark.unit
class TestCreateDraft:
    """Tests for the create_draft function."""

    def test_create_draft_builds_correct_message(self, mock_gmail_service):
        """Draft should be created with the correct to, subject, and body."""
        from tools.gmail import create_draft

        result = create_draft(
            to='recipient@example.com',
            subject='Test subject',
            body='Hello, this is a test.'
        )

        assert result['id'] == 'draft001'

        # Verify the API was called
        call_args = mock_gmail_service.users().drafts().create.call_args
        assert call_args is not None

    def test_create_draft_handles_reply(self):
        """When reply_to_id is set, the draft should include the thread ID."""
        from tools.gmail import create_draft

        service = MagicMock()

        # messages().get() returns the original message with threadId
        get_mock = MagicMock()
        get_mock.execute.return_value = {'threadId': 'thread_reply'}
        service.users().messages().get.return_value = get_mock

        # drafts().create() returns a draft object
        draft_mock = MagicMock()
        draft_mock.execute.return_value = {'id': 'draft_reply', 'message': {'id': 'msg_r'}}
        service.users().drafts().create.return_value = draft_mock

        with patch('tools.gmail.get_gmail', return_value=service):
            result = create_draft(
                to='recipient@example.com',
                subject='Re: Original',
                body='Thanks for your message.',
                reply_to_id='msg_original'
            )

        assert result is not None
        assert result['id'] == 'draft_reply'
        # Verify that messages().get() was called to look up the original
        service.users().messages().get.assert_called()
        # Verify the draft body included the threadId
        create_call = service.users().drafts().create.call_args
        body_arg = create_call[1].get('body', create_call[0][0] if create_call[0] else {})
        assert body_arg['message']['threadId'] == 'thread_reply'


@pytest.mark.unit
class TestArchiveEmails:
    """Tests for the archive_emails function."""

    def test_archive_emails_removes_labels(self, mock_gmail_service):
        """Archiving should call modify with removeLabelIds for each message."""
        from tools.gmail import archive_emails

        ids = ['msg001', 'msg002']
        archive_emails(ids)

        assert mock_gmail_service.users().messages().modify.call_count == 2


@pytest.mark.unit
class TestGetAttachments:
    """Tests for the get_attachments function."""

    def test_get_attachments_downloads_files(self, tmp_path):
        """Attachments should be saved to the specified directory."""
        from tools.gmail import get_attachments

        attachment_data = base64.urlsafe_b64encode(b'PDF file content').decode()

        service = MagicMock()

        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'msg002',
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': 'dGV4dA=='},
                    },
                    {
                        'filename': 'report.pdf',
                        'mimeType': 'application/pdf',
                        'body': {'attachmentId': 'att01', 'size': 1024},
                    },
                ],
            },
        }
        service.users().messages().get.return_value = get_mock

        att_mock = MagicMock()
        att_mock.execute.return_value = {'data': attachment_data, 'size': 1024}
        service.users().messages().attachments().get.return_value = att_mock

        with patch('tools.gmail.get_gmail', return_value=service):
            downloaded = get_attachments('msg002', output_dir=str(tmp_path))

        assert len(downloaded) == 1
        assert Path(downloaded[0]).name == 'report.pdf'
        assert Path(downloaded[0]).exists()


@pytest.mark.unit
class TestTextToHtml:
    """Tests for the _text_to_html helper function."""

    def test_text_to_html_converts_paragraphs(self):
        """Double newlines should become separate <p> tags."""
        from tools.gmail import _text_to_html

        text = "First paragraph.\n\nSecond paragraph."
        result = _text_to_html(text)

        assert '<p' in result
        assert 'First paragraph.' in result
        assert 'Second paragraph.' in result
        # Two paragraphs expected
        assert result.count('<p') == 2


@pytest.mark.unit
class TestExtractBody:
    """Tests for the _extract_body helper function."""

    def test_extract_body_handles_multipart(self):
        """Multipart payload should extract the text/plain part."""
        from tools.gmail import _extract_body

        body_text = 'Hello from a multipart message'
        encoded = base64.urlsafe_b64encode(body_text.encode()).decode()

        payload = {
            'mimeType': 'multipart/alternative',
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': encoded},
                },
                {
                    'mimeType': 'text/html',
                    'body': {'data': base64.urlsafe_b64encode(b'<p>HTML</p>').decode()},
                },
            ],
        }

        result = _extract_body(payload)
        assert result == body_text
