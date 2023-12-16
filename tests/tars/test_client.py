"""Module to test TARS Client methods"""

import os
import json
import unittest
from unittest.mock import patch
import requests_mock
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

        expected_error_message = (
            "ValidationError("
            "model='AzureSettings', "
            "errors=["
            "{'loc': ('client_secret',), 'msg': 'field required',"
            " 'type': 'value_error.missing'}, "
            "{'loc': ('scope',), 'msg': 'field required',"
            " 'type': 'value_error.missing'}])"
        )

        self.assertEqual(expected_error_message, repr(e.exception))


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
    def test_get_access_token(self, mock_credential):
        """Tests that token is retrieved as expected."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)

        expected_token = "mock_token"
        self.assertEqual(tars_client.get_access_token, expected_token)

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def test_get_headers(self, mock_credential):
        """Tests that headers is created as expected."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)
        expected_headers = {"Authorization": "Bearer mock_token"}
        self.assertEqual(tars_client.get_headers, expected_headers)

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    # @patch('aind_metadata_service.tars.client.requests.get')
    # @patch("aind_metadata_service.tars.client.TarsResponseHandler.map_response_to_injection_materials")
    def test_get_injection_materials_info(self, mock_credential):
        """Tests that client can fetch injection materials."""
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)
        url_query = "https://some_resource/api/v1/ViralPrepLots?" \
                    "order=1&orderBy=id&searchFields=lot&search=12345"

        with requests_mock.mock() as mock_request:
            mock_get_response = {
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

            mock_request.get(
                url_query,
                text=json.dumps(mock_get_response),
            )
            result = tars_client.get_injection_materials_info("12345")

        self.assertEqual(result.name, "rAAV-MGT_789")
        self.assertEqual(result.prep_protocol, "SOP#VC002")
        mock_credential.return_value.get_token.assert_called_once()


if __name__ == "__main__":
    unittest.main()
