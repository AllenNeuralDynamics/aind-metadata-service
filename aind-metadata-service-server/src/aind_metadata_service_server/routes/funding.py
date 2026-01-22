"""Module to handle funding endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.responses import JSONResponse

from aind_metadata_service_server.mappers.funding import FundingMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_smartsheet_api_instance

router = APIRouter()


@router.get("/api/v2/funding/{project_name}")
async def get_funding(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": (
                    "Thalamus in the middle - Project 1 Mesoscale thalamic"
                    " circuits"
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
    has_subprojects = any(row.subproject for row in funding_response)
    if subproject is None and has_subprojects:
        raise HTTPException(
            status_code=406,
            detail=(
                f"Project '{main_project_name}' has subprojects. "
                f"Please specify a subproject in the format: "
                f"'{main_project_name} - Subproject Name'"
            ),
        )
    mapper = FundingMapper(smartsheet_funding=funding_response)
    funding_information = mapper.get_funding_list()

    if len(funding_information) == 0:
        raise HTTPException(status_code=404, detail="Not found")

    return map_to_response(funding_information)


@router.get("/api/v2/investigators/{project_name}")
async def get_investigators(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": (
                    "Thalamus in the middle - Project 1 Mesoscale thalamic"
                    " circuits"
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
    has_subprojects = any(row.subproject for row in funding_response)
    if subproject is None and has_subprojects:
        raise HTTPException(
            status_code=406,
            detail=(
                f"Project '{main_project_name}' has subprojects. "
                f"Please specify a subproject in the format: "
                f"'{main_project_name} - Subproject Name'"
            ),
        )
    mapper = FundingMapper(smartsheet_funding=funding_response)
    investigators = mapper.get_investigators_list()

    if len(investigators) == 0:
        raise HTTPException(status_code=404, detail="Not found")

    return map_to_response(investigators)


@router.get("/api/v2/project_names")
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
    if len(project_names_list) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    response = JSONResponse(
        status_code=200,
        content=project_names_list,
    )
    return response


@router.get("/api/v2/smartsheet/funding")
async def get_smartsheet_funding(
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
) -> JSONResponse:
    """
    Get raw funding data from Smartsheet.
    """
    funding_response = await smartsheet_api_instance.get_funding(
        _request_timeout=10
    )
    return funding_response
