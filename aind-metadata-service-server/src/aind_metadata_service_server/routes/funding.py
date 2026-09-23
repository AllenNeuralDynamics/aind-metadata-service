"""Module to handle funding endpoints"""

import logging
from time import monotonic
from typing import Dict, List, Optional

from aind_data_schema.components.identifiers import Person
from fastapi import APIRouter, Depends, HTTPException, Path
from orcid_service_async_client.exceptions import NotFoundException
from starlette.responses import JSONResponse

from aind_metadata_service_server.mappers.funding import FundingMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_orcid_api_instance,
    get_smartsheet_api_instance,
)

router = APIRouter()

# An ORCID search is usually well under a second but can take several, so
# allow room per name while capping the whole enrichment. Neither should
# ever hold up the investigators or funding these are attached to.
ORCID_TIMEOUT = 5
ORCID_BUDGET = 15


async def resolve_orcids(orcid_api_instance, people: List[Person]) -> None:
    """
    Set registry_identifier in place on each person whose name resolves to
    a single ORCID iD, looking up each distinct name once and giving up on
    the rest once ORCID_BUDGET is spent. Anything unresolved is left as
    None, so a slow or broken ORCID never fails the calling request.
    """
    deadline = monotonic() + ORCID_BUDGET
    resolved: Dict[str, Optional[str]] = dict()
    for person in people:
        if person.name not in resolved and monotonic() < deadline:
            resolved[person.name] = None
            try:
                response = await orcid_api_instance.get_orcid(
                    name=person.name, _request_timeout=ORCID_TIMEOUT
                )
                resolved[person.name] = response.orcid
            except NotFoundException:
                pass
            except Exception as error:
                logging.warning(f"ORCID lookup failed: {error}")
        person.registry_identifier = resolved.get(person.name)


@router.get(
    "/api/v2/funding/{project_name}",
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
        406: {"description": "Project has subprojects, specify subproject"},
    },
)
async def get_funding(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": ("Thalamus - Project 1 Mesoscale thalamic circuits"),
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
    orcid_api_instance=Depends(get_orcid_api_instance),
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

    await resolve_orcids(
        orcid_api_instance,
        [p for f in funding_information for p in f.fundee or []],
    )
    return map_to_response(funding_information)


@router.get(
    "/api/v2/investigators/{project_name}",
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
        406: {"description": "Project has subprojects, specify subproject"},
    },
)
async def get_investigators(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": ("Thalamus - Project 1 Mesoscale thalamic circuits"),
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
    orcid_api_instance=Depends(get_orcid_api_instance),
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

    await resolve_orcids(orcid_api_instance, investigators)
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
