"""Module to handle responses"""

import json
import pickle
from typing import Generic, List, Optional, TypeVar, Union

from aind_data_schema.core.data_description import Funding
from aind_data_schema.core.procedures import (
    NonViralMaterial,
    Perfusion,
    Procedures,
    Surgery,
    ViralMaterial,
)
from aind_data_schema.core.subject import Subject
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes

T = TypeVar(
    "T",
    Subject,
    Procedures,
    Funding,
    Perfusion,
    Surgery,
    ViralMaterial,
    NonViralMaterial,
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

    def _map_data_response(
        self, pickled: bool = False
    ) -> Union[Response, JSONResponse]:
        """Map ModelResponse with StatusCodes.DB_RESPONDED to a JSONResponse.
        Perform validations."""
        if len(self.aind_models) == 0:
            status_code = StatusCodes.NO_DATA_FOUND.value
            content_data = None
            message = "No Data Found."
        elif len(self.aind_models) == 1:
            aind_model = self.aind_models[0]
            # TODO: fix validation error catching
            validation_error = None
            try:
                aind_model.__class__.model_validate(aind_model.model_dump())
            except ValidationError as e:
                validation_error = repr(e)
            if pickled:
                content_data = aind_model
            else:
                content_data = jsonable_encoder(
                    json.loads(aind_model.model_dump_json())
                )
            if validation_error:
                status_code = StatusCodes.INVALID_DATA.value
                message = f"Validation Errors: {validation_error}"
            else:
                status_code = StatusCodes.VALID_DATA.value
                message = "Valid Model."
            if self.status_code == StatusCodes.MULTI_STATUS:
                status_code = self.status_code.value
                message = (
                    "There was an error retrieving records from one or more of"
                    " the databases."
                )

        else:
            status_code = StatusCodes.MULTIPLE_RESPONSES.value
            message = "Multiple Items Found."
            if pickled:
                content_data = self.aind_models
            else:
                content_data = [
                    jsonable_encoder(json.loads(model.model_dump_json()))
                    for model in self.aind_models
                ]
        if pickled:
            return Response(
                status_code=status_code,
                content=pickle.dumps(content_data),
                media_type="application/octet-stream",
            )
        else:
            return JSONResponse(
                status_code=status_code,
                content=({"message": message, "data": content_data}),
            )

    def map_to_json_response(self) -> JSONResponse:
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
            response = self._map_data_response()
        return response

    def map_to_pickled_response(self) -> Response:
        """Map a ModelResponse to a pickled response."""

        if self.status_code != StatusCodes.DB_RESPONDED:
            response = Response(
                status_code=self.status_code.value,
                content=pickle.dumps(None),
                media_type="application/octet-stream",
            )
        else:
            response = self._map_data_response(pickled=True)
        return response
