"""Testing SlimsHandler"""

import unittest
from unittest.mock import patch, MagicMock
from requests.models import Response
from aind_metadata_service.client import StatusCodes
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig

from aind_metadata_service.slims.client import SlimsHandler, SlimsSettings
from aind_slims_api.models.instrument import SlimsInstrumentRdrc


class TestSlimsHandler(unittest.TestCase):
    """Test class for SlimsHandler"""

    @patch("aind_metadata_service.slims.client.SlimsClient")
    def setUp(self, mock_slims_client):
        """Set up the test environment by mocking SlimsClient."""
        settings = SlimsSettings(
            username="testuser", password="testpass", host="testhost"
        )
        self.mock_client = mock_slims_client.return_value
        self.handler = SlimsHandler(settings)

    def test_is_json_file_true(self):
        """Test that _is_json_file returns True for valid JSON response."""
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {"Content-Type": "application/json"}
        self.assertTrue(self.handler._is_json_file(mock_response))

    def test_is_json_file_false(self):
        """Test that _is_json_file returns False for non-JSON response."""
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {"Content-Type": "text/plain"}
        self.assertFalse(self.handler._is_json_file(mock_response))

    @patch(
        "aind_metadata_service.slims.client.SlimsHandler._is_json_file",
        return_value=True,
    )
    def test_get_instrument_model_response_success(self, mock_is_json_file):
        """Test successful response from get_instrument_model_response."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        self.mock_client.fetch_attachment_content.return_value = mock_response

        with patch(
            "aind_data_schema.core.instrument.Instrument.model_construct"
        ) as mock_construct:
            mock_construct.return_value = MagicMock(spec=Instrument)
            response = self.handler.get_instrument_model_response("test_id")

            self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)
            mock_construct.assert_called_once_with(**mock_response.json())
            self.mock_client.fetch_model.assert_called_once_with(
                SlimsInstrumentRdrc, name="test_id"
            )

    def test_get_instrument_model_response_invalid_response(self):
        """Test response when the content is not valid response."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        self.mock_client.fetch_attachment_content.return_value = mock_response

        response = self.handler.get_instrument_model_response("test_id")

        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )

    @patch("aind_metadata_service.slims.client.logging.error")
    def test_get_instrument_model_response_exception(self, mock_logging_error):
        """Test get_instrument_model_response handles generic exception."""
        self.handler.client.fetch_model.side_effect = Exception(
            "Some error from SLIMS."
        )
        response = self.handler.get_instrument_model_response("test_id")
        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )
        mock_logging_error.assert_called_once_with(
            repr(Exception("Some error from SLIMS."))
        )

        self.handler.client.fetch_model.assert_called_once_with(
            SlimsInstrumentRdrc, name="test_id"
        )

    @patch("aind_metadata_service.slims.client.logging.error")
    def test_get_rig_model_response_exception(self, mock_logging_error):
        """Test get_instrument_model_response handles generic exception."""
        self.handler.client.fetch_model.side_effect = Exception(
            "Some error from SLIMS."
        )
        response = self.handler.get_rig_model_response("test_id")
        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )
        mock_logging_error.assert_called_once_with(
            repr(Exception("Some error from SLIMS."))
        )

        self.handler.client.fetch_model.assert_called_once_with(
            SlimsInstrumentRdrc, name="test_id"
        )

    def test_get_instrument_model_response_not_found(self):
        """Test response when SlimsRecordNotFound is raised."""
        self.mock_client.fetch_model.side_effect = SlimsRecordNotFound

        response = self.handler.get_instrument_model_response("test_id")
        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)

    def test_get_instrument_model_response_connection_error(self):
        """Test response when a connection error occurs (status 401)."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 401
        self.mock_client.fetch_attachment_content.return_value = mock_response

        response = self.handler.get_instrument_model_response("test_id")
        self.assertEqual(response.status_code, StatusCodes.CONNECTION_ERROR)

    def test_get_rig_model_response_success(self):
        """Test successful response from get_rig_model_response."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        self.mock_client.fetch_attachment_content.return_value = mock_response

        with patch(
            "aind_data_schema.core.rig.Rig.model_construct"
        ) as mock_construct:
            mock_construct.return_value = MagicMock(spec=Rig)
            response = self.handler.get_rig_model_response("test_id")

            self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)
            mock_construct.assert_called_once_with(**mock_response.json())
            self.mock_client.fetch_model.assert_called_once_with(
                SlimsInstrumentRdrc, name="test_id"
            )

    def test_get_rig_model_response_not_found(self):
        """Test when SlimsRecordNotFound is raised."""
        self.mock_client.fetch_model.side_effect = SlimsRecordNotFound

        response = self.handler.get_rig_model_response("test_id")
        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)

    def test_get_rig_model_response_connection_error(self):
        """Test response when a connection error occurs (status 401)."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 401
        self.mock_client.fetch_attachment_content.return_value = mock_response

        response = self.handler.get_rig_model_response("test_id")
        self.assertEqual(response.status_code, StatusCodes.CONNECTION_ERROR)

    def test_get_rig_model_response_invalid_response(self):
        """Test response when the content is not valid response."""
        mock_inst = MagicMock()
        self.mock_client.fetch_model.return_value = mock_inst
        mock_attachment = MagicMock()
        self.mock_client.fetch_attachment.return_value = mock_attachment
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        self.mock_client.fetch_attachment_content.return_value = mock_response

        response = self.handler.get_rig_model_response("test_id")

        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )


if __name__ == "__main__":
    unittest.main()
