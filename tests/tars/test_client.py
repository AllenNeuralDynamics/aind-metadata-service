"""Module to test TARS Client methods"""

import os
import unittest
from unittest.mock import patch

from aind_metadata_service.tars.client import (
    AzureSettings,
    TarsClient,
)


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
        self.azure_settings = AzureSettings(
            tenant_id="your_tenant_id",
            client_id="your_client_id",
            client_secret="your_client_secret",
            scope="your_scope",
        )

        # Create a mock resource string for testing
        self.resource = "https://your_resource"

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def test_get_access_token(self, mock_credential):
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)

        # Ensure that get_access_token returns the expected token value
        expected_token = "mock_token"
        self.assertEqual(tars_client.get_access_token, expected_token)

    @patch("aind_metadata_service.tars.client.ClientSecretCredential")
    def test_get_headers(self, mock_credential):
        mock_credential.return_value.get_token.return_value = (
            "mock_token",
            "mock_exp",
        )
        tars_client = TarsClient(self.azure_settings, self.resource)
        expected_headers = {"Authorization": "Bearer mock_token"}
        self.assertEqual(tars_client.get_headers, expected_headers)


if __name__ == "__main__":
    unittest.main()
