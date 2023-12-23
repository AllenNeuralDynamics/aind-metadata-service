"""Module to test Smartsheet client class"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.funding.mapping import FundingMapper

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "smartsheet" / "test_funding_sheet.json"


class TestSmartsheetClient(unittest.IsolatedAsyncioTestCase):
    """Class to test methods for SmartsheetClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            contents = json.load(f)
        cls.example_sheet = json.dumps(contents)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        sheet_str = client.get_sheet()
        mapper = FundingMapper(sheet_contents=sheet_str)
        model_response = mapper.get_model_response(project_code="122-01-001-10")


if __name__ == "__main__":
    unittest.main()
