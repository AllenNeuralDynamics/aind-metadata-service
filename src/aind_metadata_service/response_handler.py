"""Module to handle responses"""
from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model

from aind_metadata_service.client import StatusCodes


class Responses:
    """This class contains methods to map responses from server."""

    @staticmethod
    def connection_error_response() -> JSONResponse:
        """Map to a connection error"""
        response = JSONResponse(
            status_code=StatusCodes.CONNECTION_ERROR.value,
            content=(
                {
                    "message": "Error Connecting to Internal Server.",
                    "data": None,
                }
            ),
        )
        return response

    @staticmethod
    def internal_server_error_response() -> JSONResponse:
        """Map to an internal server error"""
        response = JSONResponse(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR.value,
            content=({"message": "Internal Server Error.", "data": None}),
        )
        return response

    @staticmethod
    def no_data_found_response() -> JSONResponse:
        """Map to a 404 error."""
        response = JSONResponse(
            status_code=StatusCodes.NO_DATA_FOUND.value,
            content=({"message": "No Data Found.", "data": None}),
        )
        return response

    @staticmethod
    def multiple_items_found_response(models: List[BaseModel]) -> JSONResponse:
        """Map to a multiple choices error."""
        models_json = [jsonable_encoder(model) for model in models]
        response = JSONResponse(
            status_code=StatusCodes.MULTIPLE_RESPONSES.value,
            content=(
                {"message": "Multiple Items Found.", "data": models_json}
            ),
        )
        return response

    @staticmethod
    def model_response(model: BaseModel) -> JSONResponse:
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
                status_code=StatusCodes.INVALID_DATA.value,
                content=(
                    {
                        "message": f"Validation Errors: {validation_error}",
                        "data": model_json,
                    }
                ),
            )
        else:
            response = JSONResponse(
                status_code=StatusCodes.VALID_DATA.value,
                content=(
                    {
                        "message": "Valid Model.",
                        "data": model_json,
                    }
                ),
            )
        return response
