"""Additional response models not defined in aind-data-schema"""

from typing import Optional

from aind_data_schema.core.data_description import Funding
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
