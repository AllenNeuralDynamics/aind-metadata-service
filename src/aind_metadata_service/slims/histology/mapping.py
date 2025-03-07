"""Module for mapping histology data from slims"""

from datetime import datetime
from typing import List, Optional

from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

from aind_metadata_service.slims.histology.handler import (
    SlimsHistologyData,
    SlimsReagentData,
)
from aind_metadata_service.slims.table_handler import parse_html


class WashData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    wash_name: Optional[str] = None
    wash_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    modified_by: Optional[str] = None
    reagents: List[SlimsReagentData] = []


class HistologyData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    procedure_name: Optional[str] = None
    experiment_run_created_on: Optional[datetime] = None
    specimen_id: Optional[str] = None
    subject_id: Optional[str] = None
    protocol_id: Optional[str] = None
    protocol_name: Optional[str] = None
    procedure_type: Optional[SpecimenProcedureType] = None
    washes: List[WashData] = []

    @field_validator("protocol_id")
    def parse_protocol_id(cls, v: Optional[str]) -> Optional[str]:
        """Parse link from html tag"""
        return parse_html(v)

    @model_validator(mode="after")
    def parse_procedure_name(self) -> Self:
        """Map procedure_name to procedure_type"""
        procedure_name = self.procedure_name
        if procedure_name is None:
            self.procedure_type = None
        elif "DELIPIDATION" in procedure_name.upper():
            self.procedure_type = SpecimenProcedureType.DELIPIDATION
        elif "EXPANSION" in procedure_name.upper():
            self.procedure_type = SpecimenProcedureType.EXPANSION
        elif "REFRACTIVE INDEX MATCHING" in procedure_name.upper():
            self.procedure_type = (
                SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING
            )
        elif "LABELING" in procedure_name.upper():
            self.procedure_type = SpecimenProcedureType.IMMUNOLABELING
        elif "GELATION" in procedure_name.upper():
            self.procedure_type = SpecimenProcedureType.GELATION
        else:
            self.procedure_type = None
        return self


class SlimsHistologyMapper:
    """Mapper class for Slims histology procedures"""

    def __init__(self, slims_hist_data: List[SlimsHistologyData]):
        """Class constructor"""
        self.slims_hist_data = slims_hist_data

    def map_info_from_slims(self) -> List[HistologyData]:
        """Maps info from slims into data model"""

        hist_data = [
            HistologyData.model_validate(m.model_dump())
            for m in self.slims_hist_data
        ]
        hist_data.sort(
            key=lambda m: (
                m.experiment_run_created_on is None,
                m.experiment_run_created_on,
            ),
            reverse=True,
        )
        return hist_data
