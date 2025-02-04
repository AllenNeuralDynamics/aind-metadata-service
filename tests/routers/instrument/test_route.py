"""Tests methods in route module."""

from unittest.mock import patch

import pytest


class TestRoute:
    """Test instrument responses."""

    def test_get_200(self, client):
        """Tests a good response"""

        with patch(
            "aind_metadata_service.backends.slims.handler.SessionHandler"
            ".get_instrument_attachment",
            return_value={"key": "value"},
        ):
            response = client.get("/instrument/some_id")
        expected_response = {
            "message": "Success",
            "data": {"key": "value"},
        }
        assert expected_response == response.json()

    def test_get_404(self, client):
        """Tests a missing data response"""

        with patch(
            "aind_metadata_service.backends.slims.handler.SessionHandler"
            ".get_instrument_attachment",
            return_value=None,
        ):
            response = client.get("/instrument/some_id")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(
        self, client, caplog
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.slims.handler.SessionHandler"
            ".get_instrument_attachment",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/instrument/some_id")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "Something went wrong" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])
