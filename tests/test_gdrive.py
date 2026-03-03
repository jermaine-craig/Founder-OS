"""
Tests for tools/gdrive.py.
All Google API calls are mocked via the mock_drive_service fixture.
"""

import io
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock


@pytest.mark.unit
class TestListFiles:
    """Tests for the list_files function."""

    def test_list_files_returns_results(self, mock_drive_service):
        """list_files should return a list of file metadata dicts."""
        from tools.gdrive import list_files

        files = list_files(max_results=10)

        assert len(files) == 3
        assert files[0]['name'] == 'Q1 Strategy Document'
        assert files[1]['name'] == 'Contract_v2.pdf'
        assert files[2]['name'] == 'Budget Tracker 2026'

    def test_list_files_with_folder_filter(self, mock_drive_service):
        """When folder_id is provided, the query should include a parent filter."""
        from tools.gdrive import list_files

        list_files(folder_id='folder123')

        call_kwargs = mock_drive_service.files().list.call_args
        query = call_kwargs[1].get('q', '')
        assert "'folder123' in parents" in query

    def test_list_files_empty_results(self):
        """When Drive returns no files, list_files should return an empty list."""
        from tools.gdrive import list_files

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {'files': []}
        service.files().list.return_value = list_mock

        with patch('tools.gdrive.get_drive', return_value=service):
            result = list_files()

        assert result == []


@pytest.mark.unit
class TestSearchFiles:
    """Tests for the search_files function."""

    def test_search_files_constructs_query(self, mock_drive_service):
        """The search query should contain the user's search text."""
        from tools.gdrive import search_files

        search_files('budget report', max_results=5)

        call_kwargs = mock_drive_service.files().list.call_args
        query = call_kwargs[1].get('q', '')
        assert 'budget report' in query
        assert 'trashed = false' in query


@pytest.mark.unit
class TestReadFile:
    """Tests for the read_file function."""

    def test_read_file_exports_google_doc(self, mock_drive_service):
        """Google Docs should be exported as plain text."""
        from tools.gdrive import read_file

        # Override get() to return a Google Doc
        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'doc001',
            'name': 'Strategy Doc',
            'mimeType': 'application/vnd.google-apps.document',
        }
        mock_drive_service.files().get.return_value = get_mock

        export_mock = MagicMock()
        export_mock.execute.return_value = b'This is the document content.'
        mock_drive_service.files().export.return_value = export_mock

        result = read_file('doc001')

        assert result == 'This is the document content.'
        mock_drive_service.files().export.assert_called_once()

    def test_read_file_downloads_binary(self, mock_drive_service, tmp_path):
        """Non-Google files should be downloaded as binary."""
        from tools.gdrive import read_file

        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'pdf001',
            'name': 'Contract.pdf',
            'mimeType': 'application/pdf',
            'size': '1024',
        }
        mock_drive_service.files().get.return_value = get_mock

        # Mock the binary download path
        with patch('tools.gdrive._download_binary', return_value=str(tmp_path / 'Contract.pdf')) as dl_mock:
            result = read_file('pdf001')

        dl_mock.assert_called_once()
        assert 'Contract.pdf' in result


@pytest.mark.unit
class TestDownloadFile:
    """Tests for the download_file function."""

    def test_download_file_saves_to_directory(self, mock_drive_service, tmp_path):
        """Downloaded files should be saved to the specified directory."""
        from tools.gdrive import download_file

        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'pdf001',
            'name': 'Contract.pdf',
            'mimeType': 'application/pdf',
        }
        mock_drive_service.files().get.return_value = get_mock

        with patch('tools.gdrive._download_binary', return_value=str(tmp_path / 'Contract.pdf')):
            result = download_file('pdf001', output_dir=str(tmp_path))

        assert 'Contract.pdf' in result


@pytest.mark.unit
class TestGetFileInfo:
    """Tests for the get_file_info function."""

    def test_get_file_info_returns_metadata(self, mock_drive_service):
        """get_file_info should return the full metadata dict from the API."""
        from tools.gdrive import get_file_info

        get_mock = MagicMock()
        get_mock.execute.return_value = {
            'id': 'doc001',
            'name': 'Q1 Strategy Document',
            'mimeType': 'application/vnd.google-apps.document',
            'modifiedTime': '2026-03-02T14:30:00.000Z',
            'webViewLink': 'https://docs.google.com/document/d/doc001/edit',
        }
        mock_drive_service.files().get.return_value = get_mock

        metadata = get_file_info('doc001')

        assert metadata['name'] == 'Q1 Strategy Document'
        assert metadata['id'] == 'doc001'
        assert 'mimeType' in metadata


@pytest.mark.unit
class TestFormatSize:
    """Tests for the _format_size helper function."""

    def test_format_size_various_values(self):
        """File sizes should be formatted with appropriate units."""
        from tools.gdrive import _format_size

        # Zero bytes
        assert _format_size(0) == ''

        # Bytes
        assert _format_size(500) == '500 B'

        # Kilobytes
        result_kb = _format_size(2048)
        assert 'KB' in result_kb

        # Megabytes
        result_mb = _format_size(5 * 1024 * 1024)
        assert 'MB' in result_mb

        # Gigabytes
        result_gb = _format_size(3 * 1024 * 1024 * 1024)
        assert 'GB' in result_gb
