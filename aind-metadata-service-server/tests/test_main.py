"""Module to test main app"""

import pytest


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code

    def test_get_length(self, client, mock_get_example_response):
        """Tests content route length"""
        response = client.get("/length")
        expected_json = {"info": "1244", "arg": "length"}
        assert expected_json == response.json()
        assert 200 == response.status_code

    def test_get_raw(self, client, mock_get_example_response):
        """Tests content route length"""
        response = client.get("/raw")
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
