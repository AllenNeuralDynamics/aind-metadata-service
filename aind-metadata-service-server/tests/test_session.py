"""Tests session module"""

import pytest

from aind_metadata_service_server.session import get_session


class TestSession:
    """Test methods in Session Class"""

    def test_get_session(self):
        """Tests get_session method"""

        session = next(get_session())
        base_url = session.base_url
        assert "example" == base_url


if __name__ == "__main__":
    pytest.main([__file__])
