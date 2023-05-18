"""Module to handle responses"""
from typing import List
import json

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model

from aind_metadata_service.client import StatusCodes
from aind_data_schema.procedures import Procedures


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

    @staticmethod
    def combine_responses(
        lb_response: JSONResponse, sp_response: JSONResponse
    ) -> JSONResponse:
        """
        Combines JSONResponses from Labtracks and Sharepoint clients.
        Handles validation errors and special cases.
        """
        lb_data = []
        sp_data = []
        lb_contents = json.loads(lb_response.body)
        sp_contents = json.loads(sp_response.body)
        if lb_contents["data"]:
            lb_data = lb_contents["data"]["subject_procedures"]
            subject_id = lb_contents["data"]["subject_id"]
        if sp_contents["data"]:
            sp_data = sp_contents["data"]["subject_procedures"]
            subject_id = sp_contents["data"]["subject_id"]
        merged_data = lb_data + sp_data
        if merged_data:
            procedures = Procedures.construct(subject_id=subject_id)
            procedures.subject_procedures = merged_data
            model_json = jsonable_encoder(procedures)
            if lb_response.status_code == sp_response.status_code:
                if lb_response.status_code == StatusCodes.INVALID_DATA.value:
                    # combine messages to get all validation errors
                    combine_message = (
                        lb_contents["message"] + sp_contents["message"]
                    )
                    response = JSONResponse(
                        status_code=StatusCodes.INVALID_DATA.value,
                        content=(
                            {
                                "message": combine_message,
                                "data": model_json,
                            }
                        ),
                    )
                else:
                    # status message and code are the same for both responses
                    response = JSONResponse(
                        status_code=lb_response.status_code,
                        content=(
                            {
                                "message": lb_contents["message"],
                                "data": model_json,
                            }
                        ),
                    )
            else:
                # handle case where at least one response is valid.
                if {
                    lb_response.status_code == StatusCodes.VALID_DATA.value
                } or {sp_response.status_code == StatusCodes.VALID_DATA.value}:
                    response = JSONResponse(
                        status_code=StatusCodes.MULTI_STATUS.value,
                        content={
                            "message": "Valid Model.",
                            "data": model_json,
                        },
                    )
                else:
                    # statuses are different
                    combine_message = (
                        lb_contents["message"] + sp_contents["message"]
                    )
                    response = JSONResponse(
                        status_code=StatusCodes.MULTI_STATUS.value,
                        content=(
                            {
                                "message": combine_message,
                                "data": model_json,
                            }
                        ),
                    )
        else:
            # when no data is found, combine error messages
            combine_message = lb_contents["message"] + sp_contents["message"]
            response = JSONResponse(
                status_code=StatusCodes.MULTI_STATUS.value,
                content=(
                    {
                        "message": combine_message,
                        "data": None,
                    }
                ),
            )
        return response
