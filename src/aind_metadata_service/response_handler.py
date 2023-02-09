"""Module to handle responses"""
from typing import List
from enum import Enum

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model


class Responses:
    """This class contains methods to map responses from server."""

    class StatusCodes(Enum):
        """Enum class of status codes"""
        connection_error = 503
        internal_server_error = 500
        multiple_responses = 300
        valid_data = 200
        invalid_data = 406
        no_data = 404

    def connection_error_response(self) -> JSONResponse:
        """Map to a connection error"""
        response = JSONResponse(
            status_code=self.StatusCodes.connection_error.value,
            content=({"message": "Error Connecting to Internal Server.", "data": None}),
        )
        return response

    def internal_server_error_response(self) -> JSONResponse:
        """Map to an internal server error"""
        response = JSONResponse(
            status_code=self.StatusCodes.internal_server_error.value,
            content=({"message": "Internal Server Error.", "data": None}),
        )
        return response

    def no_data_found_response(self) -> JSONResponse:
        """Map to a 404 error."""
        response = JSONResponse(
            status_code=self.StatusCodes.no_data.value,
            content=({"message": "No Data Found.", "data": None}),
        )
        return response

    def multiple_items_found_response(self, models: List[BaseModel]) -> JSONResponse:
        """Map to a multiple choices error."""
        models_json = [jsonable_encoder(model) for model in models]
        response = JSONResponse(
            status_code=self.StatusCodes.multiple_responses.value,
            content=(
                {"message": "Multiple Items Found.", "data": models_json}
            ),
        )
        return response

    def model_response(self, model: BaseModel) -> JSONResponse:
        """
        Parse model to a response or return model if valid.
        Handles validation errors.
        Parameters
        ----------
        model : BaseModel
            model response from server
        """
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        model_json = jsonable_encoder(model)
        if validation_error:
            response = JSONResponse(
                status_code=self.StatusCodes.invalid_data.value,
                content=(
                    {
                        "message": f"Validation Errors: {validation_error}",
                        "data": model_json,
                    }
                ),
            )
        else:
            response = JSONResponse(
                status_code=self.StatusCodes.valid_data.value,
                content=(
                    {
                        "message": "Valid Model.",
                        "data": model_json,
                    }
                ),
            )
        return response
