"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.procedures import ProceduresMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance
)

router = APIRouter()


@router.get("/procedures/{subject_id}")
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
    # labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
):
    """
    ## Procedures
    Return Procedure metadata.
    """
    # labtracks_response = await labtracks_api_instance.get_tasks(
    #     subject_id, _request_timeout=10
    # )
    nsb_2019_response = await sharepoint_api_instance.get_nsb_2019(
        subject_id, _request_timeout=10
    )
    nsb_2023_response = await sharepoint_api_instance.get_nsb_2023(
        subject_id, _request_timeout=10
    )
    nsb_present_response = await sharepoint_api_instance.get_nsb_present(
        subject_id, _request_timeout=10
    )
    las_2020_response = await sharepoint_api_instance.get_las_2020(
        subject_id, _request_timeout=10
    )
    mapper = ProceduresMapper(
        # labtracks_tasks=labtracks_response,
        nsb_2019=nsb_2019_response,
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
        las_2020=las_2020_response
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    response_handler = ModelResponse(
        aind_models=procedures, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response

