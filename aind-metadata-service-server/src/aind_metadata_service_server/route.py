"""Module to handle endpoint responses"""

from typing import List

import aind_labtracks_service_async_client
from aind_data_schema.core.subject import Subject
from fastapi import APIRouter, Path, status

from aind_metadata_service_server.mappers.subject import SubjectMapper
from aind_metadata_service_server.models import HealthCheck

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


@router.get(
    "/subject/{subject_id}",
    response_model=List[Subject],
)
async def get_subject(subject_id: str = Path(..., examples=["632269"])):
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
    return subjects
