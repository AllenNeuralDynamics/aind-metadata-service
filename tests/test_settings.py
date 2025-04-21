"""Module to test custom settings"""

import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from aind_metadata_service.settings import (
    AWSParamStoreSource,
    ParameterStoreBaseSettings,
)


class ExampleSettings(ParameterStoreBaseSettings):
    """Example settings class for testing"""

    my_secret: str

    model_config = {
        "aws_param_store_name": "example-name",
        "case_sensitive": False,
    }


class TestAWSParamStoreSource(unittest.TestCase):
    """Test AWSParamStoreSource class"""

    @patch("aind_metadata_service.settings.boto3.client")
    def test_get_parameter(self, mock_boto_client):
        """Tests that parameter is retrieved as expected"""
        # Mock response
        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {
            "Parameter": {"Value": '{"my_secret": "secret_value"}'}
        }
        mock_boto_client.return_value = mock_ssm

        result = AWSParamStoreSource._get_parameter("example-name")
        self.assertEqual(result, {"my_secret": "secret_value"})
        mock_ssm.get_parameter.assert_called_once_with(
            Name="example-name", WithDecryption=True
        )
        mock_ssm.close.assert_called_once()

    def test_find_case_param(self):
        """Tests that correct parameter is found in json dictionary"""

        json_contents = {"keyOne": "value1", "KEYTWO": "value2"}
        result1 = AWSParamStoreSource.find_case_param(
            json_contents, "keyOne", case_sensitive=False
        )
        result2 = AWSParamStoreSource.find_case_param(
            json_contents, "keytwo", case_sensitive=False
        )
        result3 = AWSParamStoreSource.find_case_param(
            json_contents, "keytwo", case_sensitive=True
        )

        self.assertEqual(result1, "value1")
        self.assertEqual(result2, "value2")
        self.assertIsNone(result3)

    @patch.object(
        AWSParamStoreSource, "_json_contents", new_callable=PropertyMock
    )
    def test_get_field_value_success(self, mock_json_contents):
        """Tests that field value is retrieved successfully"""

        mock_json_contents.return_value = {"MY_SECRET": "topsecret"}
        source = AWSParamStoreSource(
            ExampleSettings, aws_param_store_name="example-store-name"
        )
        field = ExampleSettings.model_fields["my_secret"]

        value, key, is_complex = source.get_field_value(field, "my_secret")
        self.assertEqual(value, "topsecret")
        self.assertEqual(key, "my_secret")
        self.assertFalse(is_complex)

    @patch.object(
        AWSParamStoreSource, "_json_contents", new_callable=PropertyMock
    )
    def test_get_field_value_failure(self, mock_json_contents):
        """Tests that field value is not retrieved successfully"""

        mock_json_contents.return_value = {}
        source = AWSParamStoreSource(
            ExampleSettings, aws_param_store_name="example-store-name"
        )
        field = ExampleSettings.model_fields["my_secret"]

        value, key, is_complex = source.get_field_value(field, "my_secret")
        self.assertIsNone(value)
        self.assertEqual(key, "my_secret")
        self.assertFalse(is_complex)


class TestParameterStoreBaseSettings(unittest.TestCase):
    """Test ParameterStoreBaseSettings class"""

    def test_settings_customise_sources_with_param_store(self):
        """Tests that sources are customised correctly"""
        init = MagicMock()
        env = MagicMock()
        dotenv = MagicMock()
        secret = MagicMock()
        sources = ParameterStoreBaseSettings.settings_customise_sources(
            settings_cls=ExampleSettings,
            init_settings=init,
            env_settings=env,
            dotenv_settings=dotenv,
            file_secret_settings=secret,
        )
        print(sources)
        self.assertIsInstance(sources[1], AWSParamStoreSource)

    def test_settings_customise_sources_without_param_store(self):
        """Tests that sources are customised correctly"""

        class NoParamSettings(ParameterStoreBaseSettings):
            """Example settings class for testing no param store"""

            model_config = {}

        init = MagicMock()
        env = MagicMock()
        dotenv = MagicMock()
        secret = MagicMock()

        sources = NoParamSettings.settings_customise_sources(
            NoParamSettings, init, env, dotenv, secret
        )
        self.assertEqual(sources[0], init)
        self.assertEqual(len(sources), 4)


if __name__ == "__main__":
    unittest.main()
