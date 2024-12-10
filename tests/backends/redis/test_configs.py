"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service.backends.redis.configs import Settings


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    def test_connection_str(self):
        """Tests connection_str property"""

        settings = Settings(
            host="abc.def",
            port=123,
        )
        expected_conn_string = "redis://abc.def:123"
        self.assertEqual(expected_conn_string, settings.connection_str)

    @patch.dict(
        os.environ,
        {
            "REDIS_HOST": "redis_host",
            "REDIS_PORT": "123",
        },
        clear=True,
    )
    def test_settings(self):
        """Tests settings can be set via env vars"""
        settings = Settings()
        expected_settings = Settings(
            host="redis_host",
            port=123,
        )
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
