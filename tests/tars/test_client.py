"""Module to test TARS Client methods"""

import os
import unittest
from unittest.mock import Mock, patch

from aind_metadata_service.tars.client import AzureSettings, TarsClient


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

        self.assertIn("2 validation errors for AzureSettings", repr(e.exception))


class TestTarsClient(unittest.TestCase):
    """Tests client methods"""

    def setUp(self):
        """Sets up Test TarsClient methods"""
        self.azure_settings = AzureSettings(
            tenant_id="some_tenant_id",
            client_id="some_client_id",
            client_secret="some_client_secret",
            scope="some_scope",
        )

        self.resource = "https://some_resource"

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def test_access_token(self, mock_credential):
        """Tests that token is retrieved as expected."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)

        expected_token = "mock_token"
        self.assertEqual(tars_client._access_token, expected_token)

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def test_headers(self, mock_credential):
        """Tests that headers is created as expected."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)
        expected_headers = {"Authorization": "Bearer mock_token"}
        self.assertEqual(tars_client._headers, expected_headers)

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    @patch("aind_metadata_service.tars.client.requests.get")
    def test_get_prep_lot_response(self, mock_get, mock_credential):
        """Tests that client can fetch viral prep lot."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)

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
        result = tars_client.get_prep_lot_response("12345")
        expected_url = (
            f"{tars_client.resource}/api/v1/ViralPrepLots"
            f"?order=1&orderBy=id"
            f"&searchFields=lot"
            f"&search=12345"
        )

        self.assertEqual(result.json()["data"][0]["lot"], "12345")
        mock_credential.return_value.get_token.assert_called_once()
        mock_get.assert_called_once_with(
            expected_url, headers=tars_client._headers
        )


if __name__ == "__main__":
    unittest.main()
