"""Testing SlimsHandler"""

import json
import os
import unittest
from datetime import datetime
from decimal import Decimal
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
from aind_metadata_service.slims.ecephys.handler import SlimsEcephysData
from aind_metadata_service.slims.histology.handler import SlimsHistologyData
from aind_metadata_service.slims.imaging.handler import SlimsSpimData
from aind_metadata_service.slims.viral_injection.handler import (
    SlimsViralInjectionData,
    SlimsViralMaterialData,
)
from aind_metadata_service.slims.water_restriction.handler import (
    SlimsWaterRestrictionData,
)

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
        with open(
            RESOURCES_DIR / "water_restriction" / "slims_wr_data.json"
        ) as f:
            slims_wr_data_json = json.load(f)
        self.slims_wr_data = [
            SlimsWaterRestrictionData.model_validate(data)
            for data in slims_wr_data_json
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

    def test_get_slims_ecephys_response_bad_subject_id(self):
        """Empty subject_id should return Bad Request"""
        response = self.handler.get_slims_ecephys_response(
            session_name=None, subject_id="", start_date=None, end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_ecephys_response_bad_start_date(self):
        """Bad start date should return Bad Request"""
        response = self.handler.get_slims_ecephys_response(
            session_name=None,
            subject_id=None,
            start_date="2020/02/10",
            end_date=None,
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_ecephys_response_bad_end_date(self):
        """Bad end date should return Bad Request"""
        response = self.handler.get_slims_ecephys_response(
            subject_id=None,
            start_date=None,
            end_date="2020/02/10",
            session_name=None,
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    @patch(
        "aind_metadata_service.slims.ecephys.handler.SlimsEcephysHandler"
        ".get_ephys_data_from_slims"
    )
    def test_get_slims_ecephys_response(self, mock_slims_get: MagicMock):
        """Tests get_slims_ecephys_response success"""
        mock_slims_get.return_value = [
            SlimsEcephysData(
                experiment_run_created_on=1739383241200,
                specimen_id="BRN00000018",
                subject_id="750108",
                date_performed=1739383260000,
            )
        ]
        response = self.handler.get_slims_ecephys_response(
            subject_id="750108",
            start_date=None,
            end_date=None,
            session_name=None,
        )
        self.assertEqual(200, response.status_code)

    @patch(
        "aind_metadata_service.slims.ecephys.handler.SlimsEcephysHandler"
        ".get_ephys_data_from_slims"
    )
    def test_get_slims_ecephys_response_empty(self, mock_slims_get: MagicMock):
        """Tests get_slims_ecephys_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_slims_ecephys_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
            session_name=None,
        )
        self.assertEqual(404, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.ecephys.handler.SlimsEcephysHandler"
        ".get_ephys_data_from_slims"
    )
    def test_get_slims_ecephys_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_ecephys_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_slims_ecephys_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
            session_name=None,
        )
        self.assertEqual(500, response.status_code)
        mock_log_exception.assert_called_once()

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

    def test_get_slims_water_restriction_response_bad_subject_id(self):
        """Empty subject_id should return Bad Request"""
        response = self.handler.get_slims_water_restriction_response(
            subject_id="", start_date=None, end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_water_restriction_response_bad_start_date(self):
        """Bad start date should return Bad Request"""
        response = self.handler.get_slims_water_restriction_response(
            subject_id=None, start_date="2020/02/10", end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_water_restriction_response_bad_end_date(self):
        """Bad end date should return Bad Request"""
        response = self.handler.get_slims_water_restriction_response(
            subject_id=None,
            start_date=None,
            end_date="2020/02/10",
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_slims_water_restriction_response(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_water_restriction_response success"""
        mock_slims_get.return_value = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="762287",
                start_date=1734119012354,
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction=0.85,
                baseline_weight=28.23,
                weight_unit="g",
            )
        ]
        response = self.handler.get_slims_water_restriction_response(
            subject_id="762287",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(200, response.status_code)

    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_slims_water_restriction_response_empty(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_water_restriction_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_slims_water_restriction_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(404, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_slims_water_restriction_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_water_restriction_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_slims_water_restriction_response(
            subject_id="744743",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(500, response.status_code)
        mock_log_exception.assert_called_once()

    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_water_restriction_procedures_model_response(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_water_restriction_procedures_model_response success"""
        mock_slims_get.return_value = self.slims_wr_data
        response = (
            self.handler.get_water_restriction_procedures_model_response(
                subject_id="762287"
            )
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, response.status_code)
        self.assertIsInstance(response.aind_models[0], Procedures)

    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_water_restriction_procedures_model_response_empty(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_water_restriction_procedures when no data returned"""
        mock_slims_get.return_value = []
        response = (
            self.handler.get_water_restriction_procedures_model_response(
                subject_id="762287",
            )
        )
        self.assertEqual(StatusCodes.NO_DATA_FOUND, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.water_restriction.handler"
        ".SlimsWaterRestrictionHandler.get_water_restriction_data_from_slims"
    )
    def test_get_water_restriction_procedures_model_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_water_restriction_procedures when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = (
            self.handler.get_water_restriction_procedures_model_response(
                subject_id="762287",
            )
        )
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, response.status_code
        )
        mock_log_exception.assert_called_once()

    def test_get_slims_viral_injection_response_bad_subject_id(self):
        """Empty subject_id should return Bad Request"""
        response = self.handler.get_slims_viral_injection_response(
            subject_id="", start_date=None, end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_viral_injection_response_bad_start_date(self):
        """Bad start date should return Bad Request"""
        response = self.handler.get_slims_viral_injection_response(
            subject_id=None, start_date="2020/02/10", end_date=None
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    def test_get_slims_viral_injection_response_bad_end_date(self):
        """Bad end date should return Bad Request"""
        response = self.handler.get_slims_viral_injection_response(
            subject_id=None,
            start_date=None,
            end_date="2020/02/10",
        )
        self.assertEqual(StatusCodes.BAD_REQUEST.value, response.status_code)

    @patch(
        "aind_metadata_service.slims.viral_injection.handler"
        ".SlimsViralInjectionHandler.get_viral_injection_info_from_slims"
    )
    def test_get_slims_viral_injection_response(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_viral_injection success"""
        mock_slims_get.return_value = [
            SlimsViralInjectionData(
                content_category="Viral Materials",
                content_type="Viral injection",
                content_created_on=None,
                content_modified_on=None,
                name="INJ00000002",
                viral_injection_buffer="AAV Buffer",
                volume=Decimal(str(98.56)),
                volume_unit="&mu;l",
                labeling_protein="tdTomato",
                date_made=1746014400000,
                intake_date=None,
                storage_temperature="4 C",
                special_storage_guidelines=["Light sensitive storage"],
                special_handling_guidelines=["BSL - 1"],
                mix_count=None,
                derivation_count=None,
                ingredient_count=None,
                assigned_mice=["614178"],
                requested_for_date=None,
                planned_injection_date=1746705600000,
                planned_injection_time=None,
                order_created_on=1746717795853,
                viral_materials=[
                    SlimsViralMaterialData(
                        content_category="Viral Materials",
                        content_type="Viral solution",
                        content_created_on=1746049926016,
                        content_modified_on=None,
                        viral_solution_type="Injection Dilution",
                        virus_name="7x-TRE-tDTomato",
                        lot_number="VT5355g",
                        lab_team="Molecular Anatomy",
                        virus_type="AAV",
                        virus_serotype="PhP.eB",
                        virus_plasmid_number="AiP300001",
                        name="VRS00000029",
                        dose=Decimal(str(180000000000)),
                        dose_unit=None,
                        titer=Decimal(str(24200000000000)),
                        titer_unit="GC/ml",
                        volume=Decimal(str(8.55)),
                        volume_unit="&mu;l",
                        date_made=1746049926079,
                        intake_date=None,
                        storage_temperature="-80 C",
                        special_storage_guidelines=[
                            "Avoid freeze - thaw cycles"
                        ],
                        special_handling_guidelines=["BSL - 1"],
                        parent_name=None,
                        mix_count=1,
                        derivation_count=0,
                        ingredient_count=0,
                    )
                ],
            )
        ]
        response = self.handler.get_slims_viral_injection_response(
            subject_id="614178",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(200, response.status_code)

    @patch(
        "aind_metadata_service.slims.viral_injection.handler"
        ".SlimsViralInjectionHandler.get_viral_injection_info_from_slims"
    )
    def test_get_slims_viral_injection_response_empty(
        self, mock_slims_get: MagicMock
    ):
        """Tests get_slims_viral_injection_response when no data returned"""
        mock_slims_get.return_value = []
        response = self.handler.get_slims_viral_injection_response(
            subject_id="614178",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(404, response.status_code)

    @patch("logging.exception")
    @patch(
        "aind_metadata_service.slims.viral_injection.handler"
        ".SlimsViralInjectionHandler.get_viral_injection_info_from_slims"
    )
    def test_get_slims_viral_injection_response_error(
        self, mock_slims_get: MagicMock, mock_log_exception: MagicMock
    ):
        """Tests get_slims_viral_injection_response when an error happens"""
        mock_slims_get.side_effect = Exception("An error occurred.")
        response = self.handler.get_slims_viral_injection_response(
            subject_id="614178",
            start_date=None,
            end_date=None,
        )
        self.assertEqual(500, response.status_code)
        mock_log_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
