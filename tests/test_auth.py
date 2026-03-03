"""
Tests for tools/auth.py.
Verifies credential loading, refresh, re-authentication, and service building.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open


@pytest.mark.unit
class TestGetCredentials:
    """Tests for the get_credentials function."""

    @patch('tools.auth.TOKEN_PATH')
    @patch('tools.auth.Credentials')
    def test_get_credentials_loads_existing_token(self, mock_creds_cls, mock_token_path):
        """Valid, non-expired token file is loaded without triggering any flow."""
        from tools.auth import get_credentials

        mock_token_path.exists.return_value = True

        creds = MagicMock()
        creds.valid = True
        creds.expired = False
        creds.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive.readonly',
        ]
        mock_creds_cls.from_authorized_user_file.return_value = creds

        result = get_credentials()

        mock_creds_cls.from_authorized_user_file.assert_called_once()
        assert result is creds

    @patch('tools.auth.CREDS_DIR')
    @patch('tools.auth.TOKEN_PATH')
    @patch('tools.auth.Request')
    @patch('tools.auth.Credentials')
    def test_get_credentials_refreshes_expired_token(
        self, mock_creds_cls, mock_request_cls, mock_token_path, mock_creds_dir
    ):
        """Expired token with a refresh token should be refreshed, not re-authed."""
        from tools.auth import get_credentials

        mock_token_path.exists.return_value = True

        creds = MagicMock()
        creds.valid = False
        creds.expired = True
        creds.refresh_token = 'refresh-tok'
        creds.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive.readonly',
        ]
        mock_creds_cls.from_authorized_user_file.return_value = creds

        result = get_credentials()

        creds.refresh.assert_called_once()
        assert result is creds

    @patch('tools.auth.CREDS_DIR')
    @patch('tools.auth.TOKEN_PATH')
    @patch('tools.auth.CLIENT_SECRET_PATH')
    @patch('tools.auth.InstalledAppFlow')
    @patch('tools.auth.Credentials')
    def test_get_credentials_triggers_flow_when_no_token(
        self, mock_creds_cls, mock_flow_cls, mock_secret_path,
        mock_token_path, mock_creds_dir
    ):
        """When no token file exists, the browser auth flow should run."""
        from tools.auth import get_credentials

        mock_token_path.exists.return_value = False
        mock_secret_path.exists.return_value = True

        flow_instance = MagicMock()
        new_creds = MagicMock()
        new_creds.to_json.return_value = '{"token": "new"}'
        flow_instance.run_local_server.return_value = new_creds
        mock_flow_cls.from_client_secrets_file.return_value = flow_instance

        result = get_credentials()

        mock_flow_cls.from_client_secrets_file.assert_called_once()
        flow_instance.run_local_server.assert_called_once_with(port=0)
        assert result is new_creds

    @patch('tools.auth.CREDS_DIR')
    @patch('tools.auth.TOKEN_PATH')
    @patch('tools.auth.CLIENT_SECRET_PATH')
    @patch('tools.auth.InstalledAppFlow')
    @patch('tools.auth.Credentials')
    def test_get_credentials_reauths_on_scope_mismatch(
        self, mock_creds_cls, mock_flow_cls, mock_secret_path,
        mock_token_path, mock_creds_dir
    ):
        """When existing token is missing required scopes, re-auth should trigger."""
        from tools.auth import get_credentials

        mock_token_path.exists.return_value = True
        mock_secret_path.exists.return_value = True

        # Existing creds have a subset of scopes
        old_creds = MagicMock()
        old_creds.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        old_creds.valid = True
        mock_creds_cls.from_authorized_user_file.return_value = old_creds

        flow_instance = MagicMock()
        new_creds = MagicMock()
        new_creds.to_json.return_value = '{"token": "new"}'
        flow_instance.run_local_server.return_value = new_creds
        mock_flow_cls.from_client_secrets_file.return_value = flow_instance

        result = get_credentials()

        mock_flow_cls.from_client_secrets_file.assert_called_once()
        assert result is new_creds

    @patch('tools.auth.TOKEN_PATH')
    @patch('tools.auth.CLIENT_SECRET_PATH')
    @patch('tools.auth.Credentials')
    def test_get_credentials_exits_when_no_client_secret(
        self, mock_creds_cls, mock_secret_path, mock_token_path
    ):
        """Missing client_secret.json should cause sys.exit(1)."""
        from tools.auth import get_credentials

        mock_token_path.exists.return_value = False
        mock_secret_path.exists.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            get_credentials()

        assert exc_info.value.code == 1


@pytest.mark.unit
class TestGetService:
    """Tests for the get_service function."""

    @patch('tools.auth.build')
    @patch('tools.auth.get_credentials')
    def test_get_service_returns_api_service(self, mock_get_creds, mock_build):
        """get_service should call build() with the correct API name and version."""
        from tools.auth import get_service

        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds
        mock_build.return_value = MagicMock(name='service')

        result = get_service('gmail', 'v1')

        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        assert result is mock_build.return_value
