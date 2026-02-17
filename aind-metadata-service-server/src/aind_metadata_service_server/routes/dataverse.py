"""Module to handle dataverse endpoints"""

from aind_dataverse_service_async_client.exceptions import ApiException
from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.dataverse import (
    filter_dataverse_metadata,
)
from aind_metadata_service_server.sessions import get_dataverse_api_instance

router = APIRouter()


@router.get(
    "/api/v2/dataverse/tables",
    responses={
        404: {"description": "Not found"},
    },
)
async def get_dataverse_table_info(
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Entity table identifying information
    Retrieves identifying information for all table entities in Dataverse.
    """
    dataverse_response = await dataverse_api_instance.get_table_info(
        _request_timeout=10
    )
    if not dataverse_response:
        raise HTTPException(status_code=404, detail="Not found")
    return dataverse_response


@router.get(
    "/api/v2/dataverse/tables/{entity_set_table_name}",
    responses={
        404: {"description": "Not found"},
    },
)
async def get_dataverse_table(
    entity_set_table_name: str = Path(
        ...,
        description="The entity set name of the table to fetch",
        openapi_examples={
            "default": {
                "summary": "A sample entity set name ID",
                "description": "Example entity set name",
                "value": "cr138_projects",
            }
        },
    ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Table Data
    Retrieves data for a specific entity table in Dataverse.
    """
    try:
        dataverse_response = await dataverse_api_instance.get_table(
            entity_set_table_name, _request_timeout=10
        )
        if not dataverse_response:
            raise HTTPException(status_code=404, detail="Not found")
        return filter_dataverse_metadata(dataverse_response)

    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=f"Error fetching {entity_set_table_name}: {e.reason}",
        )
