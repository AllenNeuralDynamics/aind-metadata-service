"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service.backends.labtracks.configs import (
    Settings,
    get_settings,
)


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    def test_db_connection_str(self):
        """Tests db_connection_str property"""

        settings = Settings(
            host="abc.def",
            port=123,
            user="user",
            password="fake_password",
            database="my_db",
        )
        expected_conn_string = (
            "mssql+pyodbc://user:fake_password@abc.def:123/"
            "my_db?driver=FreeTDS&tds_version=8.0"
        )
        self.assertEqual(expected_conn_string, settings.db_connection_str)

    @patch.dict(
        os.environ,
        {
            "LABTRACKS_HOST": "lb_host",
            "LABTRACKS_PORT": "123",
            "LABTRACKS_DATABASE": "lb_db",
            "LABTRACKS_USER": "lb_user",
            "LABTRACKS_PASSWORD": "lb_password",
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = get_settings()
        expected_settings = Settings(
            host="lb_host",
            port=123,
            database="lb_db",
            user="lb_user",
            password="lb_password",
        )
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
