"""Module to test TARS Client methods"""

import os
import unittest
from datetime import date
from unittest.mock import MagicMock, Mock, patch

from aind_data_schema.core.procedures import (
    TarsVirusIdentifiers,
    ViralMaterial,
)

from aind_metadata_service.response_handler import ModelResponse, StatusCodes
from aind_metadata_service.tars.client import AzureSettings, TarsClient


class TestAzureSettings(unittest.TestCase):
    """Class to test methods for AzureSettings."""

    EXAMPLE_ENV_VAR1 = {
        "TARS_TENANT_ID": "some_tenant",
        "TARS_CLIENT_ID": "some_client",
        "TARS_RESOURCE": "some_resource",
        "TARS_CLIENT_SECRET": "some_secret",
        "TARS_SCOPE": "some_scope",
    }

    @patch.dict(os.environ, EXAMPLE_ENV_VAR1, clear=True)
    def test_settings_set_from_env_vars(self):
        """Tests that the settings can be set from env vars."""
        settings1 = AzureSettings()

        self.assertEqual("some_tenant", settings1.tenant_id)
        self.assertEqual("some_client", settings1.client_id)
        self.assertEqual("some_resource", settings1.resource)
        self.assertEqual("some_scope", settings1.scope)
        self.assertEqual(
            "some_secret",
            settings1.client_secret.get_secret_value(),
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_errors(self):
        """Tests that errors are raised if settings are incorrect."""

        with self.assertRaises(ValueError) as e:
            AzureSettings(
                client_id="some_client",
                tenant_id="some_tenant",
            )
        self.assertIn(
            "3 validation errors for AzureSettings", repr(e.exception)
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
            resource="https://some_resource",
        )
        tars_virus_identifiers = TarsVirusIdentifiers(
            virus_tars_id="AiV456",
            plasmid_tars_alias="AiP123",
            prep_lot_number="12345",
            prep_date=date(2023, 12, 15),
            prep_type="Crude",
            prep_protocol="SOP#VC002",
        )

        viral_material = ViralMaterial(
            name="rAAV-MGT_789", tars_identifiers=tars_virus_identifiers
        )

        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        self.expected_materials = viral_material
        self.tars_client = TarsClient(self.azure_settings)

    def test_access_token(self):
        """Tests that token is retrieved as expected."""
        expected_token = "mock_token"
        self.assertEqual(self.tars_client._access_token, expected_token)

    def test_headers(self):
        """Tests that headers is created as expected."""
        expected_headers = {"Authorization": "Bearer mock_token"}
        self.assertEqual(self.tars_client._headers, expected_headers)

    @patch("aind_metadata_service.tars.client.requests.get")
    def test_get_prep_lot_response_success(self, mock_get):
        """Tests that client can fetch viral prep lot."""

        mock_response = Mock()

        mock_response.json.return_value = {
            "data": [
                {
                    "lot": "VT12345",
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
        result = self.tars_client._get_prep_lot_response("VT12345")
        expected_url = (
            f"{self.azure_settings.resource}/api/v1/ViralPrepLots"
            f"?order=1&orderBy=id"
            f"&searchFields=lot"
            f"&search=VT12345"
        )

        self.assertEqual(result.json()["data"][0]["lot"], "VT12345")
        mock_get.assert_called_once_with(
            expected_url, headers=self.tars_client._headers
        )

    def test_get_prep_lot_response_failure(self):
        """Tests that exception is raised as expected"""
        with self.assertRaises(ValueError) as context:
            self.tars_client._get_prep_lot_response(prep_lot_number="")

        self.assertEqual(
            "Please input a valid prep lot number.",
            str(context.exception),
        )

    def test_filter_prep_lot_response(self):
        """Tests that response data is filtered for exact matches"""
        mock_response = MagicMock()
        mock_response.return_value.json.return_value = {
            "data": [
                {
                    "lot": "VT1",
                    "datePrepped": "2023-12-15T12:34:56Z",
                },
                {
                    "lot": "VT2",
                    "datePrepped": "2023-12-15T12:34:56Z",
                },
                {
                    "lot": "VT3",
                    "datePrepped": "2023-12-15T12:34:56Z",
                },
            ]
        }
        with self.assertRaises(ValueError) as context:
            self.tars_client._filter_prep_lot_response(
                prep_lot_number="VT", response=mock_response
            )

        self.assertEqual("No data found for VT", str(context.exception))

    @patch("aind_metadata_service.tars.client.requests.get")
    def test_get_molecules_response(self, mock_get):
        """Tests that client can fetch viral prep lot."""

        mock_response = Mock()

        mock_response.json.return_value = {
            "data": [
                {"aliases": [{"name": "AiP123"}, {"name": "rAAV-MGT_789"}]}
            ]
        }
        mock_get.return_value = mock_response
        result = self.tars_client._get_molecules_response("AiP123")
        expected_url = (
            f"{self.azure_settings.resource}/api/v1/Molecules"
            f"?order=1&orderBy=id"
            f"&searchFields=name"
            f"&search=AiP123"
        )

        self.assertEqual(
            result.json()["data"][0]["aliases"][0]["name"], "AiP123"
        )
        mock_get.assert_called_once_with(
            expected_url, headers=self.tars_client._headers
        )

    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_prep_lot_response"
    )
    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_molecules_response"
    )
    def test_get_injection_materials_info_success(
        self, mock_molecules_response, mock_get_prep_lot_response
    ):
        """Tests that ModelResponse is created successfully."""
        mock_get_prep_lot_response.return_value.json.return_value = {
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
                            ]
                        },
                    },
                }
            ]
        }
        mock_molecules_response.return_value.json.return_value = {
            "data": [
                {"aliases": [{"name": "AiP123"}, {"name": "rAAV-MGT_789"}]}
            ]
        }

        result = self.tars_client.get_injection_materials_info("12345")
        expected_response = ModelResponse(
            aind_models=[self.expected_materials],
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(
            expected_response.aind_models,
            result.aind_models,
        )
        self.assertEqual(
            expected_response.status_code,
            result.status_code,
        )

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

    @patch(
        "aind_metadata_service.tars.client.TarsClient._get_prep_lot_response"
    )
    @patch("logging.error")
    def test_get_injection_materials_info_no_data_found_error(
        self, mock_log_error: MagicMock, mock_get_prep_lot_response: MagicMock
    ):
        """Tests that Internal Error Response is returned as expected."""
        mock_get_prep_lot_response.return_value.json.return_value = {
            "data": []
        }

        result = self.tars_client.get_injection_materials_info(
            "some_invalid_number"
        )

        expected_response = ModelResponse.no_data_found_error_response()
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.aind_models, expected_response.aind_models)
        self.assertEqual(result.message, expected_response.message)
        mock_log_error.assert_called_once_with(
            "ValueError('No data found for some_invalid_number')"
        )


if __name__ == "__main__":
    unittest.main()
