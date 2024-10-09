"""Tests configs module"""

import unittest

from aind_metadata_service.backends.labtracks.configs import Settings


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


if __name__ == "__main__":
    unittest.main()
