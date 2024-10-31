"""Test subject routes"""

from unittest.mock import patch

import pytest

from aind_metadata_service.backends.labtracks.models import (
    Subject as LabTracksSubject,
)


class TestRoute:
    """Test subject responses."""

    def test_get_200_subject(
        self, client, get_lab_tracks_session, example_200_subject_response
    ):
        """Tests a good response"""
        response = client.get("/subject/632269")
        assert 200 == response.status_code
        assert example_200_subject_response == response.json()

    def test_get_404_subject(
        self,
        client,
        get_lab_tracks_session,
    ):
        """Tests a missing data response"""

        response = client.get("/subject/0")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(
        self, client, get_lab_tracks_session, caplog
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.labtracks.handler"
            ".SessionHandler.get_subject_view",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/subject/1234")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text

    def test_300_multiple_responses(
        self,
        client,
        test_lab_tracks_subject,
        get_lab_tracks_session,
        example_200_subject_response,
    ):
        """Tests a multiple_items response"""

        with patch(
            "aind_metadata_service.backends.labtracks.handler"
            ".SessionHandler.get_subject_view",
            return_value=[test_lab_tracks_subject, test_lab_tracks_subject],
        ):
            response = client.get("/subject/1234")
        expected_responses_data_item = example_200_subject_response["data"]
        expected_responses_data = [
            expected_responses_data_item,
            expected_responses_data_item,
        ]
        expected_response = {
            "message": "Multiple Items Found",
            "data": expected_responses_data,
        }

        assert 300 == response.status_code
        assert expected_response == response.json()

    def test_406_invalid_model(
        self,
        client,
        get_lab_tracks_session,
    ):
        """Tests an invalid model response"""

        with patch(
            "aind_metadata_service.backends.labtracks.handler"
            ".SessionHandler.get_subject_view",
            return_value=[LabTracksSubject(id="1234")],
        ):
            response = client.get("/subject/1234")

        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
