"""Models and schema definitions for backend data structures"""

import html
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional, List

from aind_data_schema.core.data_description import Funding
from aind_data_schema.core.procedures import ViralMaterial
from aind_slims_service_async_client import (
    SlimsSpimData,
    SlimsHistologyData,
    EcephysStreamModule,
    SlimsEcephysData
)
from pydantic import BaseModel, Field, field_validator

from aind_metadata_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class ViralMaterialInformation(ViralMaterial):
    """Viral Material with Stock Titer."""

    stock_titer: Optional[int] = Field(default=None)


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


class ProtocolNames(Enum):
    """Enum of Protocol Names in Smartsheet"""

    IMMUNOLABELING = "Immunolabeling of a Whole Mouse Brain"
    DELIPIDATION = (
        "Tetrahydrofuran and Dichloromethane Delipidation of a"
        " Whole Mouse Brain"
    )
    SBIP_DELIPADATION = "Aqueous (SBiP) Delipidation of a Whole Mouse Brain"
    GELATIN_PREVIOUS = (
        "Whole Mouse Brain Delipidation, Immunolabeling,"
        " and Expansion Microscopy"
    )
    INJECTION_NANOJECT = "Injection of Viral Tracers by Nanoject V.4"
    INJECTION_IONTOPHORESIS = (
        "Stereotaxic Surgery for Delivery of Tracers by Iontophoresis V.3"
    )
    PERFUSION = "Mouse Cardiac Perfusion Fixation and Brain Collection V.5"
    SMARTSPIM_IMAGING = "Imaging cleared mouse brains on SmartSPIM"
    SMARTSPIM_SETUP = "SmartSPIM setup and alignment"
    SURGERY = "General Set-Up and Take-Down for Rodent Neurosurgery"
    PROTOCOL_COLLECTION = (
        "Protocol Collection: Perfusing, Sectioning, IHC,"
        " Mounting and Coverslipping Mouse Brain Specimens"
    )
    SECTIONING = "Sectioning Mouse Brain with Sliding Microtome"
    MOUNTING_COVERSLIPPING = "Mounting and Coverslipping Mouse Brain Sections"
    IHC_SECTIONS = "Immunohistochemistry (IHC) Staining Mouse Brain Sections"
    DAPI_STAINING = "DAPI Staining Mouse Brain Sections"
    DURAGEL_APPLICATION = (
        "Duragel application for acute electrophysiological recordings"
    )


class SpimData(SlimsSpimData):
    """Class to for Slims Spim Data with proper datetime info."""

    date_performed: Optional[datetime] = Field(default=None)

    @field_validator("protocol_id", mode="before")
    @classmethod
    def parse_protocol_id(cls, v: Any) -> Optional[str]:
        """Parses protocol id from html"""
        if v is None:
            return None
        try:
            root = ET.fromstring(v)
            return root.get("href")
        except ET.ParseError:
            return v
        except Exception as e:
            logging.warning(
                f"There was an exception parsing the protocol_id field: {e}"
            )
            return None


class HistologyData(SlimsHistologyData):
    """Class to for Slims Histology Data with proper protocol id."""

    @field_validator("protocol_id", mode="before")
    @classmethod
    def parse_protocol_id(cls, v: Any) -> Optional[str]:
        """Parses protocol id from html"""
        if v is None:
            return None
        try:
            root = ET.fromstring(v)
            return root.get("href")
        except ET.ParseError:
            return v
        except Exception as e:
            logging.warning(
                f"There was an exception parsing the protocol_id field: {e}"
            )
            return None


class EcephysStreamModuleData(EcephysStreamModule):
    """Class for Slims Ecephys Stream Data with proper unit"""
    @field_validator(
        "ccf_coordinate_unit",
        "bregma_target_unit",
        "surface_z_unit",
        "manipulator_unit",
        mode="before",
    )
    @classmethod
    def parse_micrometer_unit(cls, v):
        """Parse HTML entity for micrometer"""
        if isinstance(v, str):
            v = html.unescape(v)
        return v


class EcephysData(SlimsEcephysData):
    """Class for Slims Ecephys Data with proper stream data"""

    stream_modules: Optional[List[EcephysStreamModuleData]] = None
