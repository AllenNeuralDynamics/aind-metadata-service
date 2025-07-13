"""Module to handle endpoint responses"""

import aind_labtracks_service_async_client
import aind_mgi_service_async_client
from fastapi import APIRouter, Depends, Path, status

from aind_metadata_service_server.configs import Settings, get_settings
from aind_metadata_service_server.mappers.subject import SubjectMapper
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
    ),
    settings: Settings = Depends(get_settings),
):
    """
    ## Subject
    Return Subject metadata.
    """
    labtracks_config = aind_labtracks_service_async_client.Configuration(
        host="http://labtracks"
    )
    async with aind_labtracks_service_async_client.ApiClient(
        labtracks_config
    ) as api_client:
        api_instance = aind_labtracks_service_async_client.DefaultApi(
            api_client
        )
        labtracks_response = await api_instance.get_subject(subject_id)

    mappers = [
        SubjectMapper(labtracks_subject=labtracks_subject)
        for labtracks_subject in labtracks_response
    ]

    mgi_config = aind_mgi_service_async_client.Configuration(
        host="http://mgi"
    )
    async with aind_mgi_service_async_client.ApiClient(
        mgi_config
    ) as api_client:
        api_instance = aind_mgi_service_async_client.DefaultApi(api_client)
        for mapper in mappers:
            mgi_info = []
            allele_names = mapper.get_allele_names_from_genotype()
            for allele_name in allele_names:
                api_response = await api_instance.get_allele_info(
                    allele_name=allele_name
                )
                mgi_info.extend(api_response)
            mapper.mgi_info = mgi_info

    subjects = [mapper.map_to_aind_subject() for mapper in mappers]
    response_handler = ModelResponse(
        aind_models=subjects, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
