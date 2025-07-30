"""Module to handle slims endpoints"""

from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from starlette.responses import JSONResponse

from aind_metadata_service_server.models import (
    SpimData,
    HistologyData,
    EcephysStreamModuleData,
    EcephysData
)
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
    workflow: SlimsWorkflow = Path(
        ...,
        description="The SLIMS workflow to query.",
    ),
    subject_id: Optional[str] = Query(
        None,
        alias="subject_id",
        description="Subject ID to filter the data.",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example subject ID",
                "value": "744742",
            },
            "histology_example": {
                "summary": "Histology example subject ID",
                "value": "744742",
            },
            "water_restriction_example": {
                "summary": "Water restriction example subject ID",
                "value": "762287",
            },
            "viral_injections_example": {
                "summary": "Viral injections example subject ID",
                "value": "614178",
            },
            "ecephys_session_example": {
                "summary": "Ecephys example subject ID",
                "value": "750108",
            },
        },
    ),
    session_name: Optional[str] = Query(
        None,
        alias="session_name",
        description="Name of the session (only for ecephys sessions).",
        openapi_examples={
            "none_example": {
                "summary": "No session name (default)",
                "value": None,
            },
            "ecephys_session_example": {
                "summary": "Ecephys example session name",
                "value": "ecephys_750108_2024-12-23_14-51-45",
            },
        },
    ),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example start date",
                "value": "2025-02-12",
            },
            "histology_example": {
                "summary": "Histology example start date",
                "value": "2025-02-06",
            },
            "water_restriction_example": {
                "summary": "Water restriction example start date",
                "value": "2024-12-13",
            },
            "viral_injections_example": {
                "summary": "Viral injections example start date",
                "value": "2025-04-23",
            },
            "ecephys_session_example": {
                "summary": "Ecephys example start date",
                "value": "2025-04-10",
            },
        },
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example end date",
                "value": "2025-02-13",
            },
            "histology_example": {
                "summary": "Histology example end date",
                "value": "2025-02-07",
            },
            "water_restriction_example": {
                "summary": "Water restriction example end date",
                "value": "2024-12-14",
            },
            "viral_injections_example": {
                "summary": "Viral injections example end date",
                "value": "2025-04-24",
            },
            "ecephys_session_example": {
                "summary": "Ecephys example end date",
                "value": "2025-04-11",
            },
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
    data = []
    match workflow:
        case SlimsWorkflow.ECEPHYS_SESSIONS:
            data = await slims_api_instance.get_ecephys_sessions(**kwargs)
            processed = []
            for d in data:
                d_dict = d.model_dump()
                if "stream_modules" in d_dict and d_dict["stream_modules"]:
                    d_dict["stream_modules"] = [
                        EcephysStreamModuleData(**sm)
                        for sm in d_dict["stream_modules"]
                    ]
                processed.append(EcephysData(**d_dict))
            data = processed
        case SlimsWorkflow.HISTOLOGY:
            data = await slims_api_instance.get_histology_data(**kwargs)
            data = [HistologyData(**d.model_dump()) for d in data]
        case SlimsWorkflow.SMARTSPIM_IMAGING:
            data = await slims_api_instance.get_smartspim_imaging(**kwargs)
            data = [SpimData(**d.model_dump()) for d in data]
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
