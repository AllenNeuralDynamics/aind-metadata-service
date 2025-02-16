"""Module for slims client"""

import json
import logging
from datetime import datetime
from typing import Optional, Union

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.rig import Rig
from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from aind_slims_api.operations import (
    fetch_ecephys_sessions,
    fetch_histology_procedures,
)
from fastapi.responses import JSONResponse
from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings
from requests.models import Response
from slims import criteria
from slims.criteria import equals

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.slims.imaging.handler import SlimsImagingHandler
from aind_metadata_service.slims.imaging.mapping import SlimsSpimMapper
from aind_metadata_service.slims.procedures.mapping import SlimsHistologyMapper
from aind_metadata_service.slims.sessions.mapping import SlimsSessionMapper


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


class SlimsHandler:
    """Client to connect to slims db"""

    def __init__(self, settings: SlimsSettings):
        """Class constructor for slims client"""
        self.client = SlimsClient(
            username=settings.username,
            password=settings.password.get_secret_value(),
            url=settings.host,
        )

    @staticmethod
    def _is_json_file(file: Response) -> bool:
        """Checks whether file is a json."""
        return file.headers.get("Content-Type", "") == "application/json"

    def get_instrument_model_response(
        self, input_id: str, partial_match: bool = False
    ) -> ModelResponse:
        """
        Fetches a response from SLIMS, extracts Instrument models from the
        response and creates a ModelResponse with said models.
        """
        try:
            if partial_match:
                inst = self.client.fetch_model(
                    SlimsInstrumentRdrc,
                    criteria.contains("name", input_id),
                )
                attachment = self.client.fetch_attachment(
                    inst,
                )
            else:
                inst = self.client.fetch_model(
                    SlimsInstrumentRdrc, name=input_id
                )
                attachment = self.client.fetch_attachment(
                    inst, equals("name", input_id)
                )
            if attachment:
                attachment_response = self.client.fetch_attachment_content(
                    attachment
                )
                if (
                    attachment_response.status_code == 200
                    and self._is_json_file(attachment_response)
                ):
                    model = Instrument.model_construct(
                        **attachment_response.json()
                    )
                    return ModelResponse(
                        aind_models=[model],
                        status_code=StatusCodes.DB_RESPONDED,
                    )
                elif attachment_response.status_code == 401:
                    return ModelResponse.connection_error_response()
                else:
                    return ModelResponse.internal_server_error_response()
        except SlimsRecordNotFound:
            return ModelResponse.no_data_found_error_response()
        # Handles case where we might gt an exception from GET request
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_rig_model_response(
        self, input_id: str, partial_match: bool = False
    ) -> ModelResponse:
        """
        Fetches a response from SLIMS, extracts Rig models from the
        response and creates a ModelResponse with said models.
        """
        try:
            if partial_match:
                inst = self.client.fetch_model(
                    SlimsInstrumentRdrc,
                    criteria.contains("name", input_id),
                )
                attachment = self.client.fetch_attachment(
                    inst,
                )
            else:
                inst = self.client.fetch_model(
                    SlimsInstrumentRdrc, name=input_id
                )
                attachment = self.client.fetch_attachment(
                    inst, equals("name", input_id)
                )
            if attachment:
                attachment_response = self.client.fetch_attachment_content(
                    attachment
                )
                if attachment_response.status_code == 200:
                    model = Rig.model_construct(**attachment_response.json())
                    return ModelResponse(
                        aind_models=[model],
                        status_code=StatusCodes.DB_RESPONDED,
                    )
                elif attachment_response.status_code == 401:
                    return ModelResponse.connection_error_response()
                else:
                    return ModelResponse.internal_server_error_response()
        except SlimsRecordNotFound:
            return ModelResponse.no_data_found_error_response()
        # Handles exception from GET request
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_sessions_model_response(self, subject_id: str) -> ModelResponse:
        """
        Fetches sessions for a given subject ID from SLIMS.
        """
        try:
            sessions = fetch_ecephys_sessions(
                subject_id=subject_id, client=self.client
            )
            if sessions:
                mapper = SlimsSessionMapper()
                mapped_sessions = mapper.map_sessions(sessions, subject_id)
                return ModelResponse(
                    aind_models=mapped_sessions,
                    status_code=StatusCodes.DB_RESPONDED,
                )
            else:
                return ModelResponse.no_data_found_error_response()
        except SlimsRecordNotFound:
            return ModelResponse.no_data_found_error_response()
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    def get_specimen_procedures_model_response(
        self, specimen_id: str
    ) -> ModelResponse:
        """
        Fetches specimen procedures for a given specimen ID from SLIMS.
        """
        try:
            procs = fetch_histology_procedures(
                specimen_id=specimen_id, client=self.client
            )
            if procs:
                mapper = SlimsHistologyMapper()
                mapped_procedures = mapper.map_specimen_procedures(
                    procs, specimen_id
                )
                procedures = Procedures.model_construct(subject_id=specimen_id)
                procedures.specimen_procedures = mapped_procedures
                return ModelResponse(
                    aind_models=[procedures],
                    status_code=StatusCodes.DB_RESPONDED,
                )
            else:
                return ModelResponse.no_data_found_error_response()
        except SlimsRecordNotFound:
            return ModelResponse.no_data_found_error_response()
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()

    @staticmethod
    def _parse_date(
        date_str: Optional[str],
    ) -> Union[Optional[datetime], ModelResponse]:
        """Parse a date_str to datetime object or return a Bad Request
        response"""
        if date_str is None:
            return None
        else:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt
            except ValueError:
                return ModelResponse.bad_request_error_response(
                    message=f"{date_str} is not valid ISOFormat!"
                )

    def get_slims_imaging_response(
        self,
        subject_id: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> JSONResponse:
        """

        Parameters
        ----------
        subject_id : str | None
        start_date : str | None
          Optional ISO Format datetime string
        end_date :  str | None
          Optional ISO Format datetime string
        Returns
        -------
        JSONResponse

        """
        if subject_id is not None and subject_id == "":
            return ModelResponse.bad_request_error_response(
                message="subject_id cannot be an empty string!"
            ).map_to_json_response()
        parsed_start_date = self._parse_date(start_date)
        if isinstance(parsed_start_date, ModelResponse):
            return parsed_start_date.map_to_json_response()
        parsed_end_date = self._parse_date(end_date)
        if isinstance(parsed_end_date, ModelResponse):
            return parsed_end_date.map_to_json_response()
        try:
            slims_imaging_handler = SlimsImagingHandler(client=self.client.db)
            slims_spim_data = slims_imaging_handler.get_spim_data_from_slims(
                subject_id=subject_id,
                start_date_greater_than_or_equal=parsed_start_date,
                end_date_less_than_or_equal=parsed_end_date,
            )
            spim_data = SlimsSpimMapper(
                slims_spim_data=slims_spim_data
            ).map_info_from_slims()
            if len(spim_data) == 0:
                m = ModelResponse.no_data_found_error_response()
                return m.map_to_json_response()
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Data from SLIMS",
                        "data": [
                            json.loads(m.model_dump_json()) for m in spim_data
                        ],
                    }
                ),
            )
            return response
        except Exception as e:
            logging.exception(e)
            m = ModelResponse.internal_server_error_response()
            return m.map_to_json_response()
