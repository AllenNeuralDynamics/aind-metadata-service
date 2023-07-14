"""Module to handle responses"""
import json
import logging
from typing import List, Optional, Tuple, Union

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validate_model

from aind_metadata_service.client import StatusCodes


class Responses:
    """This class contains methods to map responses from server."""

    @staticmethod
    def generate_message(status_code: StatusCodes, model: BaseModel = None) -> str:
        """Generate message using the status code and optional model"""
        match status_code:
            case StatusCodes.INVALID_DATA.value:
                *_, validation_error = validate_model(model.__class__, model.__dict__)
                return f"Validation Errors: {validation_error}"
            case StatusCodes.INTERNAL_SERVER_ERROR.value:
                return "Internal Server Error."
            case StatusCodes.CONNECTION_ERROR.value:
                return "Error Connecting to Internal Server."
            case StatusCodes.NO_DATA_FOUND.value:
                return "No Data Found."
            case StatusCodes.VALID_DATA.value:
                return "Valid Model."
            case StatusCodes.MULTIPLE_RESPONSES.value:
                return "Multiple Items Found."

    @staticmethod
    def generate_combine_message(status_code1: StatusCodes, status_code2: StatusCodes,
                                 model1: Optional[BaseModel], model2: Optional[BaseModel]) -> str:
        """Generate message for combined model using status codes and optional models """
        message1 = Responses.generate_message(status_code1, model1)
        message2 = Responses.generate_message(status_code2, model2)
        message = f"Message 1: {message1}, Message 2: {message2}"
        return message

    @staticmethod
    def generate_models_json(status_code: StatusCodes, models: Union[BaseModel, List[BaseModel], None]):
        """Generate model data in JSON"""
        models_json = None
        if models is not None:
            if status_code == StatusCodes.MULTIPLE_RESPONSES.value:
                models_json = [jsonable_encoder(json.loads(model.json())) for model in models]
            else:
                models_json = jsonable_encoder(json.loads(models.json()))
        return models_json

    @staticmethod
    def combine_response_json(
            status_code: StatusCodes,
            lb_response: Tuple[str, Union[BaseModel, List[BaseModel], None]],
            sp_response: Tuple[str, Union[BaseModel, List[BaseModel], None]],
            combined_model: Union[BaseModel, List[BaseModel], None]
    ) -> JSONResponse:
        """Map to a multi status JSON message."""

        lb_model = lb_response[1]
        sp_model = sp_response[1]
        sp_status_code = sp_response[0]
        lb_status_code = lb_response[0]

        return JSONResponse(
            status_code=status_code,
            content=(
                {
                    "message": Responses.generate_combine_message(lb_status_code, sp_status_code, lb_model, sp_model),
                    "data": Responses.generate_models_json(status_code, combined_model)
                }
            )
        )

    @staticmethod
    def convert_response_to_json(response: Tuple[str, Union[BaseModel, List[BaseModel], None]]):
        """Convert status code and model response into JSON response"""
        status_code = response[0]
        model = response[1]

        return JSONResponse(
            status_code=status_code,
            content=(
                {
                    "message": Responses.generate_message(status_code, model),
                    "data": Responses.generate_models_json(status_code, model)
                }
            )
        )
    @staticmethod
    def connection_error_response() -> Tuple[str, None]:
        """Map to a connection error"""
        status_code = StatusCodes.CONNECTION_ERROR.value
        message = Responses.generate_message(status_code, None)
        response = (status_code, None)
        return response

    @staticmethod
    def internal_server_error_response() -> Tuple[str, None]:
        """Map to an internal server error"""
        status_code = StatusCodes.INTERNAL_SERVER_ERROR.value
        response = (status_code, None)
        return response

    @staticmethod
    def no_data_found_response() -> Tuple[str, None]:
        """Map to a 404 error."""
        status_code = StatusCodes.NO_DATA_FOUND.value
        response = (status_code, None)
        return response

    @staticmethod
    def multiple_items_found_response(models: List[BaseModel]) -> Tuple[str, List[BaseModel]]:
        """Map to a multiple choices error."""
        status_code = StatusCodes.MULTIPLE_RESPONSES.value
        response = (status_code, models)
        return response

    @staticmethod
    def model_response(model: BaseModel) -> tuple[BaseModel, str]:
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
        lb_response: Tuple[str, Union[BaseModel, List[BaseModel], None]], sp_response: Tuple[str, Union[BaseModel, List[BaseModel], None]]
    ) -> JSONResponse:
        """
        Combines JSONResponses from Labtracks and Sharepoint clients.
        Handles validation errors and special cases.
        """
        try:
            lb_model = lb_response[1]
            sp_model = sp_response[1]
            sp_status_code = sp_response[0]
            lb_status_code = lb_response[0]
            if sp_status_code == 500 and lb_status_code == 500:
                return Responses.convert_response_to_json(Responses.internal_server_error_response())
            if sp_status_code == 503 and lb_status_code == 503:
                return Responses.convert_response_to_json(Responses.connection_error_response())
            if sp_status_code == 404 and lb_status_code == 404:
                return Responses.convert_response_to_json(Responses.no_data_found_response())
            if sp_status_code < 300 and lb_status_code == 404:
                return Responses.convert_response_to_json(sp_response)
            if sp_status_code == 404 and lb_status_code < 300:
                return Responses.convert_response_to_json(lb_response)
            # handles combination of invalid responses
            if lb_status_code == 406 and sp_status_code == 406:
                print('both invalid')
                lb_procedures = lb_model.subject_procedures
                sp_procedures = sp_model.subject_procedures
                combined_procedures = lb_procedures + sp_procedures
                lb_model.subject_procedures = combined_procedures
                status_code = StatusCodes.INVALID_DATA.value
                return Responses.combine_response_json(status_code, lb_response, sp_response, lb_model)

            # handles combinations of valid and invalid responses
            if (sp_status_code < 300 and lb_status_code == 406) or (
                lb_status_code < 300 and sp_status_code == 406
            ):
                lb_procedures = lb_model.subject_procedures
                sp_procedures = sp_model.subject_procedures
                combined_procedures = lb_procedures + sp_procedures
                lb_model.subject_procedures = combined_procedures
                status_code = StatusCodes.MULTI_STATUS.value

                return Responses.combine_response_json(status_code, lb_model, sp_model, lb_model)

            # handles case when both responses are valid
            if sp_status_code < 300 and lb_status_code < 300:
                lb_procedures = lb_model.subject_procedures
                sp_procedures = sp_model.subject_procedures
                combined_procedures = lb_procedures + sp_procedures
                lb_model.subject_procedures = combined_procedures
                status_code = StatusCodes.VALID_DATA.value

                return Responses.combine_response_json(status_code, lb_model, sp_model, lb_model)

            # handles combination of server/connection error and valid response
            if sp_status_code in (500, 503) and lb_status_code < 300:
                status_code = StatusCodes.MULTI_STATUS.value

                return Responses.combine_response_json(status_code, lb_model, sp_model, lb_model)

            if sp_status_code < 300 and lb_status_code in (500, 503):
                status_code = StatusCodes.MULTI_STATUS.value

                return Responses.combine_response_json(status_code, lb_model, sp_model, lb_model)
        except Exception as e:
            logging.error(repr(e))
            return Responses.convert_response_to_json(Responses.internal_server_error_response())
