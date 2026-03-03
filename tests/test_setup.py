"""
Tests for setup.py.
Verifies the Python version check logic.
"""

import sys
import pytest
from collections import namedtuple
from unittest.mock import patch, MagicMock


# sys.version_info is a structseq that cannot be instantiated directly.
# We use a namedtuple with the same attribute names as a stand-in.
VersionInfo = namedtuple('version_info', ['major', 'minor', 'micro', 'releaselevel', 'serial'])


def _make_version_info(major, minor, micro):
    """Build a version_info-like object that supports both tuple comparison and attribute access."""
    return VersionInfo(major, minor, micro, 'final', 0)


@pytest.mark.unit
class TestCheckPythonVersion:
    """Tests for the check_python_version function."""

    def test_check_python_version_passes(self):
        """Python 3.10+ should pass the version check without exiting."""
        from setup import check_python_version

        vi = _make_version_info(3, 10, 0)

        with patch('setup.sys') as mock_sys:
            mock_sys.version_info = vi
            mock_sys.version = '3.10.0 (default)'
            mock_sys.exit = MagicMock()

            check_python_version()

            mock_sys.exit.assert_not_called()

    def test_check_python_version_fails_old_python(self):
        """Python older than 3.9 should cause sys.exit(1)."""
        from setup import check_python_version

        vi = _make_version_info(3, 7, 0)

        with patch('setup.sys') as mock_sys:
            mock_sys.version_info = vi
            mock_sys.version = '3.7.0 (default)'
            mock_sys.exit = MagicMock(side_effect=SystemExit(1))

            with pytest.raises(SystemExit):
                check_python_version()

            mock_sys.exit.assert_called_once_with(1)
