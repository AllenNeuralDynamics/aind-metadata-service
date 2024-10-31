"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service.backends.smartsheet.configs import (
    SmartsheetAppConfigs,
    SmartsheetSettings,
    get_settings,
)


class TestConfigs(unittest.TestCase):
    """Test methods in Configs Class"""

    @patch.dict(
        os.environ,
        {
            "SMARTSHEET_FUNDING_ID": "1000",
            "SMARTSHEET_PERFUSIONS_ID": "1001",
            "SMARTSHEET_PROTOCOLS_ID": "1002",
            "SMARTSHEET_ACCESS_TOKEN": "abc-123",
            "SMARTSHEET_USER_AGENT": "some_user_agent",
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = get_settings()
        expected_settings = SmartsheetAppConfigs(
            client_settings=SmartsheetSettings(
                access_token="abc-123", user_agent="some_user_agent"
            ),
            funding_id=1000,
            perfusions_id=1001,
            protocols_id=1002,
        )
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
