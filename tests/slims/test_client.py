"""Module to test Slims client class"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig
from slims.internal import Record

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.slims.client import SlimsClient, SlimsSettings

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "slims"


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
    def _load_json_files(cls, folder_path):
        """Loads resources for testing"""
        for filename in os.listdir(folder_path):
            with open(os.path.join(folder_path, filename), "r") as f:
                attribute_name = os.path.splitext(filename)[0]
                setattr(cls, attribute_name, json.load(f))

    @classmethod
    def setUpClass(cls):
        """Load record object before running tests."""
        cls._load_json_files(EXAMPLE_PATH)
        record_object = Record(json_entity=cls.json_entity, slims_api=None)

        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        cls.client = SlimsClient(settings=settings)
        cls.example_record = record_object

    @patch("slims.slims.Slims.fetch")
    def test_slims_fetch_content_success(self, mock_fetch: MagicMock):
        """Tests successful record return response"""
        mock_fetch.return_value = [self.example_record]
        record = self.client.get_content_record("123456")
        self.assertEqual(1, record.json_entity["pk"])
        self.assertEqual("Content", record.json_entity["tableName"])

    @patch("slims.slims.Slims.fetch")
    @patch("logging.error")
    def test_get_sheet_error(
        self, mock_log_error: MagicMock, mock_fetch: MagicMock
    ):
        """Tests sheet return error response"""
        mock_fetch.side_effect = MagicMock(
            side_effect=Exception("Error connecting to server")
        )
        with self.assertRaises(Exception) as e:
            self.client.get_content_record(subject_id="12345")

        self.assertEqual("Error connecting to server", str(e.exception))
        mock_log_error.assert_called_once_with(
            "Exception('Error connecting to server')"
        )

    def test_get_record_response_no_criteria(self):
        """Tests that record is retrieved without criteria as expected."""
        table_name = "example_table"
        criteria = None
        expected_body = {
            "sortBy": None,
            "startRow": None,
            "endRow": None,
        }
        expected_url = table_name + "/advanced"
        self.client._get_response = MagicMock()
        self.client.get_record_response(table_name, criteria)

        self.client._get_response.assert_called_once_with(
            expected_url, body=expected_body
        )

    def test_get_record_response_with_criteria(self):
        """Tests that record is retrieved with criteria as expected."""
        table_name = "example_table"
        criteria = MagicMock()
        criteria.to_dict.return_value = {"field": "value"}
        expected_body = {
            "sortBy": None,
            "startRow": None,
            "endRow": None,
            "criteria": {"field": "value"},
        }
        expected_url = table_name + "/advanced"

        self.client._get_response = MagicMock()
        self.client.get_record_response(table_name, criteria)

        self.client._get_response.assert_called_once_with(
            expected_url, body=expected_body
        )

    def test_get_attachment_response(self):
        """Tests that attachment response is retrieved as expected."""
        entity = {"tableName": "example_table", "pk": 123}
        expected_url = "attachment/example_table/123"

        self.client._get_response = MagicMock()
        self.client.get_attachment_response(entity)

        self.client._get_response.assert_called_once_with(expected_url)

    def test_get_file_response(self):
        """Tests that file response is retrieved as expected."""
        entity = {"tableName": "example_table", "pk": 123}
        expected_url = "repo/123"
        self.client._get_response = MagicMock()
        self.client.get_file_response(entity)

        self.client._get_response.assert_called_once_with(expected_url)

    @patch(
        "aind_metadata_service.slims.client.SlimsClient."
        "get_attachment_response"
    )
    @patch("aind_metadata_service.slims.client.SlimsClient.get_file_response")
    @patch("aind_metadata_service.slims.client.SlimsClient._is_json_file")
    def test_extract_instrument_models_from_response(
        self,
        mock_is_json,
        mock_get_file_response,
        mock_get_attachment_response,
    ):
        """Tests that aind models are extracted as expected."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entities": [self.instrument_json_entity]
        }
        mock_get_attachment_response.return_value.status_code = 200
        mock_get_attachment_response.return_value.json.return_value = {
            "entities": [self.attachment_json_entity]
        }
        mock_get_file_response.return_value.status_code = 200
        mock_get_file_response.return_value.json.return_value = self.instrument
        mock_is_json.return_value = True

        models = self.client.extract_instrument_models_from_response(
            mock_response
        )
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].instrument_id, "SmartSPIM2-2")
        mock_get_attachment_response.assert_called_with(
            self.instrument_json_entity
        )
        mock_get_file_response.assert_called_with(self.attachment_json_entity)

    @patch(
        "aind_metadata_service.slims.client.SlimsClient."
        "get_attachment_response"
    )
    @patch("aind_metadata_service.slims.client.SlimsClient.get_file_response")
    @patch("aind_metadata_service.slims.client.SlimsClient._is_json_file")
    def test_extract_rig_models_from_response(
        self,
        mock_is_json,
        mock_get_file_response,
        mock_get_attachment_response,
    ):
        """Tests that aind models are extracted as expected."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entities": [self.instrument_json_entity]
        }
        mock_get_attachment_response.return_value.status_code = 200
        mock_get_attachment_response.return_value.json.return_value = {
            "entities": [self.attachment_json_entity]
        }
        mock_get_file_response.return_value.status_code = 200
        mock_get_file_response.return_value.json.return_value = self.ephys_rig
        mock_is_json.return_value = True

        models = self.client.extract_rig_models_from_response(mock_response)
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].rig_id, "323_EPHYS1")
        mock_get_attachment_response.assert_called_with(
            self.instrument_json_entity
        )
        mock_get_file_response.assert_called_with(self.attachment_json_entity)

    def test_is_json(self):
        """Tests instrument model check."""
        attached_file = MagicMock()
        attached_file.json.return_value = self.instrument
        attached_file.headers = {
            "content-disposition": "attachment; "
            'filename="some_instrument.json"',
            "Content-Type": "application/json",
        }
        self.assertTrue(self.client._is_json_file(attached_file))

    @patch(
        "aind_metadata_service.slims.client.SlimsClient.get_record_response"
    )
    @patch(
        "aind_metadata_service.slims.client.SlimsClient."
        "extract_instrument_models_from_response"
    )
    def test_get_instrument_model_response_success(
        self,
        mock_extract_instrument_models_from_response,
        mock_get_record_response,
    ):
        """Tests that ModelResponse is retrieved successfully."""
        input_id = "12345"
        mock_response = MagicMock()
        mock_get_record_response.return_value = mock_response

        # Test case: Successful response
        mock_response.status_code = 200
        mock_extract_instrument_models_from_response.return_value = [
            Instrument.model_construct(instrument_id="12345")
        ]
        expected_model_response = ModelResponse(
            aind_models=[Instrument.model_construct(instrument_id="12345")],
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(
            self.client.get_instrument_model_response(input_id).status_code,
            expected_model_response.status_code,
        )
        self.assertEqual(
            self.client.get_instrument_model_response(input_id).aind_models,
            expected_model_response.aind_models,
        )

    @patch(
        "aind_metadata_service.slims.client.SlimsClient.get_record_response"
    )
    @patch(
        "aind_metadata_service.slims.client.SlimsClient."
        "extract_rig_models_from_response"
    )
    def test_get_rig_model_response_success(
        self, mock_extract_rig_models_from_response, mock_get_record_response
    ):
        """Tests that ModelResponse is retrieved successfully."""
        input_id = "12345"
        mock_response = MagicMock()
        mock_get_record_response.return_value = mock_response

        # Test case: Successful response
        mock_response.status_code = 200
        mock_extract_rig_models_from_response.return_value = [
            Rig.model_construct(rig_id="12345")
        ]
        expected_model_response = ModelResponse(
            aind_models=[Rig.model_construct(rig_id="12345")],
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(
            self.client.get_rig_model_response(input_id).status_code,
            expected_model_response.status_code,
        )
        self.assertEqual(
            self.client.get_rig_model_response(input_id).aind_models,
            expected_model_response.aind_models,
        )

    @patch(
        "aind_metadata_service.slims.client.SlimsClient.get_record_response"
    )
    def test_get_model_response_connection_error(
        self, mock_get_record_response
    ):
        """Test case: Connection error"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get_record_response.return_value = mock_response
        instrument_response = self.client.get_instrument_model_response(
            "12345"
        )
        self.assertEqual(
            instrument_response.status_code, StatusCodes.CONNECTION_ERROR
        )
        self.assertEqual(instrument_response.aind_models, [])

        rig_response = self.client.get_rig_model_response("12345")
        self.assertEqual(
            rig_response.status_code, StatusCodes.CONNECTION_ERROR
        )
        self.assertEqual(rig_response.aind_models, [])

    @patch(
        "aind_metadata_service.slims.client.SlimsClient.get_record_response"
    )
    def test_get_model_response_internal_server_error(
        self, mock_get_record_response
    ):
        """Test case: Internal Server error"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get_record_response.return_value = mock_response
        instrument_response = self.client.get_instrument_model_response(
            "12345"
        )
        self.assertEqual(
            instrument_response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )
        self.assertEqual(instrument_response.aind_models, [])

        rig_response = self.client.get_rig_model_response("12345")
        self.assertEqual(
            rig_response.status_code, StatusCodes.INTERNAL_SERVER_ERROR
        )
        self.assertEqual(rig_response.aind_models, [])

    @patch(
        "aind_metadata_service.slims.client.SlimsClient.get_record_response"
    )
    @patch("logging.error")
    def test_get_model_response_exception(
        self, mock_log_error: MagicMock, mock_get_record_response: MagicMock
    ):
        """Test case: Exception during execution"""
        mock_get_record_response.side_effect = Exception("Some error")
        self.assertEqual(
            self.client.get_instrument_model_response("12345").status_code,
            StatusCodes.INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(
            self.client.get_rig_model_response("12345").status_code,
            StatusCodes.INTERNAL_SERVER_ERROR,
        )
        mock_log_error.assert_called()

    @patch("aind_metadata_service.slims.client.requests.get")
    def test_get_response_with_oauth(self, mock_requests_get):
        """Tests get response with authentication"""
        url = "https://example.com"
        body = {"key": "value"}
        slims_api = MagicMock()
        slims_api.url = "https://example.com"
        slims_api.oauth = True
        slims_api.oauth_session.get.return_value.status_code = 200
        mock_response = MagicMock()
        mock_requests_get.return_value = mock_response

        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        client = SlimsClient(settings)
        response = client._get_response(url, body, slims_api)

        slims_api.oauth_session.get.assert_called_once_with(
            url,
            headers=slims_api._headers(),
            json=body,
            **slims_api.request_params,
        )
        self.assertEqual(response, slims_api.oauth_session.get.return_value)

    @patch("aind_metadata_service.slims.client.requests.get")
    def test_get_response_with_oauth_url(self, mock_requests_get):
        """Tests get response with different url."""
        url = "other_url"
        body = {"key": "value"}
        slims_api = MagicMock()
        slims_api.url = "https://example.com"
        slims_api.oauth = True
        slims_api.oauth_session.get.return_value.status_code = 200
        mock_response = MagicMock()
        mock_requests_get.return_value = mock_response

        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        client = SlimsClient(settings)
        response = client._get_response(url, body, slims_api)

        slims_api.oauth_session.get.assert_called_once_with(
            slims_api.url + url,
            headers=slims_api._headers(),
            json=body,
            **slims_api.request_params,
        )
        self.assertEqual(response, slims_api.oauth_session.get.return_value)

    @patch("aind_metadata_service.slims.client.requests.get")
    def test_get_response_without_oauth(self, mock_requests_get):
        """Tests get response without authentication"""
        url = "https://example.com"
        body = {"key": "value"}
        slims_api = MagicMock()
        slims_api.url = "https://example.com"
        slims_api.oauth = False
        slims_api.username = "username"
        slims_api.password = "password"
        mock_response = MagicMock()
        mock_requests_get.return_value = mock_response

        settings = SlimsSettings(
            username="test-user", password="pw", host="slims-host", db="test"
        )
        client = SlimsClient(settings)
        response = client._get_response(url, body, slims_api)

        mock_requests_get.assert_called_once_with(
            url,
            auth=(slims_api.username, slims_api.password),
            headers=slims_api._headers(),
            json=body,
            **slims_api.request_params,
        )
        self.assertEqual(response, mock_response)


if __name__ == "__main__":
    unittest.main()
