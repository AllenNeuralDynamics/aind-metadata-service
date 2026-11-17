"""Maps information to aind-data-schema Procedures model."""

from datetime import datetime
from typing import List, Optional, Union

from aind_data_schema.core.procedures import (
    Antibody,
    ImmunolabelClass,
    Reagent,
    SpecimenProcedure,
    SpecimenProcedureType,
)
from aind_data_schema_models.organizations import Organization
from aind_dataverse_service_async_client.models import (
    HistologyModel,
    HistologyReagentModel,
    HistologyWashModel,
)


class SpecimenProcedureMapper:
    """Class to handle mapping of specimen procedure data."""

    def __init__(self, dataverse_histology: List[HistologyModel]):
        """Constructor for SpecimenProcedureMapper."""
        self.dataverse_histology = dataverse_histology

    @staticmethod
    def _parse_specimen_procedure_name(
        procedure_name: Optional[str],
    ) -> Union[SpecimenProcedure, None]:
        """Map procedure_name to procedure_type"""
        if procedure_name is None:
            procedure_type = None
        elif "DELIPIDATION" in procedure_name.upper():
            procedure_type = SpecimenProcedureType.DELIPIDATION
        elif "EXPANSION" in procedure_name.upper():
            procedure_type = SpecimenProcedureType.EXPANSION
        elif "REFRACTIVE INDEX MATCHING" in procedure_name.upper():
            procedure_type = SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING
        elif "LABELING" in procedure_name.upper():
            procedure_type = SpecimenProcedureType.IMMUNOLABELING
        elif "GELATION" in procedure_name.upper():
            procedure_type = SpecimenProcedureType.GELATION
        else:
            procedure_type = None
        return procedure_type

    def map_dataverse_response_to_aind_specimen_procedures(
        self,
    ) -> List[SpecimenProcedure]:
        """Maps response from dataverse into SpecimenProcedure models"""
        specimen_procedures = []
        for data in self.dataverse_histology:
            procedure_type = self._parse_specimen_procedure_name(
                data.procedure_name
            )
            if procedure_type is None:
                continue
            elif procedure_type == SpecimenProcedureType.IMMUNOLABELING:
                specimen_procedures.extend(
                    self._map_immunolabeling_procedure(data)
                )
            else:
                specimen_procedures.append(
                    self._map_specimen_procedure(
                        data, procedure_type=procedure_type
                    )
                )
        return specimen_procedures

    def _map_specimen_procedure(
        self, data: HistologyModel, procedure_type: SpecimenProcedureType
    ) -> SpecimenProcedure:
        """Maps histology data to SpecimenProcedure model"""
        washes = data.washes or []
        reagents = [
            reagent for wash in washes for reagent in (wash.reagents or [])
        ]
        start_time = washes[0].start_time if washes else None
        end_time = self._get_last_valid_end_time(washes)
        return SpecimenProcedure.model_construct(
            specimen_id=data.specimen_id,
            procedure_type=procedure_type,
            protocol_id=data.protocol_id,
            procedure_name=(
                data.protocol_name
                if getattr(data, "protocol_name", None)
                else data.procedure_name
            ),
            experimenter_full_name=(washes[0].modified_by if washes else None),
            start_date=start_time.date() if start_time else None,
            end_date=end_time.date() if end_time else None,
            reagents=self._map_reagents(reagents),
        )

    def _map_reagents(
        self, reagents: List[HistologyReagentModel]
    ) -> List[Reagent]:
        """Maps reagent data from dataverse to Reagent models"""
        return [
            Reagent.model_construct(
                name=reagent.name,
                source=Organization.from_name(reagent.source),
                lot_number=reagent.lot_number,
            )
            for reagent in reagents
        ]

    @staticmethod
    def _get_last_valid_end_time(
        washes: List[HistologyWashModel],
    ) -> Optional[datetime]:
        """Get the last valid end time from a list of washes"""
        for wash in reversed(washes):
            if wash.wash_type and wash.end_time:
                return wash.end_time
        return None

    def _map_immunolabeling_procedure(
        self, data: HistologyModel
    ) -> List[SpecimenProcedure]:
        """Maps histology data to SpecimenProcedure for immunolabeling."""
        immunolabeling_procedures = []
        for wash in data.washes or []:
            immunolabeling_procedures.append(
                SpecimenProcedure.model_construct(
                    specimen_id=data.specimen_id,
                    procedure_type=SpecimenProcedureType.IMMUNOLABELING,
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

    @staticmethod
    def _map_antibody(wash: HistologyWashModel) -> Optional[Antibody]:
        """Maps immunolabeling antibody. Dataverse does not provide mass."""
        if wash.wash_name == "Primary Antibody Wash":
            label = ImmunolabelClass.PRIMARY
        elif wash.wash_name == "Secondary Antibody Wash":
            label = ImmunolabelClass.SECONDARY
        else:
            return None
        return Antibody.model_construct(immunolabel_class=label, mass=None)
