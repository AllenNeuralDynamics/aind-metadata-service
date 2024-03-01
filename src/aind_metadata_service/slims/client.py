"""Module for slims client"""

import logging
import requests
from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings
from slims.criteria import equals
from slims.internal import Record
from slims.slims import Slims

from aind_metadata_service.slims.models import ContentsTableRow
from typing import Any
from aind_metadata_service.response_handler import ModelResponse
from requests.models import Response
from aind_data_schema.core.instrument import Instrument
from aind_metadata_service.client import StatusCodes


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

    def _get_response(self, url: str, body: dict[str, Any] = None) -> Response:
        """Method to get some response from slims"""
        slims_api = self.client.slims_api
        if (slims_api.url.startswith('https') and url.startswith('http') and url[4:].startswith(slims_api.url[5:])):
            url = 'https' + url[4:]
        if not url.startswith(slims_api.url):
            url = slims_api.url + url

        if slims_api.oauth:
            response = slims_api.oauth_session.get(
                url, headers=slims_api._headers(), json=body, **slims_api.request_params)
        else:
            assert slims_api.username is not None and slims_api.password is not None
            response = requests.get(url,
                                    auth=(slims_api.username, slims_api.password),
                                    headers=slims_api._headers(),
                                    json=body,
                                    **slims_api.request_params)
        return response

    def get_record_response(self, table_name, criteria) -> Response:
        """Fetches the response for a record in a SLIMS table."""
        body: dict[str, Any] = {
            "sortBy": None,
            "startRow": None,
            "endRow": None,
        }
        if criteria:
            body["criteria"] = criteria.to_dict()

        url = table_name + "/advanced"
        return self._get_response(url, body=body)

    def get_attachment_response(self, entity) -> Response:
        """Fetches the response for attachments related to a record in a SLIMS table."""
        return self._get_response(
            "attachment/" + entity["tableName"] + "/" + str(entity["pk"])
        )
        # return self.client.slims_api.get("repo/" + str(entity["pk"]))

    def get_instrument_response(self, input_id):
        """
        Retrieve a response from the Instruments Table.
        (contains info for both rigs and imaging instruments).
        Parameters
        ----------
        input_id : str
            Id to retrieve record for. Either instrument_id or rig_id.

        Returns
        -------
        Record
          A single slims Record
        """
        try:
            instrument_response = self.get_record_response(
                "Instrument",
                equals(
                    "nstr_name",
                    input_id,
                )
            )
            return instrument_response

        # handles any errors in getting a response from slims
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_instrument_model_response(self, response):
        """"""
        if response.status_code == 200:
            models = []
            for entity in response.json()["entities"]:
                attachment_response = self.get_attachment_response(entity)
                if attachment_response.status_code == 200:
                    for att_entity in attachment_response.json()["entities"]:
                        # TODO: add check for json and instrument file
                        file_content = self.client.slims_api.get("repo/" + str(att_entity["pk"]))
                        inst = Instrument.model_construct(**file_content.json())
                        models.append(inst)
                elif response.status_code == 401:
                    return ModelResponse.connection_error_response()
                else:
                    return ModelResponse.internal_server_error_response()
            return ModelResponse(aind_models=models, status_code=StatusCodes.DB_RESPONDED)
        elif response.status_code == 401:
            return ModelResponse.connection_error_response()
        else:
            return ModelResponse.internal_server_error_response()




