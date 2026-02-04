"""Module to handle dataverse endpoints"""

from functools import cache
from fastapi import APIRouter, Depends, HTTPException, Path
from aind_metadata_service_server.sessions import get_dataverse_api_instance
router = APIRouter()

@router.get("/api/v2/dataverse/tables")
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

@router.get("/api/v2/dataverse/tables/{entity_set_table_name}")
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
    dataverse_response = await dataverse_api_instance.get_table(
        entity_set_table_name,
        _request_timeout=10
    )
    if not dataverse_response:
        raise HTTPException(status_code=404, detail="Not found")
    return dataverse_response


