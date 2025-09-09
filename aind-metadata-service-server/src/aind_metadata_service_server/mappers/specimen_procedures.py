"""Maps information to aind-data-schema Procedures model."""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from aind_data_schema.components.specimen_procedures import (
    SpecimenProcedure,
)
from aind_data_schema.components.reagent import (
    ProbeReagent,
    Reagent,
    ProteinProbe,
)
from aind_data_schema_models.specimen_procedure_types import SpecimenProcedureType
from aind_data_schema_models.organizations import Organization
from aind_slims_service_async_client.models import (
    HistologyReagentData,
    HistologyWashData,
    SlimsHistologyData,
)


class SpecimenProcedureMapper:
    """Class to handle mapping of specimen procedure data."""

    def __init__(self, slims_histology: List[SlimsHistologyData]):
        """Constructor for SpecimenProcedureMapper."""
        self.slims_histology = slims_histology

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

    @staticmethod
    def _parse_html(v: Optional[str]) -> Optional[str]:
        """Parse link from html tag"""
        if v is None:
            return None
        try:
            root = ET.fromstring(v)
            return root.get("href")
        except ET.ParseError:
            return v
        except Exception as e:
            logging.warning(f"An exception occurred parsing link {v}: {e}")
            return None

    def map_slims_response_to_aind_specimen_procedures(
        self,
    ) -> List[SpecimenProcedure]:
        """Maps response from slims into SpecimenProcedure models"""
        specimen_procedures = []
        for data in self.slims_histology:
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
        self, data: SlimsHistologyData, procedure_type: SpecimenProcedureType
    ) -> SpecimenProcedure:
        """Maps histology data to SpecimenProcedure model"""
        reagents = [
            reagent for wash in data.washes for reagent in wash.reagents
        ]
        start_time = data.washes[0].start_time if data.washes else None
        end_time = self._get_last_valid_end_time(data.washes)
        return SpecimenProcedure.model_construct(
            specimen_id=data.subject_id,
            procedure_type=procedure_type,
            protocol_id=self._parse_html(data.protocol_id),
            procedure_name=(
                data.protocol_name
                if getattr(data, "protocol_name", None)
                else data.procedure_name
            ),
            experimenter_full_name=(
                data.washes[0].modified_by if data.washes else None
            ),
            start_date=start_time.date() if start_time else None,
            end_date=end_time.date() if end_time else None,
            reagents=self._map_reagents(reagents),
        )

    def _map_reagents(
        self, reagents: List[HistologyReagentData]
    ) -> List[Reagent]:
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
    def _get_last_valid_end_time(
        washes: List[HistologyWashData],
    ) -> Optional[datetime]:
        """Get the last valid end time from a list of washes"""
        for wash in reversed(washes):
            if wash.wash_type and wash.end_time:
                return wash.end_time
        return None

    def _map_immunolabeling_procedure(
        self, data: SlimsHistologyData
    ) -> List[SpecimenProcedure]:
        """Maps histology data to SpecimenProcedure for immunolabeling."""
        immunolabeling_procedures = []
        for wash in data.washes:
            immunolabeling_procedures.append(
                SpecimenProcedure.model_construct(
                    specimen_id=data.subject_id,
                    procedure_type=SpecimenProcedureType.IMMUNOLABELING,
                    protocol_id=self._parse_html(data.protocol_id),
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


    # TODO: need to figure this out with data-schema
    def _map_antibody(self, wash: HistologyWashData) -> Optional[ProbeReagent, ]:
        """Maps immunolabeling antibody"""
        if wash.wash_name == "Primary Antibody Wash":
            # label = ImmunolabelClass.PRIMARY
            mass = getattr(wash, "mass", None)
            target = ProteinProbe(
                    protein=PIDName(name="GFP", registry=Registry.UNIPROT, registry_identifier="P42212"),
                    mass=float(mass) if mass is not None else 0,
                    mass_unit=MassUnit.UG,
                    species=Species.CHICKEN,
                )
            return ProbeReagent(
                target=target,
                name="Chicken polyclonal to GFP",
                source=None, # can we assume a source? 
                rrid=PIDName(name="Chicken polyclonal to GFP", registry=Registry.RRID, registry_identifier="ab13970"),
            )

        elif wash.wash_name == "Secondary Antibody Wash":
            probe = ProteinProbe(
                    protein=PIDName(name="TODO", registry=Registry.UNIPROT, registry_identifier="unknown"),
                    mass=4,
                    mass_unit="microgram",
                    species=Species.CHICKEN,
                )

            fluorophore = Fluorophore(
                    fluorophore_type=FluorophoreType.ALEXA,
                    excitation_wavelength=488,
                    excitation_wavelength_unit=SizeUnit.NM,
                )
            return FluorescentStain.model_construct(
                    name=upgraded_data["rrid"]["name"],
                    source=None,
                    stain_type=StainType.PROTEIN,
                    fluorophore=fluorophore,
                )
        else:
            return None
        return Antibody.model_construct(
            immunolabel_class=label,
            mass=Decimal(wash.mass) if wash.mass else None,
        )