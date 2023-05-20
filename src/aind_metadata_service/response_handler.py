"""Module to handle responses"""
import json
from typing import List

from aind_data_schema.procedures import Procedures
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model

from aind_metadata_service.client import StatusCodes


class Responses:
    """This class contains methods to map responses from server."""

    @staticmethod
    def multi_status_response(message1: str, message2: str, data) -> JSONResponse:
        """"""
        response = JSONResponse(
            status_code=StatusCodes.MULTI_STATUS.value,
            content=(
                {
                    "message": f"Message 1: {message1}, "
                               f"Message 2: {message2}",
                    "data": data,
                }
            )
        )
        return response

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
    def combine_procedure_responses(
        subject_id: str, lb_response: JSONResponse, sp_response: JSONResponse
    ) -> JSONResponse:
        """
        Combines JSONResponses from Labtracks and Sharepoint clients.
        Handles validation errors and special cases.
        """
        lb_contents = json.loads(lb_response.body)
        sp_contents = json.loads(sp_response.body)
        sp_status_code = sp_response.status_code
        lb_status_code = lb_response.status_code
        if sp_status_code == 500 and lb_status_code == 500:
            return Responses.internal_server_error_response()
        if sp_status_code == 503 and lb_status_code == 503:
            return Responses.connection_error_response()
        if sp_status_code == 404 and lb_status_code == 404:
            return Responses.no_data_found_response()
        if sp_status_code < 300 and lb_status_code == 404:
            return sp_response
        if sp_status_code == 404 and lb_status_code < 300:
            return lb_response
        # handles combinations of valid and invalid responses
        if (sp_status_code < 300 or sp_status_code == 406) and (lb_status_code < 300 or lb_status_code == 406):
            lb_data = lb_contents["data"]["subject_procedures"]
            sp_data = sp_contents["data"]["subject_procedures"]
            combined_data = lb_data + sp_data
            print(combined_data)
            procedures = Procedures.construct(subject_id=subject_id, subject_procedures=combined_data)
            return Responses.model_response(procedures)
        # handles combination of server/connection error and valid response
        if sp_status_code in (500, 503) and lb_status_code < 300:
            lb_data = lb_contents["data"]["subject_procedures"]
            return Responses.multi_status_response(
                message1=sp_contents["message"],
                message2=lb_contents["message"],
                data=lb_data
            )
        if sp_status_code < 300 and lb_status_code in (500, 503):
            sp_data = sp_contents["data"]["subject_procedures"]
            return Responses.multi_status_response(
                message1=sp_contents["message"],
                message2=lb_contents["message"],
                data=sp_data
            )
