"""Models and schema definitions for backend data structures"""

from datetime import datetime
from typing import Literal, Optional

from aind_data_schema.components.injection_procedures import ViralMaterial
from pydantic import BaseModel, Field, field_validator

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class ProtocolInformation(BaseModel):
    """Protocol information that will be returned to the user that requests
    information from the Protocols SmartSheet"""

    protocol_type: str = Field(..., description="Protocol Type")
    procedure_name: str = Field(..., description="Procedure name")
    protocol_name: str = Field(..., description="Protocol name")
    doi: str = Field(..., description="DOI")
    version: str = Field(..., description="Version")
    protocol_collection: Optional[bool] = Field(
        None, description="Protocol Collection"
    )

    @field_validator("version", mode="before")
    def transform_version_to_str(cls, value) -> Optional[str]:
        """Converts floats and other types to strings"""
        if value is None:
            return None
        else:
            return str(value)


class ViralMaterialInformation(ViralMaterial):
    """Viral Material with Stock Titer."""

    stock_titer: Optional[int] = Field(default=None)


class IntendedMeasurementInformation(BaseModel):
    """Intended Measurement information that will be returned to the user that
    requests information from the NSB2023 Sharepoint."""

    fiber_name: Optional[str] = None
    intended_measurement_R: Optional[str] = None
    intended_measurement_G: Optional[str] = None
    intended_measurement_B: Optional[str] = None
    intended_measurement_Iso: Optional[str] = None


class MouseWeightData(BaseModel):
    """Class for Mouse Weight Data with proper datetime info"""

    record_id: Optional[str] = Field(
        default=None, description="Unique record ID"
    )
    mouse_id: Optional[str] = Field(
        default=None, description="Subject/Mouse ID"
    )
    weight: Optional[float] = Field(
        default=None, description="Weight in grams"
    )
    weight_datetime: Optional[datetime] = Field(
        default=None, description="When the weight was measured"
    )
    is_baseline_weight: Optional[bool] = Field(
        default=None, description="Whether this is a baseline weight"
    )
    operator: Optional[str] = Field(
        default=None, description="Person who performed the weighing"
    )
    workstation: Optional[str] = Field(
        default=None, description="Workstation where weight was recorded"
    )
    software_version: Optional[str] = Field(
        default=None, description="Software version used"
    )
    software_source: Optional[str] = Field(
        default=None, description="Source system (e.g., WL)"
    )
    status: Optional[str] = Field(default=None, description="Record status")
    notes: Optional[str] = Field(default=None, description="Additional notes")
