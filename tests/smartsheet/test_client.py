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

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "smartsheet" / "test_sheet.json"


class TestSmartsheetSettings(unittest.TestCase):
    """Class to test methods for SmartsheetSettings."""

    EXAMPLE_ENV_VAR1 = {
        "SMARTSHEET_ACCESS_TOKEN": "abc-123",
        "SMARTSHEET_SHEET_ID": "123456789",
        "SMARTSHEET_MAX_CONNECTIONS": "16",
    }

    @patch.dict(os.environ, EXAMPLE_ENV_VAR1, clear=True)
    def test_settings_set_from_env_vars(self):
        """Tests that the settings can be set from env vars."""

        settings1 = SmartsheetSettings()
        settings2 = SmartsheetSettings(user_agent="Agent0", max_connections=8)
        self.assertEqual("abc-123", settings1.access_token.get_secret_value())
        self.assertEqual(123456789, settings1.sheet_id)
        self.assertTrue("AIND_Metadata_Service" in settings1.user_agent)
        self.assertEqual(16, settings1.max_connections)
        self.assertEqual("abc-123", settings2.access_token.get_secret_value())
        self.assertEqual(123456789, settings2.sheet_id)
        self.assertEqual("Agent0", settings2.user_agent)
        self.assertEqual(8, settings2.max_connections)


class TestSmartsheetClient(unittest.IsolatedAsyncioTestCase):
    """Class to test methods for SmartsheetClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            contents = json.load(f)
        cls.example_sheet = json.dumps(contents)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_sheet_success(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        sheet_response = client.get_sheet()
        sheet_str = json.loads(sheet_response.body)["data"]
        sheet = json.loads(sheet_str)
        self.assertEqual("Published Protocols", sheet["name"])
        self.assertEqual(7478444220698500, sheet["id"])
        self.assertEqual(6, sheet["version"])
        self.assertEqual(7, sheet["totalRowCount"])

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch("logging.error")
    def test_get_sheet_error(
        self, mock_log_error: MagicMock, mock_get_sheet: MagicMock
    ):
        """Tests sheet return error response"""
        mock_get_sheet.side_effect = MagicMock(
            side_effect=Exception("Error connecting to server")
        )
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        response = client.get_sheet()
        self.assertEqual(500, response.status_code)
        self.assertEqual(
            "Error connecting to server", json.loads(response.body)["message"]
        )
        mock_log_error.assert_called_once_with(
            "Exception('Error connecting to server',)"
        )


if __name__ == "__main__":
    unittest.main()
