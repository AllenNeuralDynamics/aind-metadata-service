from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class BaseResponse(BaseModel):

    data: list
    totalCount: int
    pageSize: int
    page: int
    orderBy: Optional[str] = Field(default=None)
    order: Any
    morePages: bool
    search: Optional[str] = Field(default=None)
    searchFields: Optional[str] = Field(default=None)


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
    aliases: List[Alias] = Field(default=[])
    capsid: Optional[Any] = Field(default=None)
    citations: list = Field(default=None)
    molecules: list = Field(default=None)
    otherMolecules: list = Field(default=None)
    patents: list = Field(default=None)


class ViralPrepType(DataModel):
    name: Optional[str] = Field(default=None)


class ViralPrep(DataModel):
    rrId: Optional[Any] = Field(default=None)
    viralPrepType: Optional[ViralPrepType] = Field(default=None)
    virus: Optional[Virus] = Field(default=None)
    citations: list = Field(default=None)
    shipments: list = Field(default=None)
    patents: list = Field(default=[])
    materialTransferAgreements: list = Field(default=[])
    qcCertificationFiles: list = Field(default=[])
    serotypes: list = Field(default=[])


class Titers(DataModel):
    notes: Optional[str] = Field(default=None)
    isPreferred: Optional[bool] = Field(default=None)
    thawedCount: Optional[int] = Field(default=None)
    result: Optional[int] = Field(default=None)
    titerType: Optional[Any] = Field(default=None)


class PrepLotData(DataModel):
    lot: Optional[str] = Field(default=None)
    datePrepped: Optional[datetime] = Field(default=None)
    viralPrep: Optional[ViralPrep] = Field(default=None)
    titers: List[Titers] = Field(default=[])


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
    aliases: List[Alias] = Field(default=[])
    citations: list = Field(default=None)
    rrId: Optional[Any] = Field(default=None)
    fullName: Optional[str] = Field(default=None)
    addgeneId: Optional[Any] = Field(default=None)
    mgiId: Optional[Any] = Field(default=None)
    notes: Optional[Any] = Field(default=None)
    sequence: Optional[str] = Field(default=None)
    genes: list = Field(default=None)
    loci: list = Field(default=None)
    species: List[Species] = Field(default=[])
    organizations: list = Field(default=None)
    shipments: list = Field(default=None)
    materialTransferAgreements: list = Field(default=None)
    genBankFiles: List[str] = Field(default=[])
    mapFiles: List[str] = Field(default=[])
    fastaFiles: List[str] = Field(default=[])
    parents: list = Field(default=None)
    children: list = Field(default=None)
    patents: list = Field(default=None)
    creators: list = Field(default=None)
    principalInvestigator: Optional[Any] = Field(default=None)
    targetedCellPopulations: List[TargetedCellPopulation] = Field(default=[])
    validatedCellPopulations: list = Field(default=None)
    targetedRois: List[TargetedRoi] = Field(default=[])
    validatedRois: list = Field(default=None)
    genomeCoordinates: Optional[Any] = Field(default=None)


class MoleculeResponse(BaseResponse):
    data: List[MoleculeData] = Field(default=[])
