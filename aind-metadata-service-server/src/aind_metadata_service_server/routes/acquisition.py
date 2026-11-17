"""Module to handle acquisition endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.openapi.models import Example

from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.mappers.smartspim_acquisition import (
    SmartSpimAcquisitionMapper,
)
from aind_metadata_service_server.sessions import get_dataverse_api_instance

router = APIRouter()


@router.get(
    "/api/v2/acquisition/{subject_id}",
    responses={
        400: {
            "description": "Validation error in response model.",
            "headers": {
                "X-Error-Message": {
                    "description": (
                        "A JSON-encoded list of Pydantic validation errors."
                    ),
                    "schema": {"type": "string"},
                }
            },
        },
        404: {"description": "Not found"},
    },
)
async def get_acquisition(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "example1": Example(
                summary="Subject ID Example 1",
                description="Example subject ID for SmartSPIM Acquisition",
                value="886598",
            ),
        },
    ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Acquisition
    Return SmartSPIM acquisition metadata from Dataverse. One acquisition is
    returned per imaging session, newest first.
    """
    imaging_response = await dataverse_api_instance.get_smartspim_imaging(
        subject_id=subject_id, _request_timeout=30
    )
    if not imaging_response:
        raise HTTPException(status_code=404, detail="Not found")
    acquisitions = SmartSpimAcquisitionMapper(
        imaging=imaging_response
    ).map_to_acquisitions()
    return map_to_response(acquisitions)
