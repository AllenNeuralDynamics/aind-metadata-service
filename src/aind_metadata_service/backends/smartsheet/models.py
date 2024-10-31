"""Module for defining models from Smartsheet"""

from datetime import date as date_type
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProtocolNames(str, Enum):
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


class FundingModel(BaseModel):
    """Expected model for the Funding Sheet"""

    project_name: Optional[str] = Field(None, alias="Project Name")
    project_code: Optional[str] = Field(None, alias="Project Code")
    funding_institution: Optional[str] = Field(
        None, alias="Funding Institution"
    )
    grant_number: Optional[str] = Field(None, alias="Grant Number")
    investigators: Optional[str] = Field(None, alias="Investigators")
    model_config = ConfigDict(populate_by_name=True)


class PerfusionsModel(BaseModel):
    """Expected model for the Perfusions SmartSheet"""

    subject_id: Optional[Decimal] = Field(None, alias="subject id")
    date: Optional[date_type] = Field(None, alias="date")
    experimenter: Optional[str] = Field(None, alias="experimenter")
    iacuc_protocol: Optional[str] = Field(None, alias="iacuc protocol")
    animal_weight_prior: Optional[Decimal] = Field(
        None, alias="animal weight prior (g)"
    )
    output_specimen_id: Optional[Decimal] = Field(
        None, alias="Output specimen id(s)"
    )
    postfix_solution: Optional[str] = Field(None, alias="Postfix solution")
    notes: Optional[str] = Field(None, alias="Notes")
    model_config = ConfigDict(populate_by_name=True)


class ProtocolsModel(BaseModel):
    """Expected model for the Protocols SmartSheet"""

    protocol_type: Optional[str] = Field(None, alias="Protocol Type")
    procedure_name: Optional[str] = Field(None, alias="Procedure name")
    protocol_name: Optional[str] = Field(None, alias="Protocol name")
    doi: Optional[str] = Field(None, alias="DOI")
    version: Optional[Decimal] = Field(None, alias="Version")
    protocol_collection: Optional[bool] = Field(
        None, alias="Protocol collection"
    )
    model_config = ConfigDict(populate_by_name=True)
