"""Module to handle responses"""
import json
import pickle
from typing import Generic, List, Optional, TypeVar, Union

from aind_data_schema.procedures import Procedures
from aind_data_schema.subject import Subject
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import validate_model

from aind_metadata_service.client import StatusCodes

T = TypeVar("T", Subject, Procedures)


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
            *_, validation_error = validate_model(
                aind_model.__class__, aind_model.__dict__
            )
            if pickled:
                content_data = aind_model
            else:
                content_data = jsonable_encoder(json.loads(aind_model.json()))
            if validation_error:
                status_code = StatusCodes.INVALID_DATA.value
                message = f"Validation Errors: {validation_error}"
            else:
                status_code = StatusCodes.VALID_DATA.value
                message = "Valid Model."
        else:
            status_code = StatusCodes.MULTIPLE_RESPONSES.value
            message = "Multiple Items Found."
            if pickled:
                content_data = self.aind_models
            else:
                content_data = [
                    jsonable_encoder(json.loads(model.json()))
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
