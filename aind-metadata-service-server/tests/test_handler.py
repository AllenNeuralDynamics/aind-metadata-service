"""Tests for handler module"""

import pytest

from aind_metadata_service_server.handler import SessionHandler


class TestHandler:
    """Test SessionHandler"""

    def test_constructor(self, get_test_session):
        """Tests class can be constructed."""
        session_handler = SessionHandler(get_test_session)
        assert session_handler is not None


if __name__ == "__main__":
    pytest.main([__file__])
