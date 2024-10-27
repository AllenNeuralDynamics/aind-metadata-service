"""Tests methods in route module."""

from unittest.mock import patch

import pytest

from aind_metadata_service.backends.smartsheet.models import FundingModel


class TestRoute:
    """Test funding responses."""

    def test_get_200_funding(self, client, mock_get_raw_funding_sheet):
        """Tests a good response"""

        response = client.get("/funding/v1omFISH")
        expected_response = {
            "message": "Valid Model",
            "data": {
                "funder": {
                    "name": "Allen Institute",
                    "abbreviation": "AI",
                    "registry": {
                        "name": "Research Organization Registry",
                        "abbreviation": "ROR",
                    },
                    "registry_identifier": "03cpe7c52",
                },
                "grant_number": None,
                "fundee": "person.one@acme.org, Jane Doe",
            },
        }
        assert expected_response == response.json()

    def test_get_404_funding(self, client, mock_get_raw_funding_sheet):
        """Tests a missing data response"""

        response = client.get("/funding/missing_project")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(
        self, client, get_lab_tracks_session, caplog
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/funding/v1omFISH")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text

    def test_300_multiple_responses(self, client, mock_get_raw_funding_sheet):
        """Tests a multiple_items response"""
        example_model = FundingModel(
            project_name="v1omFISH",
            project_code="121-01-010-10",
            funding_institution="Allen Institute",
            investigators="person.one@acme.org, Jane Doe",
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model, example_model],
        ):
            response = client.get("/funding/v1omFISH")

        assert 300 == response.status_code

    def test_406_invalid_model(self, client, mock_get_raw_funding_sheet):
        """Tests an invalid model response"""

        example_model = FundingModel(
            project_name="v1omFISH",
            project_code="121-01-010-10",
            funding_institution="Nonesuch org",
            investigators="person.one@acme.org, Jane Doe",
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model],
        ):
            response = client.get("/funding/v1omFISH")

        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
