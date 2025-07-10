"""Test routes"""

import pytest


class TestHealthcheckRoute:
    """Test healthcheck responses."""

    def test_get_health(self, client):
        """Tests a good response"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]


class TestContentRoute:
    """Test responses."""

    def test_get_200_response(self, client, mock_get_example_response):
        """Tests a good response"""
        response = client.get("/length")
        assert 200 == response.status_code

    def test_get_404_response(self, client, mock_get_empty_response):
        """Tests an empty response"""

        response = client.get("/raw")
        assert 404 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
