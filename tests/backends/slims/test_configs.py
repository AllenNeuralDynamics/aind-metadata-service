"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service.backends.slims.configs import Settings, get_settings


class TestConfigs(unittest.TestCase):
    """Test methods in Configs Class"""

    @patch.dict(
        os.environ,
        {
            "SLIMS_URL": "http://slims.example.com",
            "SLIMS_USERNAME": "slims_user",
            "SLIMS_PASSWORD": "slims_password",
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = get_settings()
        expected_settings = Settings(
            url="http://slims.example.com",
            username="slims_user",
            password="slims_password",
        )
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
