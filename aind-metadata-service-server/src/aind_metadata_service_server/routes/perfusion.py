"""Module to handle perfusions endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.perfusion import PerfusionMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_smartsheet_api_instance
)

router = APIRouter()


@router.get("/perfusions/{subject_id}")
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
    response_handler = ModelResponse(
        aind_models=perfusions, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
