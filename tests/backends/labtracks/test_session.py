"""Tests session module"""

import pytest

from aind_metadata_service.backends.labtracks.session import get_session


class TestSession:
    """Test methods in Session Class"""

    def test_get_session(self):
        """Tests get_session method"""

        session = next(get_session())
        bind_url = str(session.get_bind().url)
        session.close()
        expected_bind_url = (
            "mssql+pyodbc://lb_user:***@lb_host:123/"
            "lb_db?driver=FreeTDS&tds_version=8.0"
        )
        assert expected_bind_url == bind_url


if __name__ == "__main__":
    pytest.main([__file__])
