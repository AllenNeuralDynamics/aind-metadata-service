"""Models and schema definitions for backend data structures"""

from typing import Literal

from pydantic import BaseModel

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__
