from datetime import date, datetime
from typing import List, Optional

from aind_data_schema.procedures import (
    Anaesthetic,
    BrainInjection,
    CoordinateReferenceLocation,
    Craniotomy,
    CraniotomyType,
    FiberImplant,
    Headframe,
    InjectionMaterial,
    IontophoresisInjection,
    NanojectInjection,
    OphysProbe,
    ProbeName,
    Side,
    SubjectProcedure,
)
from aind_metadata_service.sharepoint.nsb2019.mapping import NSB2019Mapping
from aind_metadata_service.sharepoint.nsb2023.models import (
    NSBList2023,
    BurrHoleProcedure,
    During,
    HeadPostInfo2023,
    CraniotomyType as NSBCraniotomyType,
)


class NSB2023Mapping(NSB2019Mapping):
    def map_nsb_model(self, nsb_model: NSBList2023) -> List[SubjectProcedure]:
        procedures = []
        start_date = self._map_datetime_to_date(nsb_model.date_of_surgery)
        end_date = start_date
        experimenter_full_name = self._map_auth_id_to_exp_name(
            nsb_model.author_id
        )
        iacuc_protocol = nsb_model.iacuc_protocol
        animal_weight_prior = nsb_model.weight_before_surgery
        animal_weight_post = nsb_model.weight_after_surgery

        # Check if any headframe procedures
        if nsb_model.has_hp_procedure():
            hp_during = nsb_model.headpost_perform_during
            if hp_during == During.FOLLOW_UP_SURGERY:
                anaesthetic_duration = (
                    nsb_model.first_injection_iso_duration.total_seconds() / 60
                )
                anaesthetic_level = nsb_model.round1_inj_iso_level
                headframe_start_date = self._map_datetime_to_date(
                    nsb_model.date_1st_injection
                )
                headframe_weight_prior = (
                    nsb_model.first_injection_weight_before
                )
                headframe_weight_post = nsb_model.first_injection_weight_after
            else:
                anaesthetic_duration = nsb_model.iso_on.total_seconds() / 60
                anaesthetic_level = nsb_model.hp_iso_level
                headframe_start_date = start_date
                headframe_weight_prior = animal_weight_prior
                headframe_weight_post = animal_weight_post
            anaesthetic = Anaesthetic.construct(
                type="isoflurane",
                duration=anaesthetic_duration,
                level=anaesthetic_level,
            )
            headpost_info = HeadPostInfo2023.from_hp_and_hp_type(
                hp=nsb_model.headpost, hp_type=nsb_model.headpost_type
            )

            headframe_procedure = Headframe.construct(
                start_date=headframe_start_date,
                end_date=headframe_start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=headframe_weight_prior,
                animal_weight_post=headframe_weight_post,
                headframe_type=headpost_info.headframe_type,
                headframe_part_number=headpost_info.headframe_part_number,
                well_type=headpost_info.well_type,
                well_part_number=headpost_info.well_part_number,
                anaesthesia=anaesthetic,
            )
            procedures.append(headframe_procedure)

        # Check for craniotomy procedures
        if nsb_model.has_cran_procedure():
            craniotomy_type = self._map_craniotomy_type(
                nsb_model.craniotomy_type
            )
            cran_during = nsb_model.craniotomy_perform_during
            if cran_during == During.FOLLOW_UP_SURGERY:
                anaesthetic_duration = (
                    nsb_model.first_injection_iso_duration.total_seconds() / 60
                )
                anaesthetic_level = nsb_model.round1_inj_iso_level
                cran_start_date = self._map_datetime_to_date(
                    nsb_model.date_1st_injection
                )
                cran_workstation_id = nsb_model.work_station_1st_injection
                cran_recovery_time = nsb_model.first_inj_recovery
                cran_weight_prior = nsb_model.first_injection_weight_before
                cran_weight_post = nsb_model.first_injection_weight_after
            else:
                anaesthetic_duration = nsb_model.iso_on.total_seconds() / 60
                anaesthetic_level = nsb_model.hp_iso_level
                cran_start_date = start_date
                cran_workstation_id = nsb_model.work_station_1st_injection
                cran_recovery_time = nsb_model.hp_recovery
                cran_weight_prior = animal_weight_prior
                cran_weight_post = animal_weight_post
            anaesthetic = Anaesthetic.construct(
                type="isoflurane",
                duration=anaesthetic_duration,
                level=anaesthetic_level,
            )
            bregma_to_lambda_distance = nsb_model.breg_2_lamb
            if craniotomy_type == CraniotomyType.FIVE_MM:
                craniotomy_coordinates_reference = (
                    CoordinateReferenceLocation.LAMBDA
                )
                craniotomy_size = 5
            elif craniotomy_type == CraniotomyType.THREE_MM:
                craniotomy_coordinates_reference = None
                craniotomy_size = 3
            else:
                craniotomy_coordinates_reference = None
                craniotomy_size = None

            cran_procedure = Craniotomy.construct(
                start_date=cran_start_date,
                end_date=cran_start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=cran_weight_prior,
                animal_weight_post=cran_weight_post,
                craniotomy_type=craniotomy_type,
                craniotomy_size=craniotomy_size,
                anaesthesia=anaesthetic,
                workstation_id=cran_workstation_id,
                recovery_time=cran_recovery_time,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                craniotomy_coordinates_reference=(
                    craniotomy_coordinates_reference
                ),
            )
            procedures.append(cran_procedure)

        # Check if there are any procedures for burr holes 1 through 4
        for burr_hole_num in range(1, 5):
            if nsb_model.has_burr_hole_procedure(
                burr_hole_num=burr_hole_num,
                burr_hole_procedure=BurrHoleProcedure.INJECTION,
            ):
                injection_procedure = self._map_burr_hole_injection_procedure(
                    nsb_model
                )
            if nsb_model.has_burr_hole_procedure(
                burr_hole_num=burr_hole_num,
                burr_hole_procedure=BurrHoleProcedure.FIBER_IMPLANT,
            ):
                fiber_implant_procedure = (
                    self._map_burr_hole_fiber_implant_procedure(nsb_model)
                )

        return []

    @staticmethod
    def _map_craniotomy_type(
        nsb_craniotomy: Optional[NSBCraniotomyType],
    ) -> Optional[CraniotomyType]:
        if nsb_craniotomy == NSBCraniotomyType.FIVE_MM:
            return CraniotomyType.FIVE_MM
        elif nsb_craniotomy == NSBCraniotomyType.THREE_MM:
            return CraniotomyType.THREE_MM
        elif nsb_craniotomy == NSBCraniotomyType.WHC:
            return CraniotomyType.WHC
        else:
            return CraniotomyType.OTHER

    def _map_burr_hole_injection_procedure(self, nsb_model):
        pass

    def _map_burr_hole_fiber_implant_procedure(self, nsb_model):
        pass
