"""Tests methods in route module."""

from unittest.mock import patch

import pytest

from aind_metadata_service.backends.smartsheet.models import ProtocolsModel


class TestRoute:
    """Test protocls responses."""

    example_protocol = (
        "Tetrahydrofuran and Dichloromethane Delipidation of a Whole Mouse "
        "Brain"
    )

    def test_get_200(self, client, mock_get_raw_protocols_sheet):
        """Tests a good response"""

        response = client.get(f"/protocols/{self.example_protocol}")
        expected_response = {
            "message": "Valid Model",
            "data": {
                "Protocol Type": "Specimen Procedures",
                "Procedure name": "Delipidation",
                "Protocol name": self.example_protocol,
                "DOI": "dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                "Version": "1.0",
                "Protocol collection": None,
            },
        }

        assert expected_response == response.json()

    def test_get_404(self, client, mock_get_raw_protocols_sheet):
        """Tests a missing data response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler.SessionHandler"
            ".get_protocols_info",
            return_value=[],
        ):
            response = client.get("/protocols/None_Such_Protocol")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(
        self, client, mock_get_raw_protocols_sheet, caplog
    ):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler.SessionHandler"
            ".get_protocols_info",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get(f"/protocols/{self.example_protocol}")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text

    def test_300_multiple_responses(
        self, client, mock_get_raw_protocols_sheet
    ):
        """Tests a multiple_items response"""
        example_model = ProtocolsModel(
            protocol_type="Specimen Procedures",
            procedure_name="Delipidation",
            protocol_name=self.example_protocol,
            doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
            version="1.0",
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model, example_model],
        ):
            response = client.get(f"/protocols/{self.example_protocol}")

        assert 300 == response.status_code

    def test_406_invalid_model(self, client, mock_get_raw_protocols_sheet):
        """Tests an invalid model response"""

        example_model = ProtocolsModel.model_construct(
            protocol_name=self.example_protocol, version="abc"
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model],
        ):
            response = client.get(f"/protocols/{self.example_protocol}")

        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
