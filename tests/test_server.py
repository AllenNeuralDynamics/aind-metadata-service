"""Module to test server endpoints"""

import pytest


class TestServer:
    """Tests server endpoints."""

    def test_get_healthcheck(self, client):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]

    def test_get_favicon(self, client):
        """Tests favicon"""
        response = client.get("/favicon.ico", follow_redirects=False)
        assert 200 == response.status_code

    def test_get_subject(
        self, client, get_session, example_200_subject_response
    ):
        """Tests subject"""
        response = client.get("/subject/632269")
        assert 200 == response.status_code
        assert example_200_subject_response == response.json()


if __name__ == "__main__":
    pytest.main([__file__])
