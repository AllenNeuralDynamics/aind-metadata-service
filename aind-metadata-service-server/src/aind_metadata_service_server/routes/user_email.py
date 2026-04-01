"""Module to handle endpoint responses"""

from fastapi import APIRouter, HTTPException, status, Depends

from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_active_directory_api_instance

router = APIRouter()


@router.get(
    "/api/v2/active_directory/{username}",
)
async def get_user_from_active_directory(
    username: str,
    azure_directory_api_instance=Depends(get_active_directory_api_instance)
):
    """Queries active directory for user information

    Params:
        username (str): user login or full name

    Returns:
        UserInfo: user information from Active Directory
    """
    ad_response = await azure_directory_api_instance.get_user_from_active_directory(
        username=username, _request_timeout=10
    )
    if ad_response is None:
        raise HTTPException(
            status_code=404,
            detail=f"User {username} not found in the institute Active Directory",
        )
    return map_to_response(ad_response)