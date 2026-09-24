"""Module to handle funding endpoints"""

import logging
from asyncio import gather

from aind_data_schema.components.identifiers import Person
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.openapi.models import Example
from orcid_service_async_client.api.default_api import DefaultApi
from orcid_service_async_client.exceptions import NotFoundException
from starlette.responses import JSONResponse

from aind_metadata_service_server.mappers.funding import FundingMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_dataverse_api_instance,
    get_orcid_api_instance,
)

router = APIRouter()


async def resolve_orcid(
    person: Person, orcid_api_instance: DefaultApi
) -> None:
    """
    Set registry_identifier in place on each person whose name resolves to
    a single ORCID.
    """
    try:
        response = await orcid_api_instance.get_orcid(
            name=person.name, _request_timeout=10
        )
        person.registry_identifier = response.orcid
    except NotFoundException:
        pass
    except Exception as error:
        logging.warning(f"ORCID lookup failed: {error}")


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
            "default": Example(
                summary="A sample project name",
                description="Example project name for smartsheet",
                value="Thalamus - Project 1 Mesoscale thalamic circuits",
            )
        },
    ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
    orcid_api_instance=Depends(get_orcid_api_instance),
):
    """
    ## Funding
    Return Funding metadata.
    """
    funding_response = await dataverse_api_instance.get_funding(
        _request_timeout=30,
    )
    mapper = FundingMapper(dataverse_funding=funding_response)
    people = mapper.get_people_list(project_name=project_name)
    tasks = [
        resolve_orcid(person=p, orcid_api_instance=orcid_api_instance)
        for p in people
    ]
    _ = await gather(*tasks)
    funding_information = mapper.get_funding_list(
        project_name=project_name, resolved_people=people
    )
    if len(funding_information) == 0:
        raise HTTPException(status_code=404, detail="Not found")
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
    },
)
async def get_investigators(
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": Example(
                summary="A sample project name",
                description="Example project name for smartsheet",
                value="Thalamus - Project 1 Mesoscale thalamic circuits",
            )
        },
    ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
    orcid_api_instance=Depends(get_orcid_api_instance),
):
    """
    ## Funding
    Return Funding metadata.
    """
    funding_response = await dataverse_api_instance.get_funding()
    mapper = FundingMapper(dataverse_funding=funding_response)
    investigators = mapper.get_investigators_list(project_name=project_name)

    if len(investigators) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    tasks = [
        resolve_orcid(person=p, orcid_api_instance=orcid_api_instance)
        for p in investigators
    ]
    _ = await gather(*tasks)
    return map_to_response(investigators)


@router.get("/api/v2/project_names")
async def get_project_names(
    dataverse_api_instance=Depends(get_dataverse_api_instance),
) -> JSONResponse:
    """
    Get a list of project names from the Smartsheet API.
    """
    funding_response = await dataverse_api_instance.get_funding(
        _request_timeout=30
    )
    mapper = FundingMapper(dataverse_funding=funding_response)
    project_names_list = mapper.get_project_names()
    if len(project_names_list) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    response = JSONResponse(
        status_code=200,
        content=project_names_list,
    )
    return response


@router.get("/api/v2/dataverse/funding")
async def get_dataverse_funding(
    dataverse_api_instance=Depends(get_dataverse_api_instance),
) -> JSONResponse:
    """
    Get raw funding data from Dataverse.
    """
    funding_response = await dataverse_api_instance.get_funding(
        _request_timeout=30
    )
    return funding_response
