"""Module to handle responses"""
import json
from typing import List, Tuple, Union

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model

from aind_metadata_service.client import StatusCodes


class Responses:
    """This class contains methods to map responses from server."""

    @staticmethod
    def generate_message(
        status_code: int, model: BaseModel | List[BaseModel] = None
    ) -> str:
        """Generate message using the status code and optional model.
        Use case: Subject and Procedures response."""

        if status_code == StatusCodes.INVALID_DATA.value:
            *_, validation_error = validate_model(
                model.__class__, model.__dict__
            )
            return f"Validation Errors: {validation_error}"
        elif status_code == StatusCodes.INTERNAL_SERVER_ERROR.value:
            return "Internal Server Error."
        elif status_code == StatusCodes.CONNECTION_ERROR.value:
            return "Error Connecting to Internal Server."
        elif status_code == StatusCodes.NO_DATA_FOUND.value:
            return "No Data Found."
        elif status_code == StatusCodes.VALID_DATA.value:
            return "Valid Model."
        elif status_code == StatusCodes.MULTIPLE_RESPONSES.value:
            return "Multiple Items Found."

    @staticmethod
    def generate_models_json(
        status_code: int, models: Union[BaseModel, List[BaseModel], None]
    ) -> JSONResponse:
        """Generate model data in JSON format.
        Use case: Subject and Procedures response."""
        models_json = None
        if models is not None:
            if status_code == StatusCodes.MULTIPLE_RESPONSES.value:
                models_json = [
                    jsonable_encoder(json.loads(model.json()))
                    for model in models
                ]
            else:
                models_json = jsonable_encoder(json.loads(models.json()))
        return models_json

    @staticmethod
    def convert_response_to_json(
        status_code: int,
        model: Union[BaseModel, List[BaseModel], None],
        message: str = None,
    ) -> JSONResponse:
        """Convert status code and model response into JSON response.
        An optional message may be provided if the response was the result of combining two responses.
        Use case: Subject and Procedures response, combined Procedures responses.
        """

        message = (
            Responses.generate_message(status_code, model)
            if message is None
            else message
        )

        return JSONResponse(
            status_code=status_code,
            content=(
                {
                    "message": message,
                    "data": Responses.generate_models_json(status_code, model),
                }
            ),
        )

    @staticmethod
    def generate_mixed_message(
        lb_response: Tuple[int, Union[BaseModel, None]],
        sp_response: Tuple[int, Union[BaseModel, None]],
    ) -> str:
        """Generate combined message from combining two responses.
        Use case: combine Procedures responses."""
        lb_model = lb_response[1]
        sp_model = sp_response[1]
        lb_status_code = lb_response[0]
        sp_status_code = sp_response[0]

        message1 = Responses.generate_message(lb_status_code, lb_model)
        message2 = Responses.generate_message(sp_status_code, sp_model)
        combined_message = f"Message 1: {message1},Message 2: {message2}"

        return combined_message

    @staticmethod
    def connection_error_response() -> Tuple[int, None]:
        """Map to a connection error"""
        status_code = StatusCodes.CONNECTION_ERROR.value
        message = Responses.generate_message(status_code, None)
        response = (status_code, None)
        return response

    @staticmethod
    def internal_server_error_response() -> Tuple[int, None]:
        """Map to an internal server error"""
        status_code = StatusCodes.INTERNAL_SERVER_ERROR.value
        response = (status_code, None)
        return response

    @staticmethod
    def no_data_found_response() -> Tuple[int, None]:
        """Map to a 404 error."""
        status_code = StatusCodes.NO_DATA_FOUND.value
        response = (status_code, None)
        return response

    @staticmethod
    def multiple_items_found_response(
        models: List[BaseModel],
    ) -> Tuple[int, List[BaseModel]]:
        """Map to a multiple choices error."""
        status_code = StatusCodes.MULTIPLE_RESPONSES.value
        response = (status_code, models)
        return response

    @staticmethod
    def model_response(model: BaseModel) -> tuple[int, BaseModel]:
        """
        Parse model to a response or return model if valid.
        Handles validation errors.
        Parameters
        ----------
        model : BaseModel
            model response from server
        """
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        if validation_error:
            status_code = StatusCodes.INVALID_DATA.value
        else:
            status_code = StatusCodes.VALID_DATA.value
        response = (status_code, model)
        return response

    # flake8: noqa: C901
    @staticmethod
    def combine_procedure_responses(
        lb_response: Tuple[int, Union[BaseModel, None]],
        sp_response: Tuple[int, Union[BaseModel, None]],
    ) -> Tuple[int, Union[BaseModel, None], str]:
        """
        Combines Model Responses from Labtracks and Sharepoint clients.
        Handles validation errors and special cases.
        Returns status code, combined model, and message.
        """
        lb_model = lb_response[1]
        sp_model = sp_response[1]
        sp_status_code = sp_response[0]
        lb_status_code = lb_response[0]
        if sp_status_code == 500 and lb_status_code == 500:
            message = Responses.generate_message(sp_status_code)
            return Responses.internal_server_error_response() + (message,)
        if sp_status_code == 503 and lb_status_code == 503:
            message = Responses.generate_message(sp_status_code)
            return Responses.connection_error_response() + (message,)
        if sp_status_code == 404 and lb_status_code == 404:
            message = Responses.generate_message(sp_status_code)
            return Responses.no_data_found_response() + (message,)
        if sp_status_code < 300 and lb_status_code == 404:
            message = Responses.generate_message(sp_status_code)
            return sp_response + (message,)
        if sp_status_code == 404 and lb_status_code < 300:
            message = Responses.generate_message(lb_status_code)
            return lb_response + (message,)
        # handles combination of invalid responses
        if lb_status_code == 406 and sp_status_code == 406:
            print("both invalid")
            lb_procedures = lb_model.subject_procedures
            sp_procedures = sp_model.subject_procedures

            status_code = StatusCodes.INVALID_DATA.value
            message = Responses.generate_mixed_message(
                lb_response, sp_response
            )

            combined_procedures = lb_procedures + sp_procedures
            sp_model.subject_procedures = combined_procedures

            return status_code, sp_model, message

        # handles combinations of valid and invalid responses
        if (sp_status_code < 300 and lb_status_code == 406) or (
            lb_status_code < 300 and sp_status_code == 406
        ):
            lb_procedures = lb_model.subject_procedures
            sp_procedures = sp_model.subject_procedures

            status_code = StatusCodes.MIXED_STATUS.value
            message = Responses.generate_mixed_message(
                lb_response, sp_response
            )

            combined_procedures = lb_procedures + sp_procedures
            sp_model.subject_procedures = combined_procedures
            return status_code, sp_model, message

        # handles case when both responses are valid
        if sp_status_code < 300 and lb_status_code < 300:
            lb_procedures = lb_model.subject_procedures
            sp_procedures = sp_model.subject_procedures

            status_code = StatusCodes.VALID_DATA.value
            message = Responses.generate_message(status_code)

            combined_procedures = lb_procedures + sp_procedures
            sp_model.subject_procedures = combined_procedures

            return status_code, sp_model, message

        # handles combination of server/connection error and valid response
        if sp_status_code in (500, 503) and lb_status_code < 300:
            status_code = StatusCodes.MIXED_STATUS.value
            message = Responses.generate_mixed_message(
                lb_response, sp_response
            )
            return status_code, lb_model, message

        if sp_status_code < 300 and lb_status_code in (500, 503):
            status_code = StatusCodes.MIXED_STATUS.value
            message = Responses.generate_mixed_message(
                lb_response, sp_response
            )
            return status_code, sp_model, message
