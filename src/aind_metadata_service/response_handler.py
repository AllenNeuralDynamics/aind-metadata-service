"""Module to handle responses"""

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model
from typing import Union


class Responses:
    """Class with methods to map responses."""

    @staticmethod
    def internal_server_error_response() -> JSONResponse:
        """Map to an internal server error"""
        response = JSONResponse(
            status_code=500,
            content=({"message": "Internal Server Error.", "data": None}),
        )
        return response

    @staticmethod
    def no_data_found_response() -> JSONResponse:
        """Map to a 404 error."""
        response = JSONResponse(
            status_code=404,
            content=({"message": "No Data Found.", "data": None}),
        )
        return response

    @staticmethod
    def model_response(model: BaseModel) -> Union[JSONResponse, BaseModel]:
        """Parse model to a response or return model if valid."""
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        model_json = jsonable_encoder(model)
        if validation_error:
            response = JSONResponse(
                status_code=418,
                content=(
                    {
                        "message": f"Validation Errors: {validation_error}",
                        "data": model_json,
                    }
                ),
            )
        else:
            response = model
        return response
