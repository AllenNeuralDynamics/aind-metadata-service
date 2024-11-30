"""Tests methods in session module"""

import unittest
from unittest.mock import patch, MagicMock

from aind_metadata_service.backends.tars.session import get_session


class TestSession(unittest.TestCase):
    """Test methods in session module"""

    @patch("requests.Session")
    def test_get_session(self, mock_requests_session: MagicMock):
        """Tests get_session method"""
        _ = next(get_session())

        mock_requests_session.assert_called_once()


if __name__ == "__main__":
    unittest.main()
