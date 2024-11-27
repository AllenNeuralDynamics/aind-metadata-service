from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class BaseResponse(BaseModel):

    data: list
    totalCount: int
    pageSize: int
    page: int
    orderBy: str
    order: str
    morePages: bool
    search: Optional[str]
    searchFields: Optional[str]


class DataModel(BaseModel):
    createdAt: Optional[datetime] = Field(default=None)
    updatedAt: Optional[datetime] = Field(default=None)
    createdBy: Optional[str] = Field(default=None)
    updatedBy: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)


# PrepLot Models
class Alias(DataModel):
    citation: Optional[Any] = Field(default=None)
    isPreferred: Optional[bool] = Field(default=None)
    name: Optional[str] = Field(default=None)


class Virus(DataModel):
    rrId: Optional[Any] = Field(default=None)
    aliases: Optional[List[Alias]] = Field(default=None)
    capsid: Optional[Any] = Field(default=None)
    citations: Optional[list] = Field(default=None)
    molecules: Optional[list] = Field(default=None)
    otherMolecules: Optional[list] = Field(default=None)
    patents: Optional[list] = Field(default=None)


class ViralPrepType(DataModel):
    name: Optional[str] = Field(default=None)


class ViralPrep(DataModel):
    rrId: Optional[Any] = Field(default=None)
    viralPrepType: Optional[ViralPrepType] = Field(default=None)
    virus: Optional[Virus] = Field(default=None)
    citations: Optional[list] = Field(default=None)
    shipments: Optional[list] = Field(default=None)
    patents: Optional[list] = Field(default=None)
    materialTransferAgreements: Optional[list] = Field(default=None)
    qcCertificationFiles: Optional[list] = Field(default=None)
    serotypes: Optional[list] = Field(default=None)


class PrepLotData(DataModel):
    lot: Optional[str]
    datePrepped: Optional[datetime]


class PrepLotResponse(BaseResponse):
    data: List[PrepLotData] = Field(default=[])

# Molecule Models

class MoleculeType(DataModel):
    name: Optional[str] = Field(default=None)

class Species(DataModel):
    rorID: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)

class TargetedCellPopulation(DataModel):
    name: Optional[str] = Field(default=None)

class TargetedRoi(DataModel):
    name: Optional[str] = Field(default=None)

class MoleculeData(DataModel):
    moleculeType: Optional[MoleculeType] = Field(default=None)
    state: Optional[Any] = Field(default=None)
    aliases: Optional[List[Alias]] = Field(default=None)
    citations: Optional[list] = Field(default=None)
    rrId: Optional[Any] = Field(default=None)
    fullName: Optional[str] = Field(default=None)
    addgeneId: Optional[Any] = Field(default=None)
    mgiId: Optional[Any] = Field(default=None)
    notes: Optional[Any] = Field(default=None)
    sequence: Optional[str] = Field(default=None)
    genes: Optional[list] = Field(default=None)
    loci: Optional[list] = Field(default=None)
    species: Optional[List[Species]] = Field(default=None)
    organizations: Optional[list] = Field(default=None)
    shipments: Optional[list] = Field(default=None)
    materialTransferAgreements: Optional[list] = Field(default=None)
    genBankFiles: Optional[List[str]] = Field(default=None)
    mapFiles: Optional[List[str]] = Field(default=None)
    fastaFiles: Optional[List[str]] = Field(default=None)
    parents: Optional[list] = Field(default=None)
    children: Optional[list] = Field(default=None)
    patents: Optional[list] = Field(default=None)
    creators: Optional[list] = Field(default=None)
    principalInvestigator: Optional[Any] = Field(default=None)
    targetedCellPopulations: Optional[List[TargetedCellPopulation]] = Field(default=None)
    validatedCellPopulations: Optional[list] = Field(default=None)
    targetedRois: Optional[List[TargetedRoi]] = Field(default=None)
    validatedRois: Optional[list] = Field(default=None)
    genomeCoordinates: Optional[Any] = Field(default=None)
