"""Module to handle funding endpoints"""

from fastapi import APIRouter, Depends, Path
from starlette.responses import JSONResponse

from aind_metadata_service_server.mappers.funding import FundingMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_smartsheet_api_instance

router = APIRouter()


@router.get("/funding/{project_name}")
async def get_funding(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": (
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                ),
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
):
    """
    ## Funding
    Return Funding metadata.
    """
    main_project_name, subproject = FundingMapper.split_name(project_name)
    funding_response = await smartsheet_api_instance.get_funding(
        project_name=main_project_name,
        subproject=subproject,
        _request_timeout=10,
    )
    mapper = FundingMapper(smartsheet_funding=funding_response)
    funding_information = mapper.get_funding_list()
    response_handler = ModelResponse(
        aind_models=funding_information, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response


@router.get("/project_names")
async def get_project_names(
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
) -> JSONResponse:
    """
    Get a list of project names from the Smartsheet API.
    """
    funding_response = await smartsheet_api_instance.get_funding(
        _request_timeout=10
    )
    mapper = FundingMapper(smartsheet_funding=funding_response)
    project_names_list = mapper.get_project_names()
    response = JSONResponse(
        status_code=200,
        content=({"message": "Success", "data": project_names_list}),
    )
    return response
