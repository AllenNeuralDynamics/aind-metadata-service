"""Tests session module"""

import pytest
from aind_slims_api.core import SlimsClient

from aind_metadata_service.backends.slims.session import get_session


class TestSession:
    """Test methods in Session Class"""

    def test_get_session(self):
        """Tests get_session method"""

        session = next(get_session())
        expected_session = SlimsClient(
            url="http://slims.example.com",
            username="slims_user",
            password="slims_password",
        )
        assert expected_session.url == session.url


if __name__ == "__main__":
    pytest.main([__file__])
