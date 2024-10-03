"""
Entrypoint to get a healthcheck from the service.
"""

from typing import Literal

from aind_data_schema import __version__ as data_schema_version
from aind_data_schema_models import __version__ as data_schema_models_version
from fastapi import APIRouter, status
from pydantic import BaseModel

from aind_metadata_service import __version__ as service_version

router = APIRouter()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    aind_metadata_service_version: str = service_version
    aind_data_schema_models_version: str = data_schema_models_version
    aind_data_schema_version: str = data_schema_version


@router.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def get_health() -> HealthCheck:
    """
    Endpoint to perform a healthcheck on.

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck()
