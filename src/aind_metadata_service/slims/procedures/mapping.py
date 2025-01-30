"""Module for mapping specimen procedures"""

import xml.etree.ElementTree as ET
from typing import List, Optional

from aind_data_schema.components.reagent import Reagent
from aind_data_schema.core.procedures import (
    Antibody,
    ImmunolabelClass,
    SpecimenProcedure,
)
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from aind_slims_api.operations.histology_procedures import (
    SlimsWash,
    SPIMHistologyExpBlock,
)

from aind_metadata_service.slims.procedures.models import (
    SlimsExperimentTemplateNames,
    SlimsWashNames,
)


class SlimsHistologyMapper:
    """Mapper class for Slims histology procedures"""

    def map_specimen_procedures(
        self, slims_blocks: List[SPIMHistologyExpBlock], specimen_id: str
    ):
        """Map specimen procedures from Slims histology data"""
        specimen_procedures = []
        for block in slims_blocks:
            procedure_type = self._map_procedure_type(
                block.experiment_template.name
            )
            if procedure_type is None:
                continue
            elif procedure_type == SpecimenProcedureType.IMMUNOLABELING:
                procs = self.map_immunolabeling(block, specimen_id)
                specimen_procedures.extend(procs)
            else:
                specimen_procedure = self._map_specimen_procedure(
                    block, procedure_type, specimen_id
                )
                specimen_procedures.append(specimen_procedure)
        return specimen_procedures

    def _map_specimen_procedure(
        self,
        block: SPIMHistologyExpBlock,
        procedure_type: SpecimenProcedureType,
        specimen_id: str,
    ) -> SpecimenProcedure:
        """Map specimen procedure from block name and procedure name"""
        spec = SpecimenProcedure.model_construct(
            specimen_id=specimen_id,
            procedure_type=procedure_type,  # method to map these
            procedure_name=getattr(block.protocol, "name", None),
            start_date=(
                block.washes[0].wash_step.start_time.date()
                if block.washes
                and block.washes[0].wash_step
                and block.washes[0].wash_step.start_time
                else None
            ),
            end_date=(
                block.washes[-1].wash_step.end_time.date()
                if block.washes
                and block.washes[-1].wash_step
                and block.washes[-1].wash_step.end_time
                else None
            ),
            experimenter_full_name=(
                self._map_experimenters(block.washes) if block.washes else None
            ),  # Experimenter mapping
            protocol_id=(
                [self._extract_protocol_link(block.protocol.link)]
                if getattr(block.protocol, "link", None)
                else []
            ),
            reagents=(
                self._map_reagents(block.washes) if block.washes else None
            ),  # Reagent mapping
        )
        return spec

    def map_immunolabeling(
        self, block: SPIMHistologyExpBlock, specimen_id: str
    ) -> List[SpecimenProcedure]:
        """Map immunolabeling procedure for each antibody wash"""
        procedures = []
        for wash in block.washes:
            spec = SpecimenProcedure.model_construct(
                specimen_id=specimen_id,
                procedure_type=SpecimenProcedureType.IMMUNOLABELING,
                procedure_name=getattr(
                    block.protocol, "name", None
                ),  # Safely access protocol name
                start_date=(
                    wash.wash_step.start_time.date()
                    if wash and wash.wash_step and wash.wash_step.start_time
                    else None
                ),  # First wash start time
                end_date=(
                    wash.wash_step.end_time.date()
                    if wash and wash.wash_step and wash.wash_step.end_time
                    else None
                ),  # Last wash end time
                experimenter_full_name=(
                    self._map_experimenters(block.washes)
                    if block.washes
                    else None
                ),  # Experimenter mapping
                protocol_id=(
                    [self._extract_protocol_link(block.protocol.link)]
                    if getattr(block.protocol, "link", None)
                    else []
                ),
                antibodies=(
                    [self._map_antibody(wash)] if wash else []
                ),  # Antibody mapping
            )
            procedures.append(spec)
        return procedures

    @staticmethod
    def _map_antibody(wash: SlimsWash) -> Optional[Antibody]:
        """Map antibody reagent from wash"""
        if not hasattr(wash, "wash_step") or wash.wash_step is None:
            return None
        wash_name = getattr(wash.wash_step, "wash_name", None)
        if wash_name == SlimsWashNames.PRIMARY_ANTIBODY_WASH.value:
            label = ImmunolabelClass.PRIMARY
        elif wash_name == SlimsWashNames.SECONDARY_ANTIBODY_WASH.value:
            label = ImmunolabelClass.SECONDARY
        else:
            return None
        mass = getattr(wash.wash_step, "mass", None)
        return Antibody.model_construct(
            immunolabel_class=label,
            mass=mass,
        )

    def _map_reagents(self, washes: List[SlimsWash]) -> List[Reagent]:
        """Map info from washes"""
        reagents = []
        for wash in washes:
            for reagent in wash.reagents:
                reagent_model = Reagent.model_construct(
                    name=getattr(reagent.details, "name", None),
                    source=(
                        self._map_source(reagent.source.name)
                        if getattr(reagent.source, "name", None)
                        else None
                    ),
                    lot_number=getattr(reagent.content, "lot_number", None),
                )
                reagents.append(reagent_model)
        return reagents

    @staticmethod
    def _map_source(source_name: str) -> Optional[Organization]:
        """Map source name to source type"""
        return Organization.from_name(source_name)

    @staticmethod
    def _map_procedure_type(
        block_name: str,
    ) -> Optional[SpecimenProcedureType]:
        """Map procedure type from experiment template name"""
        if (
            block_name == SlimsExperimentTemplateNames.SMARTSPIM_LABELING
            or block_name == SlimsExperimentTemplateNames.EXASPIM_LABELING
        ):
            return SpecimenProcedureType.IMMUNOLABELING
        elif (
            block_name == SlimsExperimentTemplateNames.SMARTSPIM_DELIPIDATION
            or block_name == SlimsExperimentTemplateNames.EXASPIM_DELIPIDATION
        ):
            return SpecimenProcedureType.DELIPIDATION
        elif block_name == SlimsExperimentTemplateNames.SMARTSPIM_RI_MATCHING:
            return SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING
        elif block_name == SlimsExperimentTemplateNames.EXASPIM_GELATION:
            return SpecimenProcedureType.GELATION
        elif block_name == SlimsExperimentTemplateNames.EXASPIM_EXPANSION:
            return SpecimenProcedureType.EXPANSION
        else:
            return None

    @staticmethod
    def _map_experimenters(washes: List[SlimsWash]):
        """Map unique experimenter names from washes"""
        unique_experimenters = list(
            {
                getattr(wash.wash_step, "modified_by", None)
                for wash in washes
                if hasattr(wash, "wash_step") and wash.wash_step is not None
            }
        )
        # Filter out None values
        unique_experimenters = [
            exp for exp in unique_experimenters if exp is not None
        ]
        if len(unique_experimenters) == 1:
            return unique_experimenters[0]
        return unique_experimenters

    def _extract_protocol_link(self, protocol_html: str) -> Optional[str]:
        """Parses out protocol link"""
        root = ET.fromstring(protocol_html)
        return root.get("href")
