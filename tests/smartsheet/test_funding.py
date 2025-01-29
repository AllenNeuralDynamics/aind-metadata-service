"""Module to test Smartsheet client class"""

import json
import os
import unittest
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from aind_data_schema_models.organizations import Organization
from dateutil import tz

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import FundingInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.funding.mapping import FundingMapper
from aind_metadata_service.smartsheet.models import SheetFields, SheetRow

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = (
    TEST_DIR / "resources" / "smartsheet" / "test_funding_sheet.json"
)
EXAMPLE_PATH_2 = (
    TEST_DIR / "resources" / "smartsheet" / "test_corrupt_funding_sheet.json"
)


class TestSmartsheetFundingClient(unittest.TestCase):
    """Class to test methods for SmartsheetClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            contents = json.load(f)
        with open(EXAMPLE_PATH_2, "r") as f:
            contents2 = json.load(f)
        cls.example_sheet = json.dumps(contents)
        cls.example_corrupt_sheet = json.dumps(contents2)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response,
            input_id=(
                "Discovery-Neuromodulator circuit dynamics during foraging - "
                "Subproject 2 Molecular Anatomy Cell Types"
            ),
        )
        model_response = mapper.get_model_response()
        expected_models = [
            FundingInformation(
                funder=Organization.AI,
                grant_number=None,
                fundee=(
                    "Person Four, Person Five, Person Six, Person Seven, "
                    "Person Eight"
                ),
                investigators="Person Seven",
            ),
            FundingInformation(
                funder=Organization.NIMH,
                grant_number="1R01MH134833",
                fundee=(
                    "Person Five, Person Nine, Person Ten, Person Seven, "
                    "Person Eleven"
                ),
                investigators="Person Seven",
            ),
        ]
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_empty_response(self, mock_get_sheet: MagicMock):
        """Tests empty response when no project name found"""
        mock_get_sheet.return_value.to_json.return_value = None
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response, input_id="NONE"
        )
        model_response = mapper.get_model_response()
        expected_models = []
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.NO_DATA_FOUND, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_empty_response_info(self, mock_get_sheet: MagicMock):
        """Tests empty response when no info found for project name"""

        mock_get_sheet.return_value.to_json.return_value = (
            self.example_corrupt_sheet
        )
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response, input_id="Some Project"
        )
        model_response = mapper.get_model_response()
        expected_models = []
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_invalid_institution(self, mock_get_sheet: MagicMock):
        """Tests situation where the institute name isn't in
        aind-data-schema"""
        incorrect_sheet = deepcopy(self.example_sheet).replace(
            "Allen Institute", "Some Institute"
        )

        mock_get_sheet.return_value.to_json.return_value = incorrect_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response,
            input_id="Ephys Platform",
        )
        model_response = mapper.get_model_response()
        expected_models = [
            FundingInformation.model_construct(
                funder="Some Institute",
                grant_number=None,
                fundee="Person One, Person Two, Person Three",
                investigators=None,
            )
        ]
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

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
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response, input_id="Project Name"
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
        "aind_metadata_service.smartsheet.funding.mapping.FundingMapper"
        "._get_funding_list"
    )
    @patch("logging.error")
    def test_mapping_error(
        self,
        mock_log_error: MagicMock,
        mock_get_funding_list: MagicMock,
        mock_get_sheet: MagicMock,
    ):
        """Tests mapping error"""

        mock_get_funding_list.side_effect = MagicMock(
            side_effect=Exception("Mapping Error")
        )
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response, input_id="122-01-001-10"
        )
        model_response = mapper.get_model_response()
        self.assertEqual(
            ModelResponse.internal_server_error_response().status_code,
            model_response.status_code,
        )
        mock_log_error.assert_has_calls(
            [
                call("Exception('Mapping Error')"),
            ]
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_project_names_success(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response of project names"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response,
            input_id="",
        )
        json_response = mapper.get_project_names()
        expected_response = {
            "message": "Success",
            "data": [
                "Discovery-Neuromodulator circuit dynamics during " "foraging",
                (
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                    " - Subproject 1 Electrophysiological Recordings from NM "
                    "Neurons During Behavior"
                ),
                (
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                    " - Subproject 2 Molecular Anatomy Cell Types"
                ),
                (
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                    " - Subproject 3 Fiber Photometry Recordings of NM Release"
                    " During Behavior"
                ),
                "Ephys Platform",
                "MSMA Platform",
            ],
        }
        self.assertEqual(
            expected_response, json.loads(json_response.body.decode("utf-8"))
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch("logging.error")
    def test_get_project_names_failure(
        self, mock_log_error: MagicMock, mock_get_sheet: MagicMock
    ):
        """Tests failure of sheet return response of project names"""

        def mock_get_sheet_error(_):
            """Mock the get_sheet so that it returns an error."""
            raise Exception("Something went wrong")

        type(mock_get_sheet.return_value).to_json = mock_get_sheet_error
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=6011951083638660
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = FundingMapper(
            smart_sheet_response=smart_sheet_response,
            input_id="",
        )
        json_response = mapper.get_project_names()
        self.assertEqual(500, json_response.status_code)
        mock_log_error.assert_has_calls(
            [
                call("Exception('Something went wrong',)"),
            ]
        )


class TestFundingModels(unittest.TestCase):
    """Test methods in models package"""

    def test_funding_row_datetime_parsing(self):
        """Tests that datetime strings are being parsed correctly"""

        funding_row = SheetRow(
            cells=[],
            createdAt=datetime(2020, 10, 10, 10, 10, 10, tzinfo=tz.UTC),
            expanded=True,
            id=1,
            modifiedAt=datetime(2020, 10, 10, 10, 10, 10, tzinfo=tz.UTC),
            rowNumber=1,
        )
        funding_row_string0 = SheetRow(
            cells=[],
            createdAt="2020-10-10T10:10:10+00:00Z",
            expanded=True,
            id=1,
            modifiedAt="2020-10-10T10:10:10+00:00Z",
            rowNumber=1,
        )
        funding_row_string1 = SheetRow(
            cells=[],
            createdAt="2020-10-10T10:10:10+00:00",
            expanded=True,
            id=1,
            modifiedAt="2020-10-10T10:10:10+00:00",
            rowNumber=1,
        )
        self.assertEqual(funding_row, funding_row_string0)
        self.assertEqual(funding_row_string0, funding_row_string1)

    def test_funding_sheet_datetime_parsing(self):
        """Tests that datetime strings are being parsed correctly"""

        funding_sheet = SheetFields(
            columns=[],
            accessLevel="",
            createdAt=datetime(2020, 10, 10, 10, 10, 10, tzinfo=tz.UTC),
            dependenciesEnabled=True,
            effectiveAttachmentOptions=[],
            ganttEnabled=False,
            hasSummaryFields=True,
            id=0,
            modifiedAt=datetime(2020, 10, 10, 10, 10, 10, tzinfo=tz.UTC),
            name="abc",
            permalink="permalink.url",
            readOnly=False,
            resourceManagementEnabled=False,
            rows=[],
            totalRowCount=40,
            userPermissions={},
            userSettings={},
            version=2,
            workspace={},
        )
        funding_sheet_string0 = SheetFields(
            columns=[],
            accessLevel="",
            createdAt="2020-10-10T10:10:10+00:00Z",
            dependenciesEnabled=True,
            effectiveAttachmentOptions=[],
            ganttEnabled=False,
            hasSummaryFields=True,
            id=0,
            modifiedAt="2020-10-10T10:10:10+00:00Z",
            name="abc",
            permalink="permalink.url",
            readOnly=False,
            resourceManagementEnabled=False,
            rows=[],
            totalRowCount=40,
            userPermissions={},
            userSettings={},
            version=2,
            workspace={},
        )
        funding_sheet_string1 = SheetFields(
            columns=[],
            accessLevel="",
            createdAt="2020-10-10T10:10:10+00:00",
            dependenciesEnabled=True,
            effectiveAttachmentOptions=[],
            ganttEnabled=False,
            hasSummaryFields=True,
            id=0,
            modifiedAt="2020-10-10T10:10:10+00:00",
            name="abc",
            permalink="permalink.url",
            readOnly=False,
            resourceManagementEnabled=False,
            rows=[],
            totalRowCount=40,
            userPermissions={},
            userSettings={},
            version=2,
            workspace={},
        )
        self.assertEqual(funding_sheet, funding_sheet_string0)
        self.assertEqual(funding_sheet_string0, funding_sheet_string1)


if __name__ == "__main__":
    unittest.main()
