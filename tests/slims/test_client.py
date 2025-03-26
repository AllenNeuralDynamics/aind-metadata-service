"""Testing SlimsHandler"""

import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.rig import Rig
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from aind_slims_api.operations.ecephys_session import (
    EcephysSession as SlimsEcephysSession,
)
from requests.models import Response

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import SpimImagingInformation
from aind_metadata_service.slims.client import SlimsHandler, SlimsSettings
from aind_metadata_service.slims.histology.handler import SlimsHistologyData
from aind_metadata_service.slims.imaging.handler import SlimsSpimData

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
        with open(RESOURCES_DIR / "histology" / "slims_hist_data.json") as f:
            slims_hist_data_json = json.load(f)
        with open(
            RESOURCES_DIR / "histology" / "expected_histology_procedures.json"
        ) as f:
            self.expected_procedures_json = json.load(f)
        self.slims_hist_data = [
            SlimsHistologyData.model_validate(data)
            for data in slims_hist_data_json
        ]
        with open(RAW_DIR / "imaging_metadata_response.json") as f:
            slims_data3 = json.load(f)
        slims_data4 = slims_data3.copy()
        slims_data4["date_performed"] = "2024-10-19T20:12:00Z"
        self.slims_imaging_metadata = [slims_data3, slims_data4]
        self.expected_imaging_metadata = [
            SpimImagingInformation(**slims_data3),
            SpimImagingInformation(**slims_data4),
        ]

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

    @patch(
        "aind_metadata_service.slims.client.SlimsHandler._is_json_file",
    )
    @patch("slims.criteria.contains")
    def test_get_instrument_model_response_success_partial_match(
        self, mock_contains: MagicMock, mock_is_json_file: MagicMock
    ):
        """Test successful response from get_instrument_model_response when
        partial_match is set to True"""
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
            response = self.handler.get_instrument_model_response(
                "test_id", partial_match=True
            )

            self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)
            mock_construct.assert_called_once_with(**mock_response.json())
            mock_contains.assert_called_once_with("name", "test_id")

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

    @patch("slims.criteria.contains")
    def test_get_rig_model_response_success_partial_match(
        self, mock_contains: MagicMock
    ):
        """Test successful response from get_rig_model_response when
        partial_match is set to True."""
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
            response = self.handler.get_rig_model_response(
                "test_id", partial_match=True
            )

            self.assertEqual(response.status_code, StatusCodes.DB_RESPONDED)
            mock_construct.assert_called_once_with(**mock_response.json())
            mock_contains.assert_called_once_with("name", "test_id")

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

    def test_parse_date(self):
        """Tests _parse_date method"""

        dt = self.handler._parse_date(date_str="2025-02-10T00:00:00")
        expected_dt = datetime(2025, 2, 10)
        self.assertEqual(expected_dt, dt)

    def test_parse_date_none(self):
        """Tests _parse_date method when input is None"""

        dt = self.handler._parse_date(date_str=None)
        self.assertIsNone(dt)

    def test_parse_date_error(self):
        """Tests _parse_date method when there is a parsing error"""

        response = self.handler._parse_date(date_str="2025/02/10")
        self.assertEqual(StatusCodes.BAD_REQUEST, response.status_code)

    def test_get_slims_imaging_response_bad_subject_id(self):
        """Empty subject_id should return Bad Request"""
        response = self.handler.get_slims_imaging_response(
            subject_id="", start_date=None, end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_imaging_response_bad_start_date(self):
        """Bad start date should return Bad Request"""
        response = self.handler.get_slims_imaging_response(
            subject_id=None, start_date="2020/02/10", end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_imaging_response_bad_end_date(self):
        """Bad end date should return Bad Request"""
        response = self.handler.get_slims_imaging_response(
            subject_id=None,
            start_date=None,
            end_date="2020/02/10",
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    @patch(
        "aind_metadata_service.slims.imaging.handler.SlimsImagingHandler"
        ".get_spim_data_from_slims"
    )
    def test_get_slims_imaging_response(self, mock_slims_get: MagicMock):
        """Tests get_slims_imaging_response success"""
        mock_slims_get.return_value = [
            SlimsSpimData(
                experiment_run_created_on=1739383241200,
                specimen_id="BRN00000018",
                subject_id="744742",
                date_performed=1739383260000,
            )
        ]
        response = self.handler.get_slims_imaging_response(
            subject_id="744742",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(200, response.status_code)

    @patch(
        "aind_metadata_service.slims.imaging.handler.SlimsImagingHandler"
        ".get_spim_data_from_slims"
    )
    def test_get_slims_imaging_response_empty(self, mock_slims_get: MagicMock):
        """Tests get_slims_imaging_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_slims_imaging_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(404, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.imaging.handler.SlimsImagingHandler"
        ".get_spim_data_from_slims"
    )
    def test_get_slims_imaging_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_imaging_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_slims_imaging_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(500, response.status_code)
        mock_log_exception.assert_called_once()

    def test_get_slims_histology_response_bad_subject_id(self):
        """Empty subject_id should return Bad Request"""
        response = self.handler.get_slims_histology_response(
            subject_id="", start_date=None, end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_histology_response_bad_start_date(self):
        """Bad start date should return Bad Request"""
        response = self.handler.get_slims_histology_response(
            subject_id=None, start_date="2020/02/10", end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_histology_response_bad_end_date(self):
        """Bad end date should return Bad Request"""
        response = self.handler.get_slims_histology_response(
            subject_id=None,
            start_date=None,
            end_date="2020/02/10",
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_slims_histology_response(self, mock_slims_get: MagicMock):
        """Tests get_slims_histology_response success"""
        mock_slims_get.return_value = [
            SlimsHistologyData(
                experiment_run_created_on=1739383241200,
                specimen_id="BRN00000018",
                subject_id="744742",
                date_performed=1739383260000,
            )
        ]
        response = self.handler.get_slims_histology_response(
            subject_id="744742",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(200, response.status_code)

    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_slims_histology_response_empty(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_histology_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_slims_histology_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(404, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_slims_histology_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_histology_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_slims_histology_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(500, response.status_code)
        mock_log_exception.assert_called_once()

    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_histology_procedures_model_response(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_histology_procedures_model_response success"""
        mock_slims_get.return_value = self.slims_hist_data
        response = self.handler.get_histology_procedures_model_response(
            subject_id="744742"
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        self.assertIsInstance(response.aind_models[0], Procedures)

    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_histology_procedures_model_response_empty(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_histology_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_histology_procedures_model_response(
            subject_id="744742",
        )
        self.assertEqual(StatusCodes.NO_DATA_FOUND, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.histology.handler.SlimsHistologyHandler"
        ".get_hist_data_from_slims"
    )
    def test_get_histology_procedures_model_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_histology_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_histology_procedures_model_response(
            subject_id="744743",
        )
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, response.status_code
        )
        mock_log_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
