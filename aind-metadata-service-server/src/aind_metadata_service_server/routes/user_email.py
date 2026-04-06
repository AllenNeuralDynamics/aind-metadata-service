"""Module to handle endpoint responses"""

from fastapi import APIRouter, HTTPException, Depends
from aind_active_directory_service_async_client.exceptions import (
    NotFoundException,
)

from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_active_directory_api_instance,
)

router = APIRouter()


@router.get(
    "/api/v2/active_directory/{username}",
)
async def get_user_from_active_directory(
    username: str,
    azure_directory_api_instance=Depends(get_active_directory_api_instance),
):
    """Queries active directory for user information"""
    try:
        ad_user = (
            await azure_directory_api_instance.get_user_from_active_directory(
                username=username, _request_timeout=10
            )
        )
        if ad_user is None:
            raise HTTPException(status_code=404, detail="Not found")
        return map_to_response(ad_user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Not found")
