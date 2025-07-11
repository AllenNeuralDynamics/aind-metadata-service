"""Module to handle endpoint responses"""

import aind_labtracks_service_async_client
import aind_smartsheet_service_async_client
from aind_metadata_service_server import aind_models
from fastapi import APIRouter, Path, status

from aind_metadata_service_server.mappers.subject import SubjectMapper
from aind_metadata_service_server.mappers.perfusions import PerfusionsMapper
from aind_metadata_service_server.models import HealthCheck
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)

router = APIRouter()


@router.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Endpoint to perform a healthcheck on.

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck()


@router.get("/subject/{subject_id}")
async def get_subject(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for LabTracks",
                "value": "632269",
            }
        },
    )
):
    """
    ## Subject
    Return Subject metadata.
    """
    configuration = aind_labtracks_service_async_client.Configuration(
        host="http://labtracks"
    )
    async with aind_labtracks_service_async_client.ApiClient(
        configuration
    ) as api_client:
        api_instance = aind_labtracks_service_async_client.DefaultApi(
            api_client
        )
        api_response = await api_instance.get_subject(subject_id)
    subjects = [
        SubjectMapper(labtracks_subject=s).map_to_aind_subject()
        for s in api_response
    ]
    response_handler = ModelResponse(
        aind_models=subjects, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response

@router.get("/perfusions/{subject_id}")
async def get_perfusions(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for Smartsheet",
                "value": "689418",
            }
        },
    )
):
    """
    ## Perfusions
    Return Perfusions metadata.
    """
    configuration = aind_smartsheet_service_async_client.Configuration(
        host="http:/smartsheet"
    )
    async with aind_smartsheet_service_async_client.ApiClient(
        configuration
    ) as api_client:
        api_instance = aind_smartsheet_service_async_client.DefaultApi(
            api_client
        )
        api_response = await api_instance.get_perfusions(subject_id=subject_id)
    # TODO: fix the perfusion mapper as needed 
    perfusions = [
        PerfusionsMapper(input_id=s)._get_perfusion_list()
        for s in api_response
    ]
    response_handler = ModelResponse(
        aind_models=perfusions, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
