"""Module to handle responses"""

import json
from typing import Generic, List, Optional, TypeVar, Union

from aind_data_schema.core.data_description import Funding
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import (
    NonViralMaterial,
    Perfusion,
    Procedures,
    Surgery,
    ViralMaterial,
)
from aind_data_schema.core.rig import Rig
from aind_data_schema.core.subject import Subject
from aind_metadata_mapper.core import JobResponse
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ProtocolInformation

T = TypeVar(
    "T",
    Subject,
    Procedures,
    Funding,
    Perfusion,
    Surgery,
    ViralMaterial,
    NonViralMaterial,
    ProtocolInformation,
    Instrument,
    Rig,
)


class ModelResponse(Generic[T]):
    """Class to handle responses from backend databases. Holds pydantic models
    without serializing them to json or running validation checks."""

    def __init__(
        self,
        aind_models: List[T],
        status_code: StatusCodes,
        message: Optional[str] = None,
    ):
        """
        Class constructor
        Parameters
        ----------
        aind_models : List[T]
          Either a list of Subjects or a list of Procedures
        status_code : StatusCodes
        message : Optional[str]
          Message to return to client.
        """
        self.status_code = status_code
        self.aind_models = aind_models
        self.message = message

    @classmethod
    def connection_error_response(cls):
        """Connection Error"""
        return cls(
            status_code=StatusCodes.CONNECTION_ERROR,
            aind_models=[],
            message="Connection Error.",
        )

    @classmethod
    def internal_server_error_response(cls):
        """Internal Server Error"""
        return cls(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            aind_models=[],
            message="Internal Server Error.",
        )

    @classmethod
    def no_data_found_error_response(cls):
        """No Data Found Error"""
        return cls(
            status_code=StatusCodes.NO_DATA_FOUND,
            aind_models=[],
            message="No Data Found.",
        )

    def _map_data_response(  # noqa: C901
        self, validate: bool = True
    ) -> Union[Response, JSONResponse]:
        """Map ModelResponse with StatusCodes.DB_RESPONDED to a JSONResponse.
        Perform validations, bypasses validation if flag is set to False."""
        if len(self.aind_models) == 0:
            status_code = StatusCodes.NO_DATA_FOUND.value
            content_data = None
            message = "No Data Found."
        elif len(self.aind_models) == 1:
            aind_model = self.aind_models[0]
            content_data = jsonable_encoder(
                json.loads(aind_model.model_dump_json())
            )
            if validate:
                validation_error = None
                try:
                    aind_model.__class__.model_validate(
                        aind_model.model_dump()
                    )
                except ValidationError as e:
                    validation_error = repr(e)
                except (AttributeError, ValueError, KeyError) as oe:
                    validation_error = repr(oe)
                if validation_error:
                    status_code = StatusCodes.INVALID_DATA.value
                    message = f"Validation Errors: {validation_error}"
                else:
                    status_code = StatusCodes.VALID_DATA.value
                    message = "Valid Model."
            # if validate flag is False
            else:
                status_code = StatusCodes.UNPROCESSIBLE_ENTITY.value
                message = (
                    "Valid Request Format. Models have not been validated."
                )

            if self.status_code == StatusCodes.MULTI_STATUS:
                status_code = self.status_code.value
                message = (
                    "There was an error retrieving records from one or more of"
                    " the databases."
                )
        else:
            status_code = StatusCodes.MULTIPLE_RESPONSES.value
            message = "Multiple Items Found."
            content_data = [
                jsonable_encoder(json.loads(model.model_dump_json()))
                for model in self.aind_models
            ]
        return JSONResponse(
            status_code=status_code,
            content=({"message": message, "data": content_data}),
        )

    def map_to_json_response(self, validate: bool = True) -> JSONResponse:
        """Map a ModelResponse to a JSONResponse."""
        if self.status_code == StatusCodes.CONNECTION_ERROR:
            response = JSONResponse(
                status_code=StatusCodes.CONNECTION_ERROR.value,
                content=({"message": self.message, "data": None}),
            )
        elif self.status_code == StatusCodes.INTERNAL_SERVER_ERROR:
            response = JSONResponse(
                status_code=StatusCodes.INTERNAL_SERVER_ERROR.value,
                content=({"message": self.message, "data": None}),
            )
        else:
            response = self._map_data_response(validate=validate)
        return response


class EtlResponse:
    """Handle responses from EtlJobs"""

    @staticmethod
    def map_job_response(job_response: JobResponse) -> JSONResponse:
        """Map JobResponse class to JSONResponse"""
        return JSONResponse(
            status_code=job_response.status_code,
            content=(
                {"message": job_response.message, "data": job_response.data}
            ),
        )
