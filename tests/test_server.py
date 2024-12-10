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
        self, client, get_lab_tracks_session, example_200_subject_response
    ):
        """Tests subject"""
        response = client.get("/subject/632269")
        assert 200 == response.status_code
        assert example_200_subject_response == response.json()

    def test_get_funding(self, client, mock_get_raw_funding_sheet):
        """Tests funding"""
        response = client.get("/funding/v1omFISH")
        assert 200 == response.status_code

    def test_get_project_names(self, client, mock_get_raw_funding_sheet):
        """Tests project_names"""
        response = client.get("/project_names")
        assert 200 == response.status_code

    def test_get_protocols(self, client, mock_get_raw_protocols_sheet):
        """Tests protocols"""
        example_protocol = (
            "Tetrahydrofuran and Dichloromethane Delipidation of a Whole "
            "Mouse Brain"
        )
        response = client.get(f"/protocols/{example_protocol}")
        assert 200 == response.status_code

    def test_get_perfusions(self, client, mock_get_raw_perfusions_sheet):
        """Tests perfusions"""
        response = client.get("/perfusions/689418")
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
