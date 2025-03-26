"""Additional response models not defined in aind-data-schema"""

from datetime import datetime
from typing import Optional

from aind_data_schema.core.data_description import Funding
from aind_data_schema.core.procedures import ViralMaterial
from pydantic import BaseModel, Field, field_validator


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


class FundingInformation(Funding):
    """Funding information that will be returned to the user that requests
    information from the Funding SmartSheet"""

    investigators: Optional[str] = Field(default=None)


# TODO: remove this as its not being used
class SpimImagingInformation(BaseModel):
    """SmartSPIM Imaging information that will be returned to the user that
    requests information from the SmartSPIM Imaging SLIMS Workflow"""

    specimen_id: str = Field(..., description="Specimen ID")
    subject_id: str = Field(..., description="Subject ID")
    protocol_name: Optional[str] = Field(None, description="Protocol Name")
    protocol_id: Optional[str] = Field(None, description="Protocol ID")
    date_performed: Optional[datetime] = Field(
        None, description="Date Performed"
    )
    chamber_immersion_medium: Optional[str] = Field(
        None, description="Chamber Immersion Medium"
    )
    sample_immersion_medium: Optional[str] = Field(
        None, description="Sample Immersion Medium"
    )
    chamber_refractive_index: Optional[float] = Field(
        None, description="Chamber Refractive Index"
    )
    sample_refractive_index: Optional[float] = Field(
        None, description="Sample Refractive Index"
    )
    instrument_id: Optional[str] = Field(None, description="Instrument ID")
    experimenter_name: Optional[str] = Field(
        None, description="Experimenter Name"
    )
    z_direction: Optional[str] = Field(None, description="Z Direction")
    y_direction: Optional[str] = Field(None, description="Y Direction")
    x_direction: Optional[str] = Field(None, description="X Direction")


class ViralMaterialInformation(ViralMaterial):
    """Viral Material with Stock Titer from SLIMS"""

    stock_titer: Optional[int] = Field(default=None)


class IntendedMeasurementInformation(BaseModel):
    """Intended Measurement information that will be returned to the user that
    requests information from the NSB2023 Sharepoint."""

    fiber_name: Optional[str] = None
    intended_measurement_R: Optional[str] = None
    intended_measurement_G: Optional[str] = None
    intended_measurement_B: Optional[str] = None
    intended_measurement_Iso: Optional[str] = None
