"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service_server.configs import Settings, get_settings


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    @patch.dict(
        os.environ,
        {
            "AIND_METADATA_SERVICE_LABTRACKS_HOST": (
                "http://example.com/labtracks"
            ),
            "AIND_METADATA_SERVICE_MGI_HOST": ("http://example.com/mgi"),
            "AIND_METADATA_SERVICE_SMARTSHEET_HOST": (
                "http://example.com/smartsheet"
            ),
            "AIND_METADATA_SERVICE_SLIMS_HOST": "http://example.com/slims",
            "AIND_METADATA_SERVICE_SHAREPOINT_HOST": (
                "http://example.com/sharepoint"
            ),
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = get_settings()
        expected_settings = Settings(
            labtracks_host="http://example.com/labtracks",
            mgi_host="http://example.com/mgi",
            smartsheet_host="http://example.com/smartsheet",
            slims_host="http://example.com/slims",
            sharepoint_host="http://example.com/sharepoint",
        )
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
