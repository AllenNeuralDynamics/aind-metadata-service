"""Maps information to aind-data-schema SpecimenProcedure model."""

from datetime import datetime
from typing import List, Optional, Union

from aind_data_schema.components.reagent import (
    Reagent,
)
from aind_data_schema.components.specimen_procedures import (
    SpecimenProcedure,
)
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from aind_dataverse_service_async_client.models import (
    HistologyModel,
    HistologyReagentModel,
    HistologyWashModel,
)
from pydantic import ValidationError


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
                # smartspim is not doing immunolabeling
                continue
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
        fields = dict(
            specimen_id=data.specimen_id,
            procedure_type=procedure_type,
            protocol_id=[data.protocol_id] if data.protocol_id else None,
            procedure_name=(
                data.protocol_name
                if getattr(data, "protocol_name", None)
                else data.procedure_name
            ),
            experimenters=([washes[0].modified_by] if washes else None),
            start_date=start_time.date() if start_time else None,
            end_date=end_time.date() if end_time else None,
            procedure_details=self._map_reagents(reagents),
        )
        try:
            return SpecimenProcedure(**fields)
        except ValidationError:
            return SpecimenProcedure.model_construct(**fields)

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
