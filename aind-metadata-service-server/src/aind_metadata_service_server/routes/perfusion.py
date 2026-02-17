"""Module to handle perfusions endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.perfusion import PerfusionMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_smartsheet_api_instance

router = APIRouter()


@router.get(
    "/api/v2/perfusions/{subject_id}",
    responses={
        400: {
            "description": "Validation error in response model.",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation error in response model."}
                }
            },
        },
        404: {"description": "Not found"},
    },
)
async def get_perfusions(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject id",
                "description": "Example subject id",
                "value": "689418",
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
):
    """
    ## Perfusions
    Return Perfusions metadata.
    """
    perfusions_response = await smartsheet_api_instance.get_perfusions(
        subject_id, _request_timeout=10
    )
    mappers = [
        PerfusionMapper(smartsheet_perfusion=smartsheet_perfusion)
        for smartsheet_perfusion in perfusions_response
    ]
    perfusions = [mapper.map_to_aind_surgery() for mapper in mappers]
    if len(perfusions) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return map_to_response(perfusions)
