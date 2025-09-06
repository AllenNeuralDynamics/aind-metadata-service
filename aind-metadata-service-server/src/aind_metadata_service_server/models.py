"""Models and schema definitions for backend data structures"""

from typing import Literal, Optional

from pydantic import BaseModel

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class IntendedMeasurementInformation(BaseModel):
    """Intended Measurement information that will be returned to the user that
    requests information from the NSB2023 Sharepoint."""

    fiber_name: Optional[str] = None
    intended_measurement_R: Optional[str] = None
    intended_measurement_G: Optional[str] = None
    intended_measurement_B: Optional[str] = None
    intended_measurement_Iso: Optional[str] = None
