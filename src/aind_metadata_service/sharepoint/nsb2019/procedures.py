"""Maps client objects from NSB Sharepoint database to internal AIND models."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
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
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.nsb2019.models import (
    CraniotomyType as NSBCraniotomyType,
)
from aind_metadata_service.sharepoint.nsb2019.models import (  # HeadPostInfo,; Hemisphere,; InjectionType,
    NSBList2019,
)


@dataclass
class HeadFrameInfo:
    """Container for head post information"""

    headframe_type: Optional[str] = None
    headframe_part_number: Optional[str] = None
    well_type: Optional[str] = None
    well_part_number: Optional[str] = None


class MappedNSBList2019(NSBList2019):
    @staticmethod
    def _parse_datetime_to_date(dt: Optional[datetime]) -> Optional[date]:
        """Maps datetime like '2020-10-10 00:00:00' into date like
        '2020-10-10'"""
        if dt is None:
            return None
        else:
            return dt.date()

    @staticmethod
    def _parse_basic_float_str(float_str: Optional[str]) -> Optional[float]:
        try:
            return float(float_str)
        except ValueError:
            return None

    @staticmethod
    def _parse_volume_str(volume_str: Optional[str]) -> Optional[float]:
        # TODO: Parse volume_str correctly
        return None

    @staticmethod
    def _parse_current_str(current_str: Optional[str]) -> Optional[float]:
        # TODO: Parse current_str correctly
        return None

    @staticmethod
    def _parse_alt_current_str(
        alt_current_str: Optional[str],
    ) -> Optional[float]:
        # TODO: Parse alt_current_str correctly
        return None

    @staticmethod
    def _parse_ml_str(ml_str: Optional[str]) -> Optional[float]:
        # TODO: Parse ml_str correctly
        return None

    @staticmethod
    def _parse_ap_str(ap_str: Optional[str]) -> Optional[float]:
        # TODO: Parse ap_str correctly
        return None

    @staticmethod
    def _parse_dv_str(dv_str: Optional[str]) -> Optional[float]:
        # TODO: Parse dv_str correctly
        return None

    @staticmethod
    def _parse_virus_strain_str(
        virus_strain_str: Optional[str],
    ) -> Optional[float]:
        # TODO: Parse virus_strain_str correctly
        return None

    @staticmethod
    def _parse_ap_to_coord_ref(
        ap_info: Optional[str],
    ) -> Optional[CoordinateReferenceLocation]:
        # TODO: Parse ap_info correctly
        return None

    @property
    def aind_anaesthetic_type(self) -> str:
        return "isoflurane"

    @property
    def aind_craniotomy_type(self) -> Optional[CraniotomyType]:
        return {
            self.craniotomy_type.VISUAL_CORTEX_5MM: CraniotomyType.VISCTX,
            self.craniotomy_type.FRONTAL_WINDOW_3MM: CraniotomyType.THREE_MM,
            self.craniotomy_type.WHC_2_P: CraniotomyType.WHC,
            self.craniotomy_type.WHC_NP: CraniotomyType.WHC,
        }.get(self.craniotomy_type, None)

    @property
    def aind_craniotomy_size(self) -> Optional[int]:
        return {
            self.craniotomy_type.VISUAL_CORTEX_5MM: 5,
            self.craniotomy_type.FRONTAL_WINDOW_3MM: 3,
        }.get(self.craniotomy_type, None)

    @property
    def aind_inj1_angle(self) -> Optional[float]:
        return {
            self.inj1angle0.N_0_DEGREES: 0,
            self.inj1angle0.N_10_DEGREES: 10,
            self.inj1angle0.N_15_DEGREES: 15,
            self.inj1angle0.N_20_DEGREES: 20,
            self.inj1angle0.N_30_DEGREES: 30,
            self.inj1angle0.N_40_DEGREES: 40,
        }.get(self.inj1angle0, None)

    @property
    def aind_inj2_angle(self) -> Optional[float]:
        return {
            self.inj2angle0.N_0_DEGREES: 0,
            self.inj2angle0.N_10_DEGREES: 10,
            self.inj2angle0.N_15_DEGREES: 15,
            self.inj2angle0.N_20_DEGREES: 20,
            self.inj2angle0.N_30_DEGREES: 30,
            self.inj2angle0.N_40_DEGREES: 40,
        }.get(self.inj2angle0, None)

    @property
    def aind_experimenter_full_name(self) -> str:
        if self.author_id is None:
            return "NSB"
        else:
            return f"NSB-{self.author_id}"

    @property
    def aind_weight_prior(self) -> Optional[float]:
        return self._parse_basic_float_str(self.weight_before_surger)

    @property
    def aind_weight_post(self) -> Optional[float]:
        return self._parse_basic_float_str(self.weight_after_surgery)

    @property
    def aind_start_date(self) -> Optional[date]:
        return self._parse_datetime_to_date(self.date_of_surgery)

    @property
    def aind_end_date(self) -> Optional[date]:
        return self._parse_datetime_to_date(self.date_of_surgery)

    @property
    def aind_iacuc_protocol(self) -> Optional[str]:
        if self.iacuc_protocol != self.iacuc_protocol.SELECT:
            return self.iacuc_protocol.value
        else:
            return None

    @property
    def aind_headframe_info(self) -> Optional[HeadFrameInfo]:
        return {
            self.headpost_type.AI_STRAIGHT_HEADBAR: HeadFrameInfo(
                headframe_type="AI Straight Headbar"
            ),
            self.headpost_type.CAMSTYLE_HEADFRAME_016010: HeadFrameInfo(
                headframe_type="CAM-style",
                headframe_part_number="0160-100-10 Rev A",
                well_type="CAM-style",
            ),
            self.headpost_type.NEUROPIXELSTYLE_HEADFRAME: HeadFrameInfo(
                headframe_type="Neuropixel-style",
                headframe_part_number="0160-100-10",
                well_type="Neuropixel-style",
                well_part_number="0160-200-36",
            ),
            self.headpost_type.MESOSCOPESTYLE_WELL_WITH: HeadFrameInfo(
                headframe_type="NGC-style",
                headframe_part_number="0160-100-10",
                well_type="Mesoscope-style",
                well_part_number="0160-200-20",
            ),
            self.headpost_type.WHC_42_WITH_NEUROPIXEL_WE: HeadFrameInfo(
                headframe_type="WHC #42",
                headframe_part_number="42",
                well_type="Neuropixel-style",
                well_part_number="0160-200-36",
            ),
            self.headpost_type.NGCSTYLE_HEADFRAME_NO_WEL: HeadFrameInfo(
                headframe_type="NGC-style", headframe_part_number="0160-100-10"
            ),
        }.get(self.headpost_type, HeadFrameInfo())

    @property
    def aind_hp_iso_level(self) -> Optional[float]:
        return self._parse_basic_float_str(self.hp_iso_level.value)

    @property
    def aind_first_nanoject_instrument_id(self) -> Optional[str]:
        if self.nanoject_number_inj10 in [
            self.nanoject_number_inj10.SELECT,
            self.nanoject_number_inj10.NA,
        ]:
            return None
        else:
            return self.nanoject_number_inj10.value

    @property
    def aind_second_nanoject_instrument_id(self) -> Optional[str]:
        if self.nanoject_number_inj2 in [
            self.nanoject_number_inj2.SELECT,
            self.nanoject_number_inj2.NA,
        ]:
            return None
        else:
            return self.nanoject_number_inj2.value

    @property
    def aind_first_ionto_instrument_id(self) -> Optional[str]:
        if self.ionto_number_inj1 in [
            self.ionto_number_inj1.SELECT,
            self.ionto_number_inj1.NA,
        ]:
            return None
        else:
            return self.ionto_number_inj1.value

    @property
    def aind_second_ionto_instrument_id(self) -> Optional[str]:
        if self.ionto_number_inj2 in [
            self.ionto_number_inj2.SELECT,
            self.ionto_number_inj2.NA,
        ]:
            return None
        else:
            return self.ionto_number_inj2.value

    @property
    def aind_first_injection_procedure(self):
        start_date = self._parse_datetime_to_date(self.date1st_injection)
        end_date = start_date
        experimenter_full_name = self.aind_experimenter_full_name
        animal_weight_prior = self._parse_basic_float_str(
            self.first_injection_weight_be
        )
        animal_weight_post = self._parse_basic_float_str(
            self.first_injection_weight_af
        )
        recovery_time = self.first_inj_recovery
        injection_duration = self._parse_length_of_time_strings(
            self.inj1_lenghtof_time
        )
        workstation_id = self.aind_first_inj_workstation
        anaesthetic_type = self.aind_anaesthetic_type
        anaesthetic_duration = self._parse_length_of_time_strings(
            self.first_injection_iso_durat
        )
        anaesthetic_level = self._parse_basic_float_str(
            self.round1_inj_isolevel.value
        )
        injection_coordinate_ml = self._parse_ml_str(self.virus_m_l)
        injection_coordinate_ap = self._parse_ap_str(self.virus_a_p)
        injection_coordinate_depth = self._parse_dv_str(self.virus_d_v)
        injection_angle = self.aind_inj1_angle
        bregma_to_lambda_distance = self._parse_basic_float_str(
            self.breg2_lamb
        )
        injection_materials = InjectionMaterial.construct(
            full_genome_name=self._parse_virus_strain_str(
                self.inj1_virus_strain_rt
            )
        )
        injection_coordinate_reference = self._parse_ap_to_coord_ref(
            self.virus_a_p
        )
        if self.inj1_type == self.inj1_type.NANOJECT_PRESSURE:
            instrument_id = self.aind_first_nanoject_instrument_id
            injection_volume = self._parse_volume_str(self.inj1_vol)
            injection = NanojectInjection(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj1_hemisphere,
                injection_volume=injection_volume,
            )
        elif self.inj1_type == self.inj1_type.IONTOPHORESIS:
            instrument_id = self.aind_first_ionto_instrument_id
            injection_current = self._parse_current_str(self.inj1_current)
            alternating_current = self._parse_alt_current_str(
                self.inj1_alternating_time
            )
            injection = IontophoresisInjection(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj1_hemisphere,
                injection_current=injection_current,
                alternating_current=alternating_current,
            )
        else:
            injection = BrainInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj1_hemisphere,
            )
        return injection

    @property
    def aind_second_injection_procedure(self):
        start_date = self._parse_datetime_to_date(self.date2nd_injection)
        end_date = start_date
        experimenter_full_name = self.aind_experimenter_full_name
        animal_weight_prior = self._parse_basic_float_str(
            self.second_injection_weight_b
        )
        animal_weight_post = self._parse_basic_float_str(
            self.second_injection_weight_a
        )
        recovery_time = self.second_inj_recover
        injection_duration = self._parse_length_of_time_strings(
            self.inj2_lenghtof_time
        )
        workstation_id = self.aind_second_inj_workstation
        anaesthetic_type = self.aind_anaesthetic_type
        anaesthetic_duration = self._parse_length_of_time_strings(
            self.second_injection_iso_dura
        )
        anaesthetic_level = self._parse_basic_float_str(
            self.round2_inj_isolevel
        )
        injection_coordinate_ml = self._parse_ml_str(self.ml2nd_inj)
        injection_coordinate_ap = self._parse_ap_str(self.ap2nd_inj)
        injection_coordinate_depth = self._parse_dv_str(self.dv2nd_inj)
        injection_angle = self.aind_inj2_angle
        bregma_to_lambda_distance = self._parse_basic_float_str(
            self.breg2_lamb
        )
        injection_materials = InjectionMaterial.construct(
            full_genome_name=self._parse_virus_strain_str(
                self.inj2_virus_strain_rt
            )
        )
        injection_coordinate_reference = self._parse_ap_to_coord_ref(
            self.ap2nd_inj
        )
        if self.inj2_type == self.inj2_type.NANOJECT_PRESSURE:
            instrument_id = self.aind_second_nanoject_instrument_id
            injection_volume = self._parse_volume_str(self.inj2_vol)
            injection = NanojectInjection(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj2_hemisphere,
                injection_volume=injection_volume,
            )
        elif self.inj2_type == self.inj2_type.IONTOPHORESIS:
            instrument_id = self.aind_second_ionto_instrument_id
            injection_current = self._parse_current_str(self.inj2_current)
            alternating_current = self._parse_alt_current_str(
                self.inj2_alternating_time
            )
            injection = IontophoresisInjection(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj2_hemisphere,
                injection_current=injection_current,
                alternating_current=alternating_current,
            )
        else:
            injection = BrainInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=Anaesthetic.construct(
                    type=anaesthetic_type,
                    duration=anaesthetic_duration,
                    level=anaesthetic_level,
                ),
                injection_materials=injection_materials,
                recovery_time=recovery_time,
                injection_duration=injection_duration,
                workstation_id=workstation_id,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_coordinate_reference=injection_coordinate_reference,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_angle=injection_angle,
                injection_hemisphere=self.aind_inj2_hemisphere,
            )
        return injection

    @property
    def aind_date_1st_injection(self) -> Optional[date]:
        return self._parse_datetime_to_date(self.date1st_injection)

    @property
    def aind_first_inj_weight_prior(self) -> Optional[float]:
        return self._parse_basic_float_str(self.first_injection_weight_be)

    @property
    def aind_first_inj_weight_post(self) -> Optional[float]:
        return self._parse_basic_float_str(self.first_injection_weight_af)

    @staticmethod
    def _parse_length_of_time_strings(input_string: str) -> Optional[float]:
        # TODO: Parse input_string properly
        return None

    @property
    def aind_inj1_length_of_time(self) -> Optional[float]:
        # TODO: Parse this string properly
        # self.inj1_lenghtof_time
        return None

    @property
    def aind_first_inj_iso_duration(self) -> Optional[float]:
        # TODO: Parse this string properly
        # self.first_injection_iso_durat
        return None

    @property
    def aind_first_inj_iso_level(self) -> Optional[float]:
        return self._parse_basic_float_str(self.round1_inj_isolevel)

    @property
    def aind_first_inj_recovery_time(self) -> Optional[float]:
        return self._parse_basic_float_str(self.first_inj_recovery)

    @property
    def aind_first_inj_workstation(self) -> Optional[str]:
        if (
            self.work_station1st_injection
            != self.work_station1st_injection.SELECT
        ):
            return self.work_station1st_injection.value
        else:
            return None

    @property
    def aind_second_inj_workstation(self) -> Optional[str]:
        if (
            self.work_station2nd_injection
            != self.work_station2nd_injection.SELECT
        ):
            return self.work_station2nd_injection.value
        else:
            return None

    @property
    def aind_inj1_hemisphere(self) -> Optional[Side]:
        return {
            self.virus_hemisphere.LEFT: Side.LEFT,
            self.virus_hemisphere.RIGHT: Side.RIGHT,
        }.get(self.virus_hemisphere, None)

    @property
    def aind_inj2_hemisphere(self) -> Optional[Side]:
        return {
            self.hemisphere2nd_inj.LEFT: Side.LEFT,
            self.hemisphere2nd_inj.RIGHT: Side.RIGHT,
        }.get(self.hemisphere2nd_inj, None)

    @property
    def aind_inj1_ml(self) -> Optional[float]:
        # TODO: Parse this string properly
        # self.virus_m_l
        return None

    @property
    def aind_inj1_ap(self) -> Optional[float]:
        # TODO: Parse this string properly
        # self.virus_a_p
        return None

    @property
    def aind_inj1_dv(self) -> Optional[float]:
        # TODO: Parse this string properly
        # self.inj_1_dv
        return None

    @property
    def has_hp_procedure(self) -> bool:
        hp_procs = [
            self.procedure.HPINJ,
            self.procedure.HP_ONLY,
            self.procedure.HP_TRANSCRANIAL_FOR_ISI,
            self.procedure.HPC_CAM,
            self.procedure.HPC_MULTISCOPE,
            self.procedure.HPC_NEUROPIXEL_STYLE,
            self.procedure.HP_INJECTION_OPTIC_FIBER,
            self.procedure.INJHPC,
        ]
        if self.procedure in hp_procs:
            return True
        else:
            return False

    @property
    def has_first_inj_procedure(self) -> bool:
        inj_procs = [
            self.procedure.HPINJ,
            self.procedure.HP_INJECTION_OPTIC_FIBER,
            self.procedure.INJHPC,
            self.procedure.INJWHC_NP,
            self.procedure.STEREOTAXIC_INJECTION,
        ]
        if self.procedure in inj_procs:
            return True
        else:
            return False

    @property
    def has_second_inj_procedure(self) -> bool:
        if self.has_first_inj_procedure and self.inj2_round in [
            self.inj2_round.N_1ST,
            self.inj2_round.N_2ND,
        ]:
            return True
        else:
            return False

    @property
    def aind_headframe_procedures(self) -> Headframe:
        return Headframe.construct(
            start_date=self.aind_start_date,
            end_date=self.aind_end_date,
            experimenter_full_name=self.aind_experimenter_full_name,
            iacuc_protocol=self.aind_iacuc_protocol,
            animal_weight_prior=self.aind_weight_prior,
            animal_weight_post=self.aind_weight_post,
            headframe_type=self.aind_headframe_info.headframe_type,
            headframe_part_number=self.aind_headframe_info.headframe_part_number,
            well_type=self.aind_headframe_info.well_type,
            well_part_number=self.aind_headframe_info.well_part_number,
            anaesthetic=Anaesthetic.construct(
                type=self.aind_anaesthetic_type, level=self.aind_hp_iso_level
            ),
        )

    def map_to_aind_procedures(self) -> List[SubjectProcedure]:
        procedures = []
        start_date = self.aind_start_date
        end_date = self.aind_end_date
        experimenter_full_name = self.aind_experimenter_full_name
        iacuc_protocol = self.aind_iacuc_protocol
        animal_weight_prior = self.aind_weight_prior
        animal_weight_post = self.aind_weight_post

        # Check if headframe type procedure in list of procedures
        if self.has_hp_procedure:
            procedures.append(self.aind_headframe_procedures)

        # Check if injection type procedure in procedure_types
        if self.has_first_inj_procedure:
            procedures.append(self.aind_first_injection_procedure)

        # Add second injection if exists
        if self.has_second_inj_procedure:
            procedures.append(self.aind_second_injection_procedure)

        # Check if craniotomy procedure
        if nsb_model.has_cran_procedure():
            cran_kwargs = {
                "start_date": start_date,
                "end_date": end_date,
                "experimenter_full_name": experimenter_full_name,
                "iacuc_protocol": iacuc_protocol,
                "animal_weight_prior": animal_weight_prior,
                "animal_weight_post": animal_weight_post,
            }
            hp_iso_level = nsb_model.hp_iso_level
            anaesthetic_type = "isoflurane"
            anaesthetic = Anaesthetic.construct(
                type=anaesthetic_type,
                level=hp_iso_level,
            )
            cran_kwargs["anaesthesia"] = anaesthetic
            craniotomy_type = self._map_craniotomy_type(
                nsb_model.craniotomy_type
            )
            cran_kwargs["craniotomy_type"] = craniotomy_type
            cran_kwargs["craniotomy_coordinates_reference"] = (
                CoordinateReferenceLocation.LAMBDA
                if craniotomy_type == CraniotomyType.VISCTX
                else None
            )
            cran_kwargs["craniotomy_hemisphere"] = self._map_hemisphere(
                nsb_model.hp_loc
            )

            cran_kwargs["craniotomy_coordinates_ml"] = nsb_model.hp_ml
            cran_kwargs["craniotomy_coordinates_ap"] = nsb_model.hp_ap
            cran_kwargs[
                "craniotomy_size"
            ] = self._map_nsb_craniotomy_type_to_size(
                nsb_model.craniotomy_type
            )
            cran_kwargs["dura_removed"] = nsb_model.hp_durotomy
            cran_kwargs["workstation_id"] = nsb_model.hp_work_station
            cran_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
            craniotomy = Craniotomy.construct(**cran_kwargs)
            procedures.append(craniotomy)

        # Check if there is Fiber Implant Procedure
        if nsb_model.has_fiber_implant_procedure():
            ophys_probes = []
            fiber_implant1 = nsb_model.fiber_implant1
            fiber_implant2 = nsb_model.fiber_implant2
            bregma_to_lambda_distance = nsb_model.breg_2_lamb
            if fiber_implant1 is not None:
                name = ProbeName.PROBE_A.value
                stereotactic_coordinate_ml = nsb_model.virus_ml
                stereotactic_coordinate_ap = nsb_model.virus_ap
                coordinate_reference = self._map_ap_info_to_coord_reference(
                    nsb_model.virus_ap
                )
                stereotactic_coordinate_dv = nsb_model.fiber_implant1_dv
                angle = nsb_model.inj1_angle_v2
                ophys_probe1 = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=stereotactic_coordinate_ml,
                    stereotactic_coordinate_ap=stereotactic_coordinate_ap,
                    stereotactic_coordinate_dv=stereotactic_coordinate_dv,
                    angle=angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                ophys_probes.append(ophys_probe1)
            if fiber_implant2 is not None:
                name = ProbeName.PROBE_B.value
                stereotactic_coordinate_ml = nsb_model.ml_2nd_inj
                stereotactic_coordinate_ap = nsb_model.ap_2nd_inj
                coordinate_reference = self._map_ap_info_to_coord_reference(
                    nsb_model.ap_2nd_inj
                )
                stereotactic_coordinate_dv = nsb_model.fiber_implant2_dv
                angle = nsb_model.inj2_angle_v2
                ophys_probe2 = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=stereotactic_coordinate_ml,
                    stereotactic_coordinate_ap=stereotactic_coordinate_ap,
                    stereotactic_coordinate_dv=stereotactic_coordinate_dv,
                    angle=angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                ophys_probes.append(ophys_probe2)
            fiber_implant = FiberImplant.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                probes=ophys_probes,
            )
            procedures.append(fiber_implant)

        # If list of procedures is blank or unknown, create a basic procedure
        if (
            not nsb_model.has_first_inj_procedure()
            and not nsb_model.has_2nd_inj_procedure()
            and not nsb_model.has_hp_procedure()
            and not nsb_model.has_cran_procedure()
            and not nsb_model.has_fiber_implant_procedure()
        ):
            basic_kwargs = {
                "start_date": start_date,
                "end_date": end_date,
                "experimenter_full_name": experimenter_full_name,
                "iacuc_protocol": iacuc_protocol,
                "animal_weight_prior": animal_weight_prior,
                "animal_weight_post": animal_weight_post,
            }
            subject_procedure = SubjectProcedure.construct(**basic_kwargs)
            procedures.append(subject_procedure)

        return procedures


class NSB2019Mapping:
    """Provides methods to retrieve procedure information from sharepoint,
    parses the response into an intermediate data model, and maps that model
    into AIND Procedures model."""

    def get_procedures_from_sharepoint(
        self, subject_id: str, client_context: ClientContext, list_title: str
    ) -> List[SubjectProcedure]:
        """
        Get list of Procedures from NSB 2019 database.
        Parameters
        ----------
        subject_id : str
          ID of the subject to find procedure information for
        client_context : ClientContext
          NSB Sharepoint client
        list_title : str
          Title of the list where the 2019 procedure data is stored

        Returns
        -------
        List[SubjectProcedure]

        """

        labtrack_alias = NSBList2019.__fields__.get("labtracks_id").alias
        filter_string = f"{labtrack_alias} eq '{subject_id}'"
        list_view = client_context.web.lists.get_by_title(
            list_title
        ).views.get_by_title(getattr(NSBList2019, "_view_title"))
        client_context.load(list_view)
        client_context.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        client_context.load(list_items)
        client_context.execute_query()
        list_of_procedures = []
        for list_item in list_items:
            parsed_nsb_model = NSBList2019.parse_obj(list_item.to_json())
            procedures = self.map_nsb_model(parsed_nsb_model)
            list_of_procedures.extend(procedures)
        return list_of_procedures

    # flake8: noqa: C901
    # def map_nsb_model(self, nsb_model: NSBList2019) -> List[SubjectProcedure]:
    #     """Maps an individual list item model into List[SubjectProcedures]"""
    #     mapped_model = MappedNSBList2019.parse_obj(nsb_model)
    #     procedures = []
    #     start_date = mapped_model.aind_start_date
    #     end_date = mapped_model.aind_end_date
    #     experimenter_full_name = mapped_model.aind_experimenter_full_name
    #     iacuc_protocol = mapped_model.aind_iacuc_protocol
    #     animal_weight_prior = mapped_model.aind_weight_prior
    #     animal_weight_post = mapped_model.aind_weight_post
    #
    #     # Check if headframe type procedure in list of procedures
    #     if mapped_model.has_hp_procedure:
    #         hf_kwargs = {
    #             "start_date": start_date,
    #             "end_date": end_date,
    #             "experimenter_full_name": experimenter_full_name,
    #             "iacuc_protocol": iacuc_protocol,
    #             "animal_weight_prior": animal_weight_prior,
    #             "animal_weight_post": animal_weight_post,
    #             "headframe_type": mapped_model.aind_headframe_info.headframe_type,
    #             "headframe_part_number": mapped_model.aind_headframe_info.headframe_part_number,
    #             "well_type": mapped_model.aind_headframe_info.well_type,
    #             "well_part_number": mapped_model.aind_headframe_info.well_part_number,
    #         }
    #         hp_iso_level = mapped_model.aind_hp_iso_level
    #         anaesthetic_type = "isoflurane"
    #         anaesthetic = Anaesthetic.construct(
    #             type=anaesthetic_type,
    #             level=hp_iso_level,
    #         )
    #         hf_kwargs["anaesthesia"] = anaesthetic
    #         headframe_proc = Headframe.construct(**hf_kwargs)
    #         procedures.append(headframe_proc)
    #
    #     # Check if injection type procedure in procedure_types
    #     if mapped_model.has_first_inj_procedure:
    #         # Map first injection procedure
    #         inj1_kwargs = {}
    #         inj1_start_date = mapped_model.aind_date_1st_injection
    #         inj1_kwargs["start_date"] = inj1_start_date
    #         inj1_kwargs["end_date"] = inj1_start_date
    #         inj1_kwargs[
    #             "animal_weight_prior"
    #         ] = mapped_model.aind_first_inj_weight_prior
    #         inj1_kwargs[
    #             "animal_weight_post"
    #         ] = mapped_model.aind_first_inj_weight_post
    #         inj1_kwargs["injection_duration"] = mapped_model.aind_inj1_length_of_time
    #         # First injection anaesthetic
    #         inj1_anaesthetic_type = "isoflurane"
    #         inj1_anaesthetic_duration = mapped_model.aind_first_inj_iso_duration
    #         inj1_anaesthetic_level = mapped_model.aind_first_inj_iso_level
    #         inj1_kwargs["anaesthesia"] = Anaesthetic.construct(
    #             type=inj1_anaesthetic_type,
    #             duration=inj1_anaesthetic_duration,
    #             level=inj1_anaesthetic_level,
    #         )
    #         inj1_kwargs["recovery_time"] = mapped_model.n_1st_inj_recovery
    #         inj1_kwargs["workstation_id"] = mapped_model.aind_first_inj_workstation
    #         inj1_kwargs["injection_hemisphere"] = mapped_model.aind_inj1_hemisphere
    #         inj1_kwargs["injection_coordinate_ml"] = mapped_model.inj_1_ml
    #         inj1_kwargs["injection_coordinate_ap"] = mapped_model.inj_1_ap
    #         inj1_kwargs[
    #             "injection_coordinate_reference"
    #         ] = self._map_ap_info_to_coord_reference(nsb_model.virus_ap)
    #         inj1_kwargs["injection_coordinate_depth"] = nsb_model.virus_dv
    #         inj1_kwargs["injection_angle"] = nsb_model.inj1_angle0
    #         inj1_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
    #         # inj1_virus_strain = nsb_model.inj1_virus_strain_rt
    #         inj1_kwargs[
    #             "injection_materials"
    #         ] = self._map_virus_strain_to_materials(
    #             nsb_model.inj1_virus_strain_rt
    #         )
    #         if nsb_model.inj1_type == InjectionType.IONTOPHORESIS:
    #             inj1_kwargs["instrument_id"] = nsb_model.ionto_number_inj1
    #             inj1_kwargs["injection_current"] = nsb_model.inj1_current
    #             inj1_kwargs[
    #                 "alternating_current"
    #             ] = nsb_model.inj1_alternating_time
    #             injection1 = IontophoresisInjection.construct(**inj1_kwargs)
    #         elif nsb_model.inj1_type == InjectionType.NANOJECT:
    #             inj1_kwargs["instrument_id"] = nsb_model.nanoject_number_inj10
    #             inj1_kwargs["injection_volume"] = nsb_model.inj1_vol
    #             injection1 = NanojectInjection.construct(**inj1_kwargs)
    #         else:
    #             injection1 = BrainInjection.construct(**inj1_kwargs)
    #         procedures.append(injection1)
    #
    #     # Add second injection if exists
    #     if nsb_model.has_2nd_inj_procedure():
    #         inj2_kwargs = {}
    #         inj2_start_date = self._map_datetime_to_date(
    #             nsb_model.date_2nd_injection
    #         )
    #         inj2_kwargs["start_date"] = inj2_start_date
    #         inj2_kwargs["end_date"] = inj2_start_date
    #         inj2_kwargs[
    #             "animal_weight_prior"
    #         ] = nsb_model.second_injection_weight_before
    #         inj2_kwargs[
    #             "animal_weight_post"
    #         ] = nsb_model.second_injection_weight_after
    #         inj2_kwargs["injection_duration"] = self._duration_to_minutes(
    #             nsb_model.inj2_length_of_time
    #         )
    #         # First injection anaesthetic
    #         inj2_anaesthetic_type = "isoflurane"
    #         inj2_anaesthetic_duration = nsb_model.second_injection_iso_duration
    #         inj2_anaesthetic_level = nsb_model.round2_inj_iso_level
    #         inj2_kwargs["anaesthesia"] = Anaesthetic.construct(
    #             type=inj2_anaesthetic_type,
    #             duration=inj2_anaesthetic_duration,
    #             level=inj2_anaesthetic_level,
    #         )
    #         inj2_kwargs["recovery_time"] = nsb_model.second_inj_recovery
    #         inj2_kwargs["workstation_id"] = nsb_model.workstation_2nd_injection
    #         inj2_kwargs["injection_hemisphere"] = self._map_hemisphere(
    #             nsb_model.hemisphere_2nd_inj
    #         )
    #         inj2_kwargs["injection_coordinate_ml"] = nsb_model.ml_2nd_inj
    #         inj2_kwargs["injection_coordinate_ap"] = nsb_model.ap_2nd_inj
    #         inj2_kwargs[
    #             "injection_coordinate_reference"
    #         ] = self._map_ap_info_to_coord_reference(nsb_model.ap_2nd_inj)
    #         inj2_kwargs["injection_coordinate_depth"] = nsb_model.dv_2nd_inj
    #         inj2_kwargs["injection_angle"] = nsb_model.inj2_angle0
    #         # Is this the same for 1st and 2nd injections?
    #         inj2_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
    #         # inj2_virus_strain = nsb_model.inj2_virus_strain_rt
    #         inj2_kwargs[
    #             "injection_materials"
    #         ] = self._map_virus_strain_to_materials(
    #             nsb_model.inj2_virus_strain_rt
    #         )
    #         if nsb_model.inj2_type == InjectionType.IONTOPHORESIS:
    #             inj2_kwargs["instrument_id"] = nsb_model.ionto_number_inj2
    #             inj2_kwargs["injection_current"] = nsb_model.inj2_current
    #             inj2_kwargs[
    #                 "alternating_current"
    #             ] = nsb_model.inj2_alternating_time
    #             injection2 = IontophoresisInjection.construct(**inj2_kwargs)
    #         elif nsb_model.inj2_type == InjectionType.NANOJECT:
    #             inj2_kwargs["instrument_id"] = nsb_model.nanoject_number_inj2
    #             inj2_kwargs["injection_volume"] = nsb_model.inj2_vol
    #             injection2 = NanojectInjection.construct(**inj2_kwargs)
    #         else:
    #             injection2 = BrainInjection.construct(**inj2_kwargs)
    #         procedures.append(injection2)
    #
    #     # Check if craniotomy procedure
    #     if nsb_model.has_cran_procedure():
    #         cran_kwargs = {
    #             "start_date": start_date,
    #             "end_date": end_date,
    #             "experimenter_full_name": experimenter_full_name,
    #             "iacuc_protocol": iacuc_protocol,
    #             "animal_weight_prior": animal_weight_prior,
    #             "animal_weight_post": animal_weight_post,
    #         }
    #         hp_iso_level = nsb_model.hp_iso_level
    #         anaesthetic_type = "isoflurane"
    #         anaesthetic = Anaesthetic.construct(
    #             type=anaesthetic_type,
    #             level=hp_iso_level,
    #         )
    #         cran_kwargs["anaesthesia"] = anaesthetic
    #         craniotomy_type = self._map_craniotomy_type(
    #             nsb_model.craniotomy_type
    #         )
    #         cran_kwargs["craniotomy_type"] = craniotomy_type
    #         cran_kwargs["craniotomy_coordinates_reference"] = (
    #             CoordinateReferenceLocation.LAMBDA
    #             if craniotomy_type == CraniotomyType.VISCTX
    #             else None
    #         )
    #         cran_kwargs["craniotomy_hemisphere"] = self._map_hemisphere(
    #             nsb_model.hp_loc
    #         )
    #
    #         cran_kwargs["craniotomy_coordinates_ml"] = nsb_model.hp_ml
    #         cran_kwargs["craniotomy_coordinates_ap"] = nsb_model.hp_ap
    #         cran_kwargs[
    #             "craniotomy_size"
    #         ] = self._map_nsb_craniotomy_type_to_size(
    #             nsb_model.craniotomy_type
    #         )
    #         cran_kwargs["dura_removed"] = nsb_model.hp_durotomy
    #         cran_kwargs["workstation_id"] = nsb_model.hp_work_station
    #         cran_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
    #         craniotomy = Craniotomy.construct(**cran_kwargs)
    #         procedures.append(craniotomy)
    #
    #     # Check if there is Fiber Implant Procedure
    #     if nsb_model.has_fiber_implant_procedure():
    #         ophys_probes = []
    #         fiber_implant1 = nsb_model.fiber_implant1
    #         fiber_implant2 = nsb_model.fiber_implant2
    #         bregma_to_lambda_distance = nsb_model.breg_2_lamb
    #         if fiber_implant1 is not None:
    #             name = ProbeName.PROBE_A.value
    #             stereotactic_coordinate_ml = nsb_model.virus_ml
    #             stereotactic_coordinate_ap = nsb_model.virus_ap
    #             coordinate_reference = self._map_ap_info_to_coord_reference(
    #                 nsb_model.virus_ap
    #             )
    #             stereotactic_coordinate_dv = nsb_model.fiber_implant1_dv
    #             angle = nsb_model.inj1_angle_v2
    #             ophys_probe1 = OphysProbe.construct(
    #                 name=name,
    #                 stereotactic_coordinate_ml=stereotactic_coordinate_ml,
    #                 stereotactic_coordinate_ap=stereotactic_coordinate_ap,
    #                 stereotactic_coordinate_dv=stereotactic_coordinate_dv,
    #                 angle=angle,
    #                 bregma_to_lambda_distance=bregma_to_lambda_distance,
    #                 stereotactic_coordinate_reference=coordinate_reference,
    #             )
    #             ophys_probes.append(ophys_probe1)
    #         if fiber_implant2 is not None:
    #             name = ProbeName.PROBE_B.value
    #             stereotactic_coordinate_ml = nsb_model.ml_2nd_inj
    #             stereotactic_coordinate_ap = nsb_model.ap_2nd_inj
    #             coordinate_reference = self._map_ap_info_to_coord_reference(
    #                 nsb_model.ap_2nd_inj
    #             )
    #             stereotactic_coordinate_dv = nsb_model.fiber_implant2_dv
    #             angle = nsb_model.inj2_angle_v2
    #             ophys_probe2 = OphysProbe.construct(
    #                 name=name,
    #                 stereotactic_coordinate_ml=stereotactic_coordinate_ml,
    #                 stereotactic_coordinate_ap=stereotactic_coordinate_ap,
    #                 stereotactic_coordinate_dv=stereotactic_coordinate_dv,
    #                 angle=angle,
    #                 bregma_to_lambda_distance=bregma_to_lambda_distance,
    #                 stereotactic_coordinate_reference=coordinate_reference,
    #             )
    #             ophys_probes.append(ophys_probe2)
    #         fiber_implant = FiberImplant.construct(
    #             start_date=start_date,
    #             end_date=end_date,
    #             experimenter_full_name=experimenter_full_name,
    #             iacuc_protocol=iacuc_protocol,
    #             animal_weight_prior=animal_weight_prior,
    #             animal_weight_post=animal_weight_post,
    #             probes=ophys_probes,
    #         )
    #         procedures.append(fiber_implant)
    #
    #     # If list of procedures is blank or unknown, create a basic procedure
    #     if (
    #         not nsb_model.has_inj_procedure()
    #         and not nsb_model.has_2nd_inj_procedure()
    #         and not nsb_model.has_hp_procedure()
    #         and not nsb_model.has_cran_procedure()
    #         and not nsb_model.has_fiber_implant_procedure()
    #     ):
    #         basic_kwargs = {
    #             "start_date": start_date,
    #             "end_date": end_date,
    #             "experimenter_full_name": experimenter_full_name,
    #             "iacuc_protocol": iacuc_protocol,
    #             "animal_weight_prior": animal_weight_prior,
    #             "animal_weight_post": animal_weight_post,
    #         }
    #         subject_procedure = SubjectProcedure.construct(**basic_kwargs)
    #         procedures.append(subject_procedure)
    #
    #     return procedures
    #
    # @staticmethod
    # def _map_auth_id_to_exp_name(
    #     nsb_author_id: Optional[str],
    # ) -> Optional[str]:
    #     """Maps NSB Author ID to Experimenter name as "NSB" + ID"""
    #     return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"
    #
    # @staticmethod
    # def _map_hemisphere(
    #     nsb_hemisphere: Optional[Hemisphere],
    # ) -> Optional[Side]:
    #     """Maps NSB Hemisphere to AIND Side"""
    #     if nsb_hemisphere == Hemisphere.LEFT:
    #         return Side.LEFT
    #     elif nsb_hemisphere == Hemisphere.RIGHT:
    #         return Side.RIGHT
    #     else:
    #         return None
    #
    # @staticmethod
    # def _map_craniotomy_type(
    #     nsb_craniotomy: Optional[NSBCraniotomyType],
    # ) -> Optional[CraniotomyType]:
    #     """Maps NSB CraniotomyType into AIND CraniotomyType"""
    #     if nsb_craniotomy == NSBCraniotomyType.VISUAL_CORTEX:
    #         return CraniotomyType.VISCTX
    #     elif nsb_craniotomy == NSBCraniotomyType.FRONTAL_WINDOW:
    #         return CraniotomyType.THREE_MM
    #     elif (
    #         nsb_craniotomy == NSBCraniotomyType.WHC_NP
    #         or nsb_craniotomy == NSBCraniotomyType.WHC_2P
    #     ):
    #         return CraniotomyType.WHC
    #     else:
    #         return CraniotomyType.OTHER
    #
    # @staticmethod
    # def _map_nsb_craniotomy_type_to_size(
    #     cran_type: NSBCraniotomyType,
    # ) -> Optional[float]:
    #     """Maps NSB CraniotomyType into size"""
    #     if cran_type == NSBCraniotomyType.VISUAL_CORTEX:
    #         return 5.0
    #     elif cran_type == NSBCraniotomyType.FRONTAL_WINDOW:
    #         return 3.0
    #     else:
    #         return None
    #
    # @staticmethod
    # def _map_ap_info_to_coord_reference(
    #     _: None,
    # ) -> Optional[CoordinateReferenceLocation]:
    #     """Maps NSB virus ap into AIND CoordinateReferenceLocation"""
    #     return None
    #
    # @staticmethod
    # def _map_virus_strain_to_materials(
    #     virus_strain: Optional[str],
    # ) -> Optional[InjectionMaterial]:
    #     """Maps NASB virus strain into AIND InjectionMaterials"""
    #     if virus_strain is None:
    #         return None
    #     else:
    #         return InjectionMaterial.construct(full_genome_name=virus_strain)
    #
    # @staticmethod
    # def _map_datetime_to_date(dt: datetime) -> Optional[date]:
    #     """Maps datetime like '2020-10-10 00:00:00' into date like
    #     '2020-10-10'"""
    #     if dt is None:
    #         return None
    #     else:
    #         return dt.date()
    #
    # @staticmethod
    # def _duration_to_minutes(duration: Optional[timedelta]) -> Optional[float]:
    #     """Converts Optional[timedelta] into an Optional[float]"""
    #     return None if duration is None else duration.total_seconds() / 60
