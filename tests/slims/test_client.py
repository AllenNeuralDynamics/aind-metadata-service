"""Testing SlimsHandler"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from aind_slims_api.operations import SPIMHistologyExpBlock
from aind_slims_api.operations.ecephys_session import (
    EcephysSession as SlimsEcephysSession,
)
from requests.models import Response

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.slims.client import SlimsHandler, SlimsSettings

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "slims"
)
RAW_DIR = RESOURCES_DIR / "raw"
MAPPED_DIR = RESOURCES_DIR / "mapped"


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

        with open(RAW_DIR / "ecephys_session_response.json", "r") as f:
            slims_data1 = json.load(f)
        with open(MAPPED_DIR / "ecephys_session.json", encoding="utf-8") as f:
            expected_data1 = json.load(f)
        self.slims_sessions = [
            SlimsEcephysSession.model_validate(slims_data1),
        ]
        self.expected_sessions = [expected_data1]
        with open(RAW_DIR / "histology_procedures_response.json") as f:
            slims_data2 = json.load(f)
        with open(MAPPED_DIR / "specimen_procedures.json") as f:
            expected_data2 = json.load(f)
        self.slims_procedures = [
            SPIMHistologyExpBlock.model_validate(block)
            for block in slims_data2
        ]
        self.expected_procedures = expected_data2

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
    )
    def test_get_instrument_model_response_success(self, mock_is_json_file):
        """Test successful response from get_instrument_model_response."""
        mock_inst = MagicMock()
        mock_is_json_file.return_value = True
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

    @patch("aind_metadata_service.slims.client.SlimsSessionMapper")
    @patch("aind_metadata_service.slims.client.fetch_ecephys_sessions")
    def test_get_sessions_model_response_success(
        self, mock_fetch_sessions, mock_mapper
    ):
        """Tests that sessions data is fetched as expected."""
        mock_fetch_sessions.return_value = self.slims_sessions
        mock_mapper_instance = mock_mapper.return_value
        mock_mapper_instance.map_sessions.return_value = self.expected_sessions
        response = self.handler.get_sessions_model_response("test_id")

        self.assertEqual(response.aind_models, self.expected_sessions)
        self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)

    @patch("aind_metadata_service.slims.client.fetch_ecephys_sessions")
    def test_get_sessions_model_response_no_data(self, mock_fetch_sessions):
        """Tests no data found response."""
        mock_fetch_sessions.return_value = []
        response = self.handler.get_sessions_model_response("test_id")

        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)

    @patch("aind_metadata_service.slims.client.fetch_ecephys_sessions")
    def test_get_sessions_model_response_unexpected_error(
        self, mock_fetch_sessions
    ):
        """Tests internal server error.""" ""
        mock_fetch_sessions.side_effect = Exception("Unexpected error")

        response = self.handler.get_sessions_model_response("test_id")

        # Assert that the response is internal server error
        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )

    def test_get_sessions_model_response_not_found(self):
        """Test response when SlimsRecordNotFound is raised."""
        self.mock_client.fetch_model.side_effect = SlimsRecordNotFound

        response = self.handler.get_sessions_model_response("test_id")
        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)

    @patch("aind_metadata_service.slims.client.SlimsHistologyMapper")
    @patch("aind_metadata_service.slims.client.fetch_histology_procedures")
    def test_get_specimen_procedures_model_response_success(
        self, mock_fetch_procedures, mock_mapper
    ):
        """Tests that sessions data is fetched as expected."""
        mock_fetch_procedures.return_value = self.slims_procedures
        mock_mapper_instance = mock_mapper.return_value
        mock_mapper_instance.map_specimen_procedures.return_value = (
            self.expected_procedures
        )
        response = self.handler.get_specimen_procedures_model_response(
            "test_id"
        )
        self.assertEqual(
            response.aind_models[0].specimen_procedures,
            self.expected_procedures,
        )
        self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)

    @patch("aind_metadata_service.slims.client.fetch_histology_procedures")
    def test_get_specimen_procedures_model_response_no_data(
        self, mock_fetch_procedures
    ):
        """Tests no data found response."""
        mock_fetch_procedures.return_value = []
        response = self.handler.get_specimen_procedures_model_response(
            "test_id"
        )

        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)

    @patch("aind_metadata_service.slims.client.fetch_histology_procedures")
    def test_get_specimen_procedures_model_response_unexpected_error(
        self, mock_fetch_procedures
    ):
        """Tests internal server error.""" ""
        mock_fetch_procedures.side_effect = Exception("Unexpected error")
        response = self.handler.get_specimen_procedures_model_response(
            "test_id"
        )
        self.assertEqual(
            response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )

    def test_get_specimen_procedures_model_response_not_found(self):
        """Test response when SlimsRecordNotFound is raised."""
        self.mock_client.fetch_model.side_effect = SlimsRecordNotFound

        response = self.handler.get_specimen_procedures_model_response(
            "test_id"
        )
        self.assertEqual(response.status_code, StatusCodes.NO_DATA_FOUND)


if __name__ == "__main__":
    unittest.main()
