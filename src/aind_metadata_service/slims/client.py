"""Module for slims client"""

import logging
from typing import Any, List

import requests
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig
from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings
from requests.models import Response
from slims.criteria import equals
from slims.internal import Record
from slims.slims import Slims

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.slims.models import ContentsTableRow


class SlimsSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around smartsheet.Smartsheet
    class constructor arguments."""

    username: str = Field(..., description="User name")
    password: SecretStr = Field(..., description="Password")
    host: str = Field(..., description="host")
    db: str = Field(default="slims", description="Database")

    class Config:
        """Set env prefix and forbid extra fields."""

        env_prefix = "SLIMS_"
        extra = Extra.forbid


class SlimsClient:
    """Client to connect to slims db"""

    def __init__(self, settings: SlimsSettings):
        """Class constructor for slims client"""
        self.settings = settings
        self.client = Slims(
            settings.db,
            settings.host,
            settings.username,
            settings.password.get_secret_value(),
        )

    def get_content_record(self, subject_id: str) -> Record:
        """
        Retrieve a record from the Contents Table using Slims API
        Parameters
        ----------
        subject_id : str
          Labtracks id of subject to retrieve record for

        Returns
        -------
        Record
          A single slims Record

        """
        try:
            content_record = self.client.fetch(
                "Content",
                equals(
                    ContentsTableRow.model_fields["cntn_cf_labtracksId"].title,
                    subject_id,
                ),
                start=0,
                end=1,
            )[0]
            return content_record
        except Exception as e:
            logging.error(repr(e))
            raise Exception(e)

    def _get_response(
        self, url: str, body: dict[str, Any] = None, slims_api=None
    ) -> Response:
        """Method to get some response from slims"""
        slims_api = slims_api or self.client.slims_api
        if not url.startswith(slims_api.url):
            url = slims_api.url + url

        if slims_api.oauth:
            response = slims_api.oauth_session.get(
                url,
                headers=slims_api._headers(),
                json=body,
                **slims_api.request_params,
            )
        else:
            assert (
                slims_api.username is not None
                and slims_api.password is not None
            )
            response = requests.get(
                url,
                auth=(slims_api.username, slims_api.password),
                headers=slims_api._headers(),
                json=body,
                **slims_api.request_params,
            )
        return response

    def get_record_response(self, table_name: str, criteria: Any) -> Response:
        """Fetches the response for a record in a SLIMS table."""
        body: dict[str, Any] = {
            "sortBy": None,
            "startRow": None,
            "endRow": None,
        }
        if criteria:
            body["criteria"] = criteria.to_dict()

        url = f"{table_name}/advanced"
        return self._get_response(url, body=body)

    def get_attachment_response(self, entity: dict[str, Any]) -> Response:
        """
        Fetches the attachments related to a record in a SLIMS table.
        """
        return self._get_response(
            f"attachment/{entity['tableName']}/{entity['pk']}"
        )

    def get_file_response(self, entity):
        """Fetches the file related to an attachment."""
        return self._get_response(f"repo/{entity['pk']}")

    @staticmethod
    def _is_json_file(file: Response) -> bool:
        """Checks whether file is a json."""
        return file.headers.get("Content-Type", "") == "application/json"

    def extract_instrument_models_from_response(
        self, response: Response
    ) -> List[Instrument]:
        """
        Fetches Attachment from SLIMS Instrument Response and extracts
        aind_data_schema Instrument models.
        """
        models = []
        for entity in response.json().get("entities", []):
            attachment_response = self.get_attachment_response(entity)
            if attachment_response.status_code == 200:
                for att_entity in attachment_response.json().get(
                    "entities", []
                ):
                    file_response = self.get_file_response(att_entity)
                    if (
                        file_response.status_code == 200
                        and self._is_json_file(file_response)
                    ):
                        inst = Instrument.model_construct(
                            **file_response.json()
                        )
                        models.append(inst)
        return models

    def extract_rig_models_from_response(
        self, response: Response
    ) -> List[Rig]:
        """
        Fetches Attachment from SLIMS Instrument Response and extracts
        aind_data_schema Rig models.
        """
        models = []
        for entity in response.json().get("entities", []):
            attachment_response = self.get_attachment_response(entity)
            if attachment_response.status_code == 200:
                for att_entity in attachment_response.json().get(
                    "entities", []
                ):
                    file_response = self.get_file_response(att_entity)
                    if (
                        file_response.status_code == 200
                        and self._is_json_file(file_response)
                    ):
                        rig = Rig.model_construct(**file_response.json())
                        models.append(rig)
        return models

    def get_instrument_model_response(self, input_id) -> ModelResponse:
        """
        Fetches a response from SLIMS, extracts Instrument models from the
        response and creates a ModelResponse with said models.
        """
        try:
            response = self.get_record_response(
                "ReferenceDataRecord", equals("rdrc_name", input_id)
            )
            if response.status_code == 200:
                models = self.extract_instrument_models_from_response(response)
                return ModelResponse(
                    aind_models=models, status_code=StatusCodes.DB_RESPONDED
                )
            elif response.status_code == 401:
                return ModelResponse.connection_error_response()
            else:
                return ModelResponse.internal_server_error_response()
        # Handles case where we might gt an exception from GET request
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_rig_model_response(self, input_id) -> ModelResponse:
        """
        Fetches a response from SLIMS, extracts Rig models from the
        response and creates a ModelResponse with said models.
        """
        try:
            response = self.get_record_response(
                "ReferenceDataRecord", equals("rdrc_name", input_id)
            )
            if response.status_code == 200:
                models = self.extract_rig_models_from_response(response)
                return ModelResponse(
                    aind_models=models, status_code=StatusCodes.DB_RESPONDED
                )
            elif response.status_code == 401:
                return ModelResponse.connection_error_response()
            else:
                return ModelResponse.internal_server_error_response()
        # Handles case where we might gt an exception from GET request
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
