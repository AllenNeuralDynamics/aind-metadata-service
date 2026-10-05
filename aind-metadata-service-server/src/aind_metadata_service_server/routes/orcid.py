"""Module to handle orcid endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from orcid_service_async_client.exceptions import NotFoundException

from aind_metadata_service_server.sessions import get_orcid_api_instance

router = APIRouter()


@router.get("/api/v2/orcid/{name}")
async def get_orcid(
    name: str,
    orcid_api_instance=Depends(get_orcid_api_instance),
):
    """
    ## ORCID
    Return an Allen Institute researcher's ORCID iD, or 404 when the match
    is not definitive. See orcid-service for how the match is made.
    """
    try:
        return await orcid_api_instance.get_orcid(
            name=name, _request_timeout=10
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Not found")
