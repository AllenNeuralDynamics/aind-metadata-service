"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service_server.configs import Settings


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    @patch.dict(os.environ, {"MYENV_HOST": "example"}, clear=True)
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = Settings()
        expected_settings = Settings(host="example")
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
