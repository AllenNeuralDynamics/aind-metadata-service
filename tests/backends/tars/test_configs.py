"""Tests configs module"""

import os
import unittest
from unittest.mock import patch, MagicMock

from aind_metadata_service.backends.tars.configs import Settings, get_settings


class TestConfigs(unittest.TestCase):
    """Test methods in Configs Class"""

    @patch.dict(
        os.environ,
        {
            "TARS_TENANT_ID": "123-abc",
            "TARS_CLIENT_ID": "456-def",
            "TARS_CLIENT_SECRET": "my_secret",
            "TARS_SCOPE": "www.scope.example.com",
            "TARS_RESOURCE": "www.res.example.com",
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = get_settings()
        expected_settings = Settings(
            tenant_id="123-abc",
            client_id="456-def",
            client_secret="my_secret",
            scope="www.scope.example.com",
            resource="www.res.example.com",
        )
        self.assertEqual(expected_settings, settings)

    @patch(
        "aind_metadata_service.backends.tars.configs.ClientSecretCredential"
    )
    def test_get_bearer_token(self, mock_creds: MagicMock):
        """Tests get_bearer_token"""
        settings = Settings(
            tenant_id="123-abc",
            client_id="456-def",
            client_secret="my_secret",
            scope="www.scope.example.com",
            resource="www.res.example.com",
        )
        mock_creds.return_value.get_token.return_value = (
            "aaa-111-bbb-222",
            1732913004,
        )
        token, exp = settings.get_bearer_token()
        self.assertEqual("aaa-111-bbb-222", token)
        self.assertEqual(exp, 1732913004)


if __name__ == "__main__":
    unittest.main()
