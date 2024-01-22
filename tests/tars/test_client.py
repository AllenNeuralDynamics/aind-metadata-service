"""Module to test TARS Client methods"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.tars.client import AzureSettings, TarsClient

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "tars" / "mapped_materials.json"


class TestAzureSettings(unittest.TestCase):
    """Class to test methods for AzureSettings."""

    EXAMPLE_ENV_VAR1 = {
        "TENANT_ID": "some_tenant",
        "CLIENT_ID": "some_client",
        "AUTHORITY": "some_authority",
        "CLIENT_SECRET": "some_secret",
        "SCOPE": "some_scope",
    }

    @patch.dict(os.environ, EXAMPLE_ENV_VAR1, clear=True)
    def test_settings_set_from_env_vars(self):
        """Tests that the settings can be set from env vars."""
        settings1 = AzureSettings()

        self.assertEqual("some_tenant", settings1.tenant_id)
        self.assertEqual("some_client", settings1.client_id)
        self.assertEqual("some_scope", settings1.scope)
        self.assertEqual(
            "some_secret",
            settings1.client_secret.get_secret_value(),
        )

    def test_settings_errors(self):
        """Tests that errors are raised if settings are incorrect."""

        with self.assertRaises(ValueError) as e:
            AzureSettings(
                client_id="some_client",
                tenant_id="some_tenant",
            )
        self.assertIn(
            "2 validation errors for AzureSettings", repr(e.exception)
        )


class TestTarsClient(unittest.TestCase):
    """Tests client methods"""

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def setUp(self, mock_credential):
        """Sets up Test TarsClient methods"""
        self.azure_settings = AzureSettings(
            tenant_id="some_tenant_id",
            client_id="some_client_id",
            client_secret="some_client_secret",
            scope="some_scope",
        )

        self.resource = "https://some_resource"

        with open(EXAMPLE_PATH, "r") as f:
            self.expected_materials = json.load(f)

        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        self.tars_client = TarsClient(self.azure_settings, self.resource)
        # mock_credential.return_value.get_token.assert_called_once()

    def test_access_token(self):
        """Tests that token is retrieved as expected."""
        expected_token = "mock_token"
        self.assertEqual(self.tars_client._access_token, expected_token)

    def test_headers(self):
        """Tests that headers is created as expected."""
        expected_headers = {"Authorization": "Bearer mock_token"}
        self.assertEqual(self.tars_client._headers, expected_headers)

    @patch("aind_metadata_service.tars.client.requests.get")
    def test_get_prep_lot_response(self, mock_get):
        """Tests that client can fetch viral prep lot."""

        mock_response = Mock()

        mock_response.json.return_value = {
            "data": [
                {
                    "lot": "12345",
                    "datePrepped": "2023-12-15T12:34:56Z",
                    "viralPrep": {
                        "viralPrepType": {"name": "Crude-SOP#VC002"},
                        "virus": {
                            "aliases": [
                                {"name": "AiP123"},
                                {"name": "AiV456"},
                                {"name": "rAAV-MGT_789"},
                            ]
                        },
                    },
                }
            ]
        }
        mock_get.return_value = mock_response
        result = self.tars_client._get_prep_lot_response("12345")
        expected_url = (
            f"{self.resource}/api/v1/ViralPrepLots"
            f"?order=1&orderBy=id"
            f"&searchFields=lot"
            f"&search=12345"
        )

        self.assertEqual(result.json()["data"][0]["lot"], "12345")
        mock_get.assert_called_once_with(
            expected_url, headers=self.tars_client._headers
        )

    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_prep_lot_response"
    )
    @patch(
        "aind_metadata_service.tars.mapping.TarsResponseHandler."
        "map_response_to_injection_materials"
    )
    def test_get_injection_materials_info_success(
        self, mock_map_response, mock_get_prep_lot_response
    ):
        """Tests that ModelResponse is created successfully."""
        mock_get_prep_lot_response.return_value = {
            "data": [
                {
                    "lot": "12345",
                    "datePrepped": "2023-12-15T12:34:56Z",
                    "viralPrep": {
                        "viralPrepType": {"name": "Crude-SOP#VC002"},
                        "virus": {
                            "aliases": [
                                {"name": "AiP123"},
                                {"name": "AiV456"},
                                {"name": "rAAV-MGT_789"},
                            ]
                        },
                    },
                }
            ]
        }
        mock_map_response.return_value = self.expected_materials
        result = self.tars_client.get_injection_materials_info(
            "your_prep_lot_number"
        )
        expected_response = ModelResponse(
            aind_models=self.expected_materials,
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(result.aind_models, expected_response.aind_models)
        self.assertEqual(result.status_code, expected_response.status_code)

    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_prep_lot_response"
    )
    @patch("logging.error")
    def test_get_injection_materials_info_connection_error(
        self, mock_log_error: MagicMock, mock_get_prep_lot_response: MagicMock
    ):
        """Tests that connection error is returned as expected."""
        mock_get_prep_lot_response.side_effect = ConnectionError(
            "Connection error"
        )

        # Call the method you want to test
        result = self.tars_client.get_injection_materials_info(
            "your_prep_lot_number"
        )

        # Assert that the ModelResponse for connection error is returned
        expected_response = ModelResponse.connection_error_response()
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.aind_models, expected_response.aind_models)
        self.assertEqual(result.message, expected_response.message)
        mock_log_error.assert_called_once_with(
            "ConnectionError('Connection error')"
        )

    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_prep_lot_response"
    )
    @patch("logging.error")
    def test_get_injection_materials_info_internal_error(
        self, mock_log_error: MagicMock, mock_get_prep_lot_response: MagicMock
    ):
        """Tests that Internal Error Response is returned as expected."""
        mock_get_prep_lot_response.side_effect = Exception("Some server error")

        result = self.tars_client.get_injection_materials_info(
            "your_prep_lot_number"
        )

        expected_response = ModelResponse.internal_server_error_response()
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.aind_models, expected_response.aind_models)
        self.assertEqual(result.message, expected_response.message)
        mock_log_error.assert_called_once_with(
            "Exception('Some server error')"
        )


if __name__ == "__main__":
    unittest.main()
