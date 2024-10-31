"""Tests methods in route module."""

from unittest.mock import patch

import pytest

from aind_metadata_service.backends.smartsheet.models import PerfusionsModel


class TestRoute:
    """Test perfusions responses."""

    def test_get_200(self, client, mock_get_raw_perfusions_sheet):
        """Tests a good response"""

        response = client.get("/perfusions/689418")
        print(response.json())
        expected_response = {
            "message": "Valid Model",
            "data": {
                "procedure_type": "Surgery",
                "protocol_id": "dx.doi.org/10.17504/protocols.io.bg5vjy66",
                "start_date": "2023-10-02",
                "experimenter_full_name": "Jane Smith",
                "iacuc_protocol": "2109",
                "animal_weight_prior": "22.0",
                "animal_weight_post": None,
                "weight_unit": "gram",
                "anaesthesia": None,
                "workstation_id": None,
                "procedures": [
                    {
                        "procedure_type": "Perfusion",
                        "protocol_id": (
                            "dx.doi.org/10.17504/protocols.io.bg5vjy66"
                        ),
                        "output_specimen_ids": ["689418"],
                    }
                ],
                "notes": None,
            },
        }
        assert expected_response == response.json()

    def test_get_404(self, client, mock_get_raw_perfusions_sheet):
        """Tests a missing data response"""

        response = client.get("/perfusions/1")
        expected_response = {"message": "No Data Found", "data": None}
        assert 404 == response.status_code
        assert expected_response == response.json()

    def test_500_internal_server_error(self, client, caplog):
        """Tests an internal server error response"""

        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            side_effect=Exception("Something went wrong"),
        ):
            response = client.get("/perfusions/689418")

        expected_response = {"message": "Internal Server Error", "data": None}
        assert 500 == response.status_code
        assert expected_response == response.json()
        assert "An error occurred: ('Something went wrong',)" in caplog.text

    def test_300_multiple_responses(
        self, client, mock_get_raw_perfusions_sheet
    ):
        """Tests a multiple_items response"""
        example_iacuc_protocol = (
            "2109 - Analysis of brain - wide neural circuits in the mouse"
        )
        example_model = PerfusionsModel(
            subject_id="689418",
            date="2023-10-02",
            experimenter="Person One",
            iacuc_protocol=example_iacuc_protocol,
            animal_weight_prior="22",
            output_specimen_id="689418",
            postfix_solution="1xPBS",
            notes="Good",
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model, example_model],
        ):
            response = client.get("/perfusions/689418")

        assert 300 == response.status_code

    def test_406_invalid_model(self, client, mock_get_raw_perfusions_sheet):
        """Tests an invalid model response"""

        example_model = PerfusionsModel(
            subject_id="689418",
            experimenter="Person One",
            animal_weight_prior="22",
            output_specimen_id="689418",
            postfix_solution="1xPBS",
            notes="Good",
        )
        with patch(
            "aind_metadata_service.backends.smartsheet.handler"
            ".SessionHandler.get_parsed_sheet",
            return_value=[example_model],
        ):
            response = client.get("/perfusions/689418")

        assert 406 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
