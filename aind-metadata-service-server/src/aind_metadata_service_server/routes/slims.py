"""Module to handle slims endpoints"""

from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse

from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_slims_api_instance

router = APIRouter()


class SlimsWorkflow(str, Enum):
    """Available workflows that can be queried."""

    SMARTSPIM_IMAGING = "smartspim_imaging"
    HISTOLOGY = "histology"
    WATER_RESTRICTION = "water_restriction"
    VIRAL_INJECTIONS = "viral_injections"
    ECEPHYS_SESSIONS = "ecephys_sessions"


@router.get("/slims/{workflow}")
async def get_slims_workflow(
    workflow: SlimsWorkflow,
    subject_id: Optional[str] = Query(
        None,
        alias="subject_id",
        openapi_examples={
            "ecephys_session_example": {
                "summary": "An example subject ID",
                "description": "Example subject ID for SLIMS ecephys data",
                "value": "750108",
            }
        },
    ),
    session_name: Optional[str] = Query(
        None,
        alias="session_name",
        description="Name of the session",
        openapi_examples={
            "ecephys_session_example": {
                "summary": "An example session name",
                "description": "Example session name for ecephys data",
                "value": "ecephys_750108_2024-12-23_14-51-45",
            }
        },
    ),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
        openapi_examples={
            "ecephys_session_example": {
                "summary": "ISO date format",
                "description": "Date only in ISO format",
                "value": "2025-04-10",
            }
        },
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
        openapi_examples={
            "ecephys_session_example": {
                "summary": "ISO date format",
                "description": "Date only in ISO format",
                "value": "2025-04-11",
            }
        },
    ),
    slims_api_instance=Depends(get_slims_api_instance),
):
    """
    ## SLIMS
    Return information from SLIMS.
    """
    kwargs = {
        "subject_id": subject_id,
        "start_date_gte": start_date_gte,
        "end_date_lte": end_date_lte,
        "_request_timeout": 30,
    }
    if workflow == SlimsWorkflow.ECEPHYS_SESSIONS:
        kwargs["session_name"] = session_name
    data = None
    match workflow:
        case SlimsWorkflow.ECEPHYS_SESSIONS:
            data = await slims_api_instance.get_ecephys_sessions(**kwargs)
        case SlimsWorkflow.HISTOLOGY:
            data = await slims_api_instance.get_histology_data(**kwargs)
        case SlimsWorkflow.SMARTSPIM_IMAGING:
            data = await slims_api_instance.get_smartspim_imaging(**kwargs)
        case SlimsWorkflow.WATER_RESTRICTION:
            data = await slims_api_instance.get_water_restriction_data(
                **kwargs
            )
        case SlimsWorkflow.VIRAL_INJECTIONS:
            data = await slims_api_instance.get_viral_injections(**kwargs)
    if data == [] or data is None:
        return ModelResponse.no_data_found_error_response()
    else:
        return JSONResponse(
            status_code=StatusCodes.VALID_DATA.value,
            content=(
                {
                    "message": "Data from SLIMS",
                    "data": [
                        d.model_dump(mode="json", exclude_none=True)
                        for d in data
                    ],
                }
            ),
        )
