"""Module to test Slims client class"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.client import SlimsClient, SlimsSettings

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "slims" / "json_entity.json"


class TestSlimsSettings(unittest.TestCase):
    """Class to test methods for SlimsSettings."""

    EXAMPLE_ENV_VAR1 = {
        "SLIMS_USERNAME": "slims-user",
        "SLIMS_PASSWORD": "abc-123",
        "SLIMS_HOST": "slims-host",
        "SLIMS_DB": "test",
    }

    @patch.dict(os.environ, EXAMPLE_ENV_VAR1, clear=True)
    def test_settings_set_from_env_vars(self):
        """Tests that the settings can be set from env vars."""

        settings1 = SlimsSettings()
        settings2 = SlimsSettings(username="Agent0")
        self.assertEqual("abc-123", settings1.password.get_secret_value())
        self.assertEqual("slims-user", settings1.username)
        self.assertEqual("slims-host", settings1.host)
        self.assertEqual("test", settings1.db)
        self.assertEqual("abc-123", settings2.password.get_secret_value())
        self.assertEqual("Agent0", settings2.username)
        self.assertEqual("slims-host", settings2.host)
        self.assertEqual("test", settings2.db)


class TestSlimsClient(unittest.IsolatedAsyncioTestCase):
    """Class to test methods for SlimsClient."""

    @classmethod
    def setUpClass(cls):
        """Load record object before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            json_entity = json.load(f)
        # Turning off type check on slims_api argument
        # noinspection PyTypeChecker
        record_object = Record(json_entity=json_entity, slims_api=None)
        cls.example_record = record_object

    @patch("slims.slims.Slims.fetch")
    async def test_slims_fetch_success(self, mock_fetch: MagicMock):
        """Tests successful record return response"""
        mock_fetch.return_value = [self.example_record]
        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        client = SlimsClient(settings=settings)
        record = await client.get_record("123456")
        self.assertEqual(1, record.json_entity["pk"])
        self.assertEqual("Content", record.json_entity["tableName"])

    @patch("slims.slims.Slims.fetch")
    @patch("logging.error")
    async def test_get_sheet_error(
        self, mock_log_error: MagicMock, mock_fetch: MagicMock
    ):
        """Tests sheet return error response"""
        mock_fetch.side_effect = MagicMock(
            side_effect=Exception("Error connecting to server")
        )
        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        client = SlimsClient(settings=settings)
        with self.assertRaises(Exception) as e:
            _ = await client.get_record(subject_id="12345")

        self.assertEqual("Error connecting to server", str(e.exception))
        mock_log_error.assert_called_once_with(
            "Exception('Error connecting to server')"
        )


if __name__ == "__main__":
    unittest.main()
