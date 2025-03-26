"""Module for mapping histology data from slims"""

from datetime import datetime
from typing import List, Optional

from aind_data_schema.core.procedures import (
    Antibody,
    ImmunolabelClass,
    Reagent,
    SpecimenProcedure,
)
from aind_data_schema_models.organizations import Organization
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
    mass: Optional[float] = None


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

    def map_slims_info_to_specimen_procedures(self) -> List[SpecimenProcedure]:
        """Maps response from slims into SpecimenProcedure models"""
        hist_data = [
            HistologyData.model_validate(m.model_dump())
            for m in self.slims_hist_data
        ]
        specimen_procedures = []
        for data in hist_data:
            if data.procedure_type is None:
                continue
            elif data.procedure_type == SpecimenProcedureType.IMMUNOLABELING:
                immunolabeling_procedures = self._map_immunolabeling_procedure(
                    data
                )
                specimen_procedures.extend(immunolabeling_procedures)
            else:
                specimen_procedures.append(self._map_specimen_procedure(data))
        return specimen_procedures

    def _map_specimen_procedure(
        self, data: HistologyData
    ) -> SpecimenProcedure:
        """Maps histology data to SpecimenProcedure model"""
        reagents = [
            reagent for wash in data.washes for reagent in wash.reagents
        ]
        start_time = data.washes[0].start_time
        end_time = self._get_last_valid_end_time(data.washes)
        return SpecimenProcedure.model_construct(
            specimen_id=data.subject_id,
            procedure_type=data.procedure_type,
            protocol_id=data.protocol_id,
            procedure_name=(
                data.protocol_name
                if getattr(data, "protocol_name", None)
                else data.procedure_name
            ),
            experimenter_full_name=data.washes[0].modified_by,
            start_date=start_time.date() if start_time else None,
            end_date=end_time.date() if end_time else None,
            reagents=self._map_reagents(reagents),
        )

    def _map_reagents(self, reagents: List[SlimsReagentData]) -> List[Reagent]:
        """Maps reagent data from slims to Reagent models"""
        return [
            Reagent.model_construct(
                name=reagent.name,
                source=Organization.from_name(reagent.source),
                lot_number=reagent.lot_number,
            )
            for reagent in reagents
        ]

    @staticmethod
    def _get_last_valid_end_time(washes: List[WashData]) -> Optional[datetime]:
        """Get the last valid end time from a list of washes"""
        for wash in reversed(washes):
            if wash.wash_type and wash.end_time:
                return wash.end_time
        return None

    def _map_immunolabeling_procedure(
        self, data: HistologyData
    ) -> List[SpecimenProcedure]:
        """Maps histology data to SpecimenProcedure."""
        immunolabeling_procedures = []
        for wash in data.washes:
            immunolabeling_procedures.append(
                SpecimenProcedure.model_construct(
                    specimen_id=data.subject_id,
                    procedure_type=data.procedure_type,
                    protocol_id=data.protocol_id,
                    procedure_name=(
                        data.protocol_name
                        if getattr(data, "protocol_name", None)
                        else data.procedure_name
                    ),
                    start_date=(
                        wash.start_time.date() if wash.start_time else None
                    ),
                    end_date=wash.end_time.date() if wash.end_time else None,
                    experimenter_full_name=wash.modified_by,
                    antibodies=self._map_antibody(wash),
                )
            )
        return immunolabeling_procedures

    def _map_antibody(self, wash: WashData) -> Optional[Antibody]:
        """Maps immunolabeling antibody"""
        # TODO: add fluor data once in SLIMS
        if wash.wash_name == "Primary Antibody Wash":
            label = ImmunolabelClass.PRIMARY
        elif wash.wash_name == "Secondary Antibody Wash":
            label = ImmunolabelClass.SECONDARY
        return Antibody.model_construct(
            immunolabel_class=label,
            mass=wash.mass,
        )
