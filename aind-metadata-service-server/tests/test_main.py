"""Module to test main app"""

import pytest


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
