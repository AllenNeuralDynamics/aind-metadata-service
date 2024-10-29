"""Tests methods in route module."""

from unittest.mock import patch

import pytest


class TestRoute:
    """Test funding responses."""

    def test_get_200(self, client, mock_get_raw_funding_sheet):
        """Tests a good response"""

        response = client.get("/project_names")
        expected_response = {
            "message": "Success",
            "data": ["AIND Scientific Activities", "v1omFISH"],
        }
        assert expected_response == response.json()

    def test_get_404(self, client, mock_get_raw_funding_sheet):
        """Tests a missing data response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler.SessionHandler"
            ".get_project_names",
            return_value=[],
        ):
            response = client.get("/project_names")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(
        self, client, mock_get_raw_funding_sheet, caplog
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler.SessionHandler"
            ".get_project_names",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/project_names")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])
