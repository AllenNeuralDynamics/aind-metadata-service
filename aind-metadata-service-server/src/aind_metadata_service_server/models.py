"""Models and schema definitions for backend data structures"""

from typing import Literal, Optional

from aind_data_schema.core.procedures import ViralMaterial
from pydantic import BaseModel, Field

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class ViralMaterialInformation(ViralMaterial):
    """Viral Material with Stock Titer."""

    stock_titer: Optional[int] = Field(default=None)
