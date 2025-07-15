"""Module to handle funding endpoints"""

from fastapi import APIRouter, Depends, Path, Query
from typing import Optional
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_smartsheet_api_instance
from aind_metadata_service_server.mappers.funding import FundingMapper

router = APIRouter()


@router.get("/funding/{project_name}")
async def get_funding(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": "Discovery-Neuromodulator circuit dynamics during foraging",
            }
        },
    ),
    subproject: Optional[str] = Query(
        default=None,
        openapi_examples={
            "default": {
                "summary": "A sample subproject",
                "description": "Example subproject name",
                "value": "Subproject 2 Molecular Anatomy Cell Types",
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
):
    """
    ## Funding
    Return Funding metadata.
    """
    funding_response = await smartsheet_api_instance.get_funding(
        project_name=project_name, subproject=subproject, _request_timeout=10
    )
    mapper = FundingMapper(funding_data=funding_response)
    funding_information = mapper.get_funding_list()
    response_handler = ModelResponse(
        aind_models=funding_information, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response


@router.get("/project_names")
async def get_project_names(
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
) -> list:
    """
    Get a list of project names from the Smartsheet API.
    """
    funding_response = await smartsheet_api_instance.get_funding(
        _request_timeout=10
    )
    mapper = FundingMapper(funding_data=funding_response)
    response = mapper.get_project_names()
    return response
