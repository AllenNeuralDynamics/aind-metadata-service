"""Tests methods in smartsheet perfusions module"""

import json
import os
import unittest
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from aind_data_schema.core.procedures import Perfusion, Surgery
from aind_data_schema_models.units import MassUnit

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.perfusions.mapping import (
    PerfusionsMapper,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = (
    TEST_DIR / "resources" / "smartsheet" / "test_perfusions_sheet.json"
)


class TestSmartsheetPerfusionsClient(unittest.TestCase):
    """Class to test methods for SmartsheetClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            contents = json.load(f)
        cls.example_sheet_contents = contents
        cls.example_sheet = json.dumps(contents)
        # TODO: Add protocol id
        cls.expected_model = [
            Surgery.model_construct(
                start_date=date(2023, 10, 2),
                experimenter_full_name="Jane Smith",
                iacuc_protocol="2109",
                animal_weight_prior=Decimal("22.0"),
                animal_weight_post=None,
                weight_unit=MassUnit.G,
                anaesthesia=None,
                notes=None,
                procedures=[
                    Perfusion(
                        output_specimen_ids={"689418"},
                        protocol_id=(
                            "dx.doi.org/10.17504/protocols.io.bg5vjy66"
                        ),
                    )
                ],
            )
        ]

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        expected_models = self.expected_model
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_empty_response(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = None
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        expected_models = []
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.NO_DATA_FOUND, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch("logging.error")
    def test_mapping_server_error(
        self, mock_log_error: MagicMock, mock_get_sheet: MagicMock
    ):
        """Tests server error"""

        def mock_get_sheet_error(_):
            """Mock the get_sheet so that it returns an error."""
            raise Exception("Something went wrong")

        type(mock_get_sheet.return_value).to_json = mock_get_sheet_error
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        self.assertEqual(
            ModelResponse.internal_server_error_response().status_code,
            model_response.status_code,
        )
        mock_log_error.assert_has_calls(
            [
                call("Exception('Something went wrong',)"),
            ]
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch(
        "aind_metadata_service.smartsheet.perfusions.mapping.PerfusionsMapper"
        "._get_perfusion_list"
    )
    @patch("logging.error")
    def test_mapping_error(
        self,
        mock_log_error: MagicMock,
        mock_get_perfusions_list: MagicMock,
        mock_get_sheet: MagicMock,
    ):
        """Tests mapping error"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        mock_get_perfusions_list.side_effect = MagicMock(
            side_effect=Exception("Mapping Error")
        )
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        expected_models = []
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, model_response.status_code
        )
        mock_log_error.assert_has_calls(
            [
                call("Exception('Mapping Error')"),
            ]
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_missing_iacuc_id(self, mock_get_sheet: MagicMock):
        """Tests response when iacuc field is missing"""

        # Make the iacuc id field blank
        mock_sheet_contents = deepcopy(self.example_sheet_contents)
        mock_sheet_contents["rows"][0]["cells"][3]["displayValue"] = None
        mock_sheet_contents["rows"][0]["cells"][3]["value"] = None
        mock_sheet = json.dumps(mock_sheet_contents)

        mock_get_sheet.return_value.to_json.return_value = mock_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        self.assertIsNone(model_response.aind_models[0].iacuc_protocol)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_malformed_iacuc_id(self, mock_get_sheet: MagicMock):
        """Tests sheet return response when the iacuc field is malformed"""

        # Make the iacuc id field malformed (we expect it to be number - text)
        mock_sheet_contents = deepcopy(self.example_sheet_contents)
        mock_sheet_contents["rows"][0]["cells"][3]["displayValue"] = "abc"
        mock_sheet_contents["rows"][0]["cells"][3]["value"] = "abc"
        mock_sheet = json.dumps(mock_sheet_contents)

        mock_get_sheet.return_value.to_json.return_value = mock_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        self.assertEqual("abc", model_response.aind_models[0].iacuc_protocol)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_malformed_date(self, mock_get_sheet: MagicMock):
        """Tests response when date field is malformed"""

        # Make the iacuc id field malformed (we expect it to be number - text)
        mock_sheet_contents = deepcopy(self.example_sheet_contents)
        mock_sheet_contents["rows"][0]["cells"][1]["value"] = "12/21/2021"
        mock_sheet = json.dumps(mock_sheet_contents)

        mock_get_sheet.return_value.to_json.return_value = mock_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="689418"
        )
        model_response = mapper.get_model_response()
        self.assertEqual(
            "12/21/2021", model_response.aind_models[0].start_date
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_no_data_found(self, mock_get_sheet: MagicMock):
        """Tests response no data for the subject id is discovered"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = PerfusionsMapper(
            smart_sheet_response=smart_sheet_response, input_id="4"
        )
        model_response = mapper.get_model_response()
        self.assertEqual([], model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)


if __name__ == "__main__":
    unittest.main()
