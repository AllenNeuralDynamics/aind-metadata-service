"""Module for slims client"""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Union

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.rig import Rig
from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from fastapi.responses import JSONResponse
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict
from requests.models import Response
from slims import criteria
from slims.criteria import equals

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.settings import ParameterStoreBaseSettings
from aind_metadata_service.slims.ecephys.handler import SlimsEcephysHandler
from aind_metadata_service.slims.ecephys.mapping import SlimsEcephysMapper
from aind_metadata_service.slims.histology.handler import SlimsHistologyHandler
from aind_metadata_service.slims.histology.mapping import SlimsHistologyMapper
from aind_metadata_service.slims.imaging.handler import SlimsImagingHandler
from aind_metadata_service.slims.imaging.mapping import SlimsSpimMapper
from aind_metadata_service.slims.viral_injection.handler import (
    SlimsViralInjectionHandler,
)
from aind_metadata_service.slims.viral_injection.mapping import (
    SlimsViralInjectionMapper,
)
from aind_metadata_service.slims.water_restriction.handler import (
    SlimsWaterRestrictionHandler,
)
from aind_metadata_service.slims.water_restriction.mapping import (
    SlimsWaterRestrictionMapper,
)


class SlimsSettings(ParameterStoreBaseSettings):
    """Configuration class. Mostly a wrapper around smartsheet.Smartsheet
    class constructor arguments."""

    model_config = SettingsConfigDict(
        env_prefix="SLIMS_",
        extra="ignore",
        aws_param_store_name=os.getenv("AWS_PARAM_STORE_NAME"),
    )

    username: str = Field(..., description="User name")
    password: SecretStr = Field(..., description="Password")
    host: str = Field(..., description="host")
    db: str = Field(default="slims", description="Database")


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

    def get_histology_procedures_model_response(
        self,
        subject_id: str,
    ) -> ModelResponse:
        """
        Parameters
        ----------
        subject_id : str | None
        Returns
        -------
        JSONResponse

        """
        try:
            slims_histology_handler = SlimsHistologyHandler(
                client=self.client.db
            )
            slims_hist_data = slims_histology_handler.get_hist_data_from_slims(
                subject_id=subject_id,
            )
            if slims_hist_data:
                mapped_histology_procedures = SlimsHistologyMapper(
                    slims_hist_data=slims_hist_data
                ).map_slims_info_to_specimen_procedures()
                procedures = Procedures.model_construct(subject_id=subject_id)
                procedures.specimen_procedures = mapped_histology_procedures
                return ModelResponse(
                    aind_models=[procedures],
                    status_code=StatusCodes.DB_RESPONDED,
                )
            else:
                return ModelResponse.no_data_found_error_response()
        except Exception as e:
            logging.exception(e)
            return ModelResponse.internal_server_error_response()

    def get_slims_ecephys_response(
        self,
        subject_id: Optional[str],
        session_name: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> JSONResponse:
        """

        Parameters
        ----------
        subject_id : str | None
        session_name : str | None
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
            slims_ecephys_handler = SlimsEcephysHandler(client=self.client.db)
            slims_ephys_data = slims_ecephys_handler.get_ephys_data_from_slims(
                subject_id=subject_id,
                session_name=session_name,
                start_date_greater_than_or_equal=parsed_start_date,
                end_date_less_than_or_equal=parsed_end_date,
            )
            ephys_data = SlimsEcephysMapper(
                slims_ephys_data=slims_ephys_data
            ).map_info_from_slims()
            if len(ephys_data) == 0:
                m = ModelResponse.no_data_found_error_response()
                return m.map_to_json_response()
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Data from SLIMS",
                        "data": [
                            json.loads(m.model_dump_json()) for m in ephys_data
                        ],
                    }
                ),
            )
            return response
        except Exception as e:
            logging.exception(e)
            m = ModelResponse.internal_server_error_response()
            return m.map_to_json_response()

    def get_slims_histology_response(
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
            slims_histology_handler = SlimsHistologyHandler(
                client=self.client.db
            )
            slims_hist_data = slims_histology_handler.get_hist_data_from_slims(
                subject_id=subject_id,
                start_date_greater_than_or_equal=parsed_start_date,
                end_date_less_than_or_equal=parsed_end_date,
            )
            hist_data = SlimsHistologyMapper(
                slims_hist_data=slims_hist_data
            ).map_info_from_slims()
            if len(hist_data) == 0:
                m = ModelResponse.no_data_found_error_response()
                return m.map_to_json_response()
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Data from SLIMS",
                        "data": [
                            json.loads(m.model_dump_json()) for m in hist_data
                        ],
                    }
                ),
            )
            return response
        except Exception as e:
            logging.exception(e)
            m = ModelResponse.internal_server_error_response()
            return m.map_to_json_response()

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

    def get_slims_water_restriction_response(
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
            slims_wr_handler = SlimsWaterRestrictionHandler(
                client=self.client.db
            )
            slims_wr_data = (
                slims_wr_handler.get_water_restriction_data_from_slims(
                    subject_id=subject_id,
                    start_date_greater_than_or_equal=parsed_start_date,
                    end_date_less_than_or_equal=parsed_end_date,
                )
            )
            wr_data = SlimsWaterRestrictionMapper(
                slims_wr_data=slims_wr_data
            ).map_info_from_slims()
            if len(wr_data) == 0:
                m = ModelResponse.no_data_found_error_response()
                return m.map_to_json_response()
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Data from SLIMS",
                        "data": [
                            json.loads(m.model_dump_json()) for m in wr_data
                        ],
                    }
                ),
            )
            return response
        except Exception as e:
            logging.exception(e)
            m = ModelResponse.internal_server_error_response()
            return m.map_to_json_response()

    def get_water_restriction_procedures_model_response(
        self,
        subject_id: str,
    ) -> ModelResponse:
        """
        Parameters
        ----------
        subject_id : str | None
        Returns
        -------
        JSONResponse

        """
        try:
            slims_wr_handler = SlimsWaterRestrictionHandler(
                client=self.client.db
            )
            slims_wr_data = (
                slims_wr_handler.get_water_restriction_data_from_slims(
                    subject_id=subject_id,
                )
            )
            if slims_wr_data:
                mapped_wr_procedures = SlimsWaterRestrictionMapper(
                    slims_wr_data=slims_wr_data
                ).map_slims_info_to_water_restrictions()
                procedures = Procedures.model_construct(subject_id=subject_id)
                procedures.subject_procedures = mapped_wr_procedures
                return ModelResponse(
                    aind_models=[procedures],
                    status_code=StatusCodes.DB_RESPONDED,
                )
            else:
                return ModelResponse.no_data_found_error_response()
        except Exception as e:
            logging.exception(e)
            return ModelResponse.internal_server_error_response()

    def get_slims_viral_injection_response(
        self,
        subject_id: str,
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
            slims_vm_handler = SlimsViralInjectionHandler(
                client=self.client.db
            )
            slims_vm_data = (
                slims_vm_handler.get_viral_injection_info_from_slims(
                    subject_id=subject_id,
                    start_date_greater_than_or_equal=parsed_start_date,
                    end_date_less_than_or_equal=parsed_end_date,
                )
            )
            vm_data = SlimsViralInjectionMapper(
                slims_vm_data=slims_vm_data
            ).map_info_from_slims()
            if len(vm_data) == 0:
                m = ModelResponse.no_data_found_error_response()
                return m.map_to_json_response()
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Data from SLIMS",
                        "data": [
                            json.loads(m.model_dump_json()) for m in vm_data
                        ],
                    }
                ),
            )
            return response
        except Exception as e:
            logging.exception(e)
            m = ModelResponse.internal_server_error_response()
            return m.map_to_json_response()
