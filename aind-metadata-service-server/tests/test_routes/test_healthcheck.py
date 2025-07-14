"""Test healthcheck routes"""

import pytest
from fastapi.testclient import TestClient


class TestRoute:
    """Test healthcheck responses."""

    def test_get_health(self, client: TestClient):
        """Tests a good response"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]


if __name__ == "__main__":
    pytest.main([__file__])
