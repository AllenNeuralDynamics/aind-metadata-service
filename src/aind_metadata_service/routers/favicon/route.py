"""Favicon endpoint"""

import os

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

router = APIRouter()

# TODO: Handle favicon better?
favicon_path = os.getenv("FAVICON_PATH")


@router.get(
    "/favicon.ico",
    include_in_schema=False,
    response_class=RedirectResponse,
    response_description="Returns path of favicon",
    status_code=status.HTTP_200_OK,
)
async def favicon():
    """
    Returns the favicon
    """
    return favicon_path
