"""Models and schema definitions for backend data structures"""

from typing import Literal, Optional

from aind_data_schema.core.data_description import Funding
from pydantic import BaseModel, Field, field_validator

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class FundingInformation(Funding):
    """Funding information that will be returned to the user that requests
    information from the Funding SmartSheet"""

    investigators: Optional[str] = Field(default=None)


class ProtocolInformation(BaseModel):
    """Protocol information that will be returned to the user that requests
    information from the Protocols SmartSheet"""

    protocol_type: str = Field(..., description="Protocol Type")
    procedure_name: str = Field(..., description="Procedure name")
    protocol_name: str = Field(..., description="Protocol name")
    doi: str = Field(..., description="DOI")
    version: str = Field(..., description="Version")
    protocol_collection: Optional[str] = Field(
        None, description="Protocol Collection"
    )

    @field_validator("version", "protocol_collection", mode="before")
    def transform_version_to_str(cls, value) -> Optional[str]:
        """Converts floats to strings"""
        if value is None:
            return None
        else:
            return str(value)


class IntendedMeasurementInformation(BaseModel):
    """Intended Measurement information that will be returned to the user that
    requests information from the NSB2023 Sharepoint."""

    fiber_name: Optional[str] = None
    intended_measurement_R: Optional[str] = None
    intended_measurement_G: Optional[str] = None
    intended_measurement_B: Optional[str] = None
    intended_measurement_Iso: Optional[str] = None
