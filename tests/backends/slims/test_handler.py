"""Tests handler module"""

import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from requests import Response

from aind_metadata_service.backends.slims.handler import SessionHandler

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
RESOURCE_DIR = TEST_DIR / "resources" / "backends" / "smartsheet"


class TestSessionHandler(unittest.TestCase):
    """Test methods in SessionHandler Class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class with loaded json and shared examples."""

        test_client = SlimsClient(
            url="http://slims.example.com",
            username="slims_user",
            password="slims_password",
        )
        cls.test_handler = SessionHandler(session=test_client)

    @patch("aind_slims_api.core.SlimsClient.fetch_attachment_content")
    @patch("aind_slims_api.core.SlimsClient.fetch_attachment")
    @patch("aind_slims_api.core.SlimsClient.fetch_model")
    @patch("logging.warning")
    def test_get_instrument_attachment(
        self,
        mock_log_warn: MagicMock,
        mock_fetch_model: MagicMock,
        mock_fetch_attachment: MagicMock,
        mock_fetch_attachment_content: MagicMock,
    ):
        """Tests get_instrument_attachment success with partial_match set to
        False"""

        mocked_model = MagicMock()
        mock_fetch_model.return_value = mocked_model
        mocked_attachment = MagicMock()
        mock_fetch_attachment.return_value = mocked_attachment
        mocked_attachment_response = Response()
        mocked_attachment_response.status_code = 200
        mocked_attachment_response._content = b'{"a": "b"}'
        mock_fetch_attachment_content.return_value = mocked_attachment_response

        content = self.test_handler.get_instrument_attachment(input_id="abc")
        self.assertEqual({"a": "b"}, content)
        mock_log_warn.assert_not_called()

    @patch("aind_slims_api.core.SlimsClient.fetch_attachment_content")
    @patch("aind_slims_api.core.SlimsClient.fetch_attachment")
    @patch("aind_slims_api.core.SlimsClient.fetch_model")
    @patch("logging.warning")
    def test_get_instrument_attachment_partial_match(
        self,
        mock_log_warn: MagicMock,
        mock_fetch_model: MagicMock,
        mock_fetch_attachment: MagicMock,
        mock_fetch_attachment_content: MagicMock,
    ):
        """Tests get_instrument_attachment success with partial_match set to
        True"""

        mocked_model = MagicMock()
        mock_fetch_model.return_value = mocked_model
        mocked_attachment = MagicMock()
        mock_fetch_attachment.return_value = mocked_attachment
        mocked_attachment_response = Response()
        mocked_attachment_response.status_code = 200
        mocked_attachment_response._content = b'{"a": "b"}'
        mock_fetch_attachment_content.return_value = mocked_attachment_response

        content = self.test_handler.get_instrument_attachment(
            input_id="abc", partial_match=True
        )
        self.assertEqual({"a": "b"}, content)
        mock_log_warn.assert_not_called()

    @patch("aind_slims_api.core.SlimsClient.fetch_attachment_content")
    @patch("aind_slims_api.core.SlimsClient.fetch_attachment")
    @patch("aind_slims_api.core.SlimsClient.fetch_model")
    @patch("logging.warning")
    def test_get_instrument_attachment_no_attachment(
        self,
        mock_log_warn: MagicMock,
        mock_fetch_model: MagicMock,
        mock_fetch_attachment: MagicMock,
        mock_fetch_attachment_content: MagicMock,
    ):
        """Tests get_instrument_attachment return None if no attachment."""

        mocked_model = MagicMock()
        mock_fetch_model.return_value = mocked_model
        mock_fetch_attachment.return_value = None

        content = self.test_handler.get_instrument_attachment(input_id="abc")
        self.assertIsNone(content)
        mock_log_warn.assert_called_once_with(
            "Attachment not found for input_id abc and partial match False"
        )
        mock_fetch_attachment_content.assert_not_called()

    @patch("aind_slims_api.core.SlimsClient.fetch_attachment_content")
    @patch("aind_slims_api.core.SlimsClient.fetch_attachment")
    @patch("aind_slims_api.core.SlimsClient.fetch_model")
    @patch("logging.warning")
    def test_get_instrument_attachment_error(
        self,
        mock_log_warn: MagicMock,
        mock_fetch_model: MagicMock,
        mock_fetch_attachment: MagicMock,
        mock_fetch_attachment_content: MagicMock,
    ):
        """Tests get_instrument_attachment raises error if there is an error
        fetching the attachment for slims."""

        mocked_model = MagicMock()
        mock_fetch_model.return_value = mocked_model
        mocked_attachment = MagicMock()
        mock_fetch_attachment.return_value = mocked_attachment
        mocked_attachment_response = Response()
        mocked_attachment_response.status_code = 500
        mock_fetch_attachment_content.return_value = mocked_attachment_response

        with self.assertRaises(Exception) as e:
            self.test_handler.get_instrument_attachment(input_id="abc")
        self.assertIn("500 Server Error", str(e.exception))
        mock_log_warn.assert_not_called()

    @patch("aind_slims_api.core.SlimsClient.fetch_attachment_content")
    @patch("aind_slims_api.core.SlimsClient.fetch_attachment")
    @patch("aind_slims_api.core.SlimsClient.fetch_model")
    @patch("logging.warning")
    def test_get_instrument_attachment_no_record(
        self,
        mock_log_warn: MagicMock,
        mock_fetch_model: MagicMock,
        mock_fetch_attachment: MagicMock,
        mock_fetch_attachment_content: MagicMock,
    ):
        """Tests get_instrument_attachment return None if no record."""

        mock_fetch_model.side_effect = SlimsRecordNotFound()

        content = self.test_handler.get_instrument_attachment(input_id="abc")
        self.assertIsNone(content)
        mock_log_warn.assert_called_once_with(
            "Slims record not found for input_id abc and partial match False"
        )
        mock_fetch_attachment.assert_not_called()
        mock_fetch_attachment_content.assert_not_called()


if __name__ == "__main__":
    unittest.main()
