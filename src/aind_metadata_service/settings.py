"""Module to handle custom settings"""

import functools
import json
import logging
from typing import Any, Dict, Tuple, Type

import boto3
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from pydantic_settings.sources import PydanticBaseEnvSettingsSource


class AWSParamStoreSource(PydanticBaseEnvSettingsSource):
    """Custom pydantic settings source pulled from AWS Param Store"""

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        aws_param_store_name: str | None = None,
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_ignore_empty: bool | None = None,
        env_parse_none_str: str | None = None,
    ) -> None:
        """Class constructor"""
        super().__init__(
            settings_cls,
            case_sensitive,
            env_prefix,
            env_ignore_empty,
            env_parse_none_str,
        )
        self.aws_param_store_name = (
            aws_param_store_name
            if aws_param_store_name is not None
            else self.config.get("aws_param_store_name")
        )

    @staticmethod
    def _get_parameter(parameter_name: str) -> Dict[str, Any]:
        """
        Retrieves a parameter file from AWS Param Store

        Parameters
        ----------
        parameter_name : str
          Parameter name as stored in AWS Param Store

        Returns
        -------
        Dict[str, Any]
          Contents of the secret

        """
        client = boto3.client("ssm")
        try:
            response = client.get_parameter(
                Name=parameter_name, WithDecryption=True
            )
        finally:
            client.close()
        return json.loads(response["Parameter"]["Value"])

    @functools.cached_property
    def _json_contents(self):
        """Cache contents to a property to avoid re-downloading."""
        contents_from_aws = self._get_parameter(
            self.config.get("aws_param_store_name")
        )
        return contents_from_aws

    @classmethod
    def find_case_param(
        cls, json_contents: dict, param_name: str, case_sensitive: bool
    ) -> str | None:
        """
        Find a parameter from a json dictionary pulled from aws

        Parameters
        ----------
          json_contents: dict
          param_name: str
          case_sensitive: bool
            Whether to search for param name case sensitively.

        Returns
        -------
          str | None
        """

        if json_contents.get(param_name) is not None:
            return json_contents.get(param_name)
        elif (
            not case_sensitive
            and json_contents.get(param_name.upper()) is not None
        ):
            return json_contents.get(param_name.upper())
        else:
            return None

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        """
        Gets the value for field from secret file and a flag to determine
        whether value is complex.

        Parameters
        ----------
          field: The field.
          field_name: The field name.

        Returns
        -------
        tuple[Any, str, bool]
          A tuple contains the key, value if the file exists otherwise `None`,
          and a flag to determine whether value is complex.
        """
        param = None
        field_key = ""
        value_is_complex = False
        for field_key, env_name, value_is_complex in self._extract_field_info(
            field, field_name
        ):
            param = self.find_case_param(
                self._json_contents, env_name, self.case_sensitive
            )
            if param:
                return param, field_key, value_is_complex
            else:
                logging.debug(f"param not found {field_key}")

        return param, field_key, value_is_complex


class ParameterStoreBaseSettings(BaseSettings):
    """Custom Settings class to handle AWS Parameter Store"""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """If the param store name is set as an env var, pull from there."""

        if settings_cls.model_config.get("aws_param_store_name") is None:
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
        else:
            return (
                init_settings,
                AWSParamStoreSource(settings_cls),
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
