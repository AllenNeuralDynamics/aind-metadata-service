"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.intended_measurements import (
    IntendedMeasurementMapper,
)
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_sharepoint_api_instance,
)

router = APIRouter()


@router.get("/intended_measurements/{subject_id}")
async def get_intended_measurements(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "example1": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for Procedures",
                "value": "775745",
            },
        },
    ),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
):
    """
    ## Intended Measurements
    Return Intended Measurements metadata.
    """
    nsb_2023_response = await sharepoint_api_instance.get_nsb2023(
        subject_id, _request_timeout=10
    )
    nsb_present_response = await sharepoint_api_instance.get_nsb_present(
        subject_id, _request_timeout=10
    )
    mapper = IntendedMeasurementMapper(
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
    )
    intended_measurements = mapper.map_responses_to_intended_measurements(
        subject_id
    )
    response_handler = ModelResponse(
        aind_models=intended_measurements, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
