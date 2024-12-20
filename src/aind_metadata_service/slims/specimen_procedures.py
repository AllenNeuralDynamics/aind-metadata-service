"""Module for mapping specimen procedures"""

from aind_data_schema.core.procedures import SpecimenProcedure, ImmunolabelClass, Antibody
from aind_data_schema.components.reagent import Reagent
from aind_data_schema_models.specimen_procedure_types import SpecimenProcedureType
from aind_data_schema_models.organizations import Organization
from aind_slims_api.operations.histology_procedures import SPIMHistologyExpBlock, SlimsWash
from aind_slims_api.models.histology import  SlimsSampleContent, SlimsReagentContent, SlimsProtocolSOP, SlimsSource
from typing import List, Optional

class SlimsHistologyMapper:
    """Mapper class for Slims histology procedures"""

    def map_specimen_procedures(self, slims_blocks: List[SPIMHistologyExpBlock], specimen_id: str):
        """Map specimen procedures from Slims histology data"""
        # TODO: Iterate through each block in exp_blocks list
        specimen_procedures = []
        for block in slims_blocks: 
            procedure_type = self._map_procedure_type(block.experiment_template.name)
            if procedure_type == SpecimenProcedureType.IMMUNOLABELING:
                procs = self.map_immunolabeling(block, specimen_id)
                specimen_procedures.extend(procs)
            else:
                specimen_procedure = self._map_specimen_procedure(block, procedure_type, specimen_id)
                specimen_procedures.append(specimen_procedure)
        return specimen_procedures

    def _map_specimen_procedure(self, block: SPIMHistologyExpBlock, procedure_type: SpecimenProcedureType, specimen_id: str) -> SpecimenProcedure:
        """Map specimen procedure from block name and procedure name"""
        # TODO: map a particular block to a specimen procedure
        spec = SpecimenProcedure.model_construct(
            specimen_id=specimen_id,
            procedure_type=procedure_type,  # method to map these
            procedure_name=getattr(block.protocol, "name", None),  # Safely access protocol name
            start_date=(
                block.washes[0].wash_step.start_time.date()
                if block.washes and block.washes[0].wash_step and block.washes[0].wash_step.start_time
                else None
            ),  # First wash start time
            end_date=(
                block.washes[-1].wash_step.end_time.date()
                if block.washes and block.washes[-1].wash_step and block.washes[-1].wash_step.end_time
                else None
            ),  # Last wash end time
            experimenter_full_name=self._map_experimenters(block.washes) if block.washes else None,  # Experimenter mapping
            protocol_id=[getattr(block.protocol, "link", None)],  # Protocol link
            reagents=self._map_reagents(block.washes) if block.washes else None,  # Reagent mapping
        )
        return spec

    def map_immunolabeling(self, block: SPIMHistologyExpBlock, specimen_id: str) -> List[SpecimenProcedure]:
        """Map immunolabeling procedure for each antibody wash"""
        procedures = []
        for wash in block.washes:
            spec = SpecimenProcedure.model_construct(
                specimen_id=specimen_id,
                procedure_type=SpecimenProcedureType.IMMUNOLABELING,
                procedure_name=getattr(block.protocol, "name", None),  # Safely access protocol name
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
                experimenter_full_name=self._map_experimenters(block.washes) if block.washes else None,  # Experimenter mapping
                protocol_id=[getattr(block.protocol, "link", None)],  # Protocol link
                antibodies=self._map_antibody(wash) if wash else None,  # Antibody mapping
            )
            procedures.append(spec)
        return procedures

    def _map_antibody(self, wash: SlimsWash) -> List[Antibody]:
        """Map antibody reagent from wash"""
        antibodies = []
        if "primary" in wash.wash_step.name.lower():
            label = ImmunolabelClass.PRIMARY
        elif "secondary" in wash.wash_step.name.lower():
            label = ImmunolabelClass.SECONDARY
        for reagent, source in wash.reagents:
            antibody = Antibody.model_construct(
                immunolabel_class=label,
                mass=wash.mass,
                name=reagent.reagent_name, 
                source=self._map_source(source.name),
                lot_number=reagent.lot_number,
            )
            antibodies.append(antibody)
        return antibodies

    def _map_reagents(self, washes: List[SlimsWash]) -> List[Reagent]:
        """Map info from washes"""
        # TODO: iterate through washes to create a list of reagents for a particular block, and map each reagent
        reagents = []
        for wash in washes:
            for reagent, source in wash.reagents:
                reagent_model = Reagent.model_construct(
                    name=reagent.reagent_name, 
                    source=self._map_source(source.name),
                    lot_number=reagent.lot_number,
                )
                reagents.append(reagent_model)
        return reagents

    def _map_source(self, source_name: str) -> Optional[Organization]:
        """Map source name to source type"""
        # TODO: check source name list in SLIMS to ensure this works
        return Organization.from_name(source_name)

    def _map_procedure_type(self, block_name: str) -> Optional[SpecimenProcedureType]:
        """Map procedure type from experiment template name"""
        # TODO: map by enum (exact values) instead of str in
        if "labeling" in block_name.lower():
            return SpecimenProcedureType.IMMUNOLABELING
        elif "delipidation" in block_name.lower():
            return SpecimenProcedureType.DELIPIDATION
        elif "refractive index matching" in block_name.lower():
            return SpecimenProcedureType.REFRACTIVE_INDEX_MATCHING
        elif "gelation" in block_name.lower():
            return SpecimenProcedureType.GELATION
        elif "expansion" in block_name.lower():
            return SpecimenProcedureType.EXPANSION
        else:
            return None
        

    def _map_experimenters(self, washes: List[SlimsWash]) -> List[str]:
        """Map unique experimenter names from washes"""
        return list({wash.wash_step.modified_by for wash in washes})



# for all "experiment blocks/templates" -> put all washes into one spec procedure (decide active/passive from protocol)
# for immunolabeling -> split each wash into sep spec procedures (should be 2, one for primary antibody and one for secondary antibody) SEPARATE THEM
# for proc name use protocol name and protocol id will be the link
