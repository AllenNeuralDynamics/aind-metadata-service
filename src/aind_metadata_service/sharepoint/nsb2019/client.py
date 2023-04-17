from typing import List, Optional

from aind_data_schema.procedures import (
    Anaesthetic,
    BrainInjection,
    CoordinateReferenceLocation,
    Craniotomy,
    CraniotomyType,
    Headframe,
    InjectionMaterial,
    IontophoresisInjection,
    NanojectInjection,
    Side,
    SubjectProcedure,
)
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.nsb2019.models import (
    CraniotomyType as NSBCraniotomyType,
)
from aind_metadata_service.sharepoint.nsb2019.models import (
    HeadPostInfo,
    HemisphereType,
    InjectionType,
    NSBList2019,
    NumberWithNotes,
)


class ListClient:
    def __init__(
        self, client_context: ClientContext, subject_id: str, list_title: str
    ):
        self.subject_id = subject_id
        self.client_context = client_context
        self.list_title = list_title

    def get_list_of_procedures(self) -> List[SubjectProcedure]:
        filter_string = (
            f"substringof('{self.subject_id}', "
            f"{NSBList2019.__fields__.get('labtracks_id').alias})"
        )
        list_view = self.client_context.web.lists.get_by_title(
            self.list_title
        ).views.get_by_title(getattr(NSBList2019, "_view_title"))
        self.client_context.load(list_view)
        self.client_context.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        self.client_context.load(list_items)
        self.client_context.execute_query()
        list_of_procedures = []
        for list_item in list_items:
            parsed_nsb_model = NSBList2019.parse_obj(list_item.to_json())
            procedures = self._map_nsb_model(parsed_nsb_model)
            list_of_procedures.extend(procedures)
        return list_of_procedures

    def _map_nsb_model(self, nsb_model: NSBList2019) -> List[SubjectProcedure]:
        procedures = []
        start_date = nsb_model.date_of_surgery
        end_date = start_date
        experimenter_full_name = self._map_auth_id_to_exp_name(
            nsb_model.author_id
        )
        iacuc_protocol = nsb_model.iacuc_protocol
        animal_weight_prior = nsb_model.weight_before_surgery
        animal_weight_post = nsb_model.weight_after_surgery

        # Check if headframe type procedure in list of procedures
        if nsb_model.has_hp_procedure():
            hf_kwargs = {
                "start_date": start_date,
                "end_date": end_date,
                "experimenter_full_name": experimenter_full_name,
                "iacuc_protocol": iacuc_protocol,
                "animal_weight_prior": animal_weight_prior,
                "animal_weight_post": animal_weight_post,
            }
            headpost_type = nsb_model.headpost_type
            headpost_info = HeadPostInfo.from_headpost_type(
                headpost_type=headpost_type
            )
            hf_kwargs["headframe_type"] = headpost_info.headframe_type
            hf_kwargs[
                "headframe_part_number"
            ] = headpost_info.headframe_part_number
            hf_kwargs["well_type"] = headpost_info.well_type
            hf_kwargs["well_part_number"] = headpost_info.well_part_number
            hp_iso_level = nsb_model.hp_iso_level
            anaesthetic_type = "isoflurane"
            anaesthetic = Anaesthetic.construct(
                type=anaesthetic_type,
                level=hp_iso_level,
            )
            hf_kwargs["anaesthesia"] = anaesthetic
            headframe_proc = Headframe.construct(**hf_kwargs)
            procedures.append(headframe_proc)

        # Check if injection type procedure in procedure_types
        if nsb_model.has_inj_procedure():
            # Map first injection procedure
            inj1_kwargs = {}
            inj1_start_date = nsb_model.date_1st_injection
            inj1_kwargs["start_date"] = inj1_start_date
            inj1_kwargs["end_date"] = inj1_start_date
            inj1_kwargs[
                "animal_weight_prior"
            ] = nsb_model.first_injection_weight_before
            inj1_kwargs[
                "animal_weight_post"
            ] = nsb_model.first_injection_weight_after
            inj1_kwargs["injection_duration"] = nsb_model.inj1_length_of_time
            # First injection anaesthetic
            inj1_anaesthetic_type = "isoflurane"
            inj1_anaesthetic_duration = nsb_model.first_injection_iso_duration
            inj1_anaesthetic_level = nsb_model.round1_inj_iso_level
            inj1_kwargs["anaesthesia"] = Anaesthetic.construct(
                type=inj1_anaesthetic_type,
                duration=inj1_anaesthetic_duration,
                level=inj1_anaesthetic_level,
            )
            inj1_kwargs["recovery_time"] = nsb_model.first_inj_recovery
            inj1_kwargs["workstation_id"] = nsb_model.workstation_1st_injection
            inj1_kwargs["injection_hemisphere"] = self._map_hemisphere(
                nsb_model.virus_hemisphere
            )
            inj1_kwargs["injection_coordinate_ml"] = nsb_model.virus_ml.number
            inj1_kwargs["injection_coordinate_ap"] = nsb_model.virus_ap.number
            inj1_kwargs[
                "injection_coordinate_reference"
            ] = self._map_ap_info_to_coord_reference(nsb_model.virus_ap)
            inj1_kwargs[
                "injection_coordinate_depth"
            ] = nsb_model.virus_dv.number
            inj1_kwargs["injection_angle"] = nsb_model.inj1_angle0
            inj1_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
            # inj1_virus_strain = nsb_model.inj1_virus_strain_rt
            inj1_kwargs[
                "injection_materials"
            ] = self._map_virus_strain_to_materials(
                nsb_model.inj1_virus_strain_rt
            )
            if nsb_model.inj1_type == InjectionType.IONTOPHORESIS:
                inj1_kwargs["instrument_id"] = nsb_model.ionto_number_inj1
                inj1_kwargs["injection_current"] = nsb_model.inj1_current
                inj1_kwargs[
                    "alternating_current"
                ] = nsb_model.inj1_alternating_time
                injection1 = IontophoresisInjection.construct(**inj1_kwargs)
            elif nsb_model.inj1_type == InjectionType.NANOJECT:
                inj1_kwargs["instrument_id"] = nsb_model.nanoject_number_inj10
                inj1_kwargs["injection_volume"] = nsb_model.inj1_vol
                injection1 = NanojectInjection.construct(**inj1_kwargs)
            else:
                injection1 = BrainInjection.construct(**inj1_kwargs)
            procedures.append(injection1)

        # Add second injection if exists
        if nsb_model.has_2nd_inj_procedure():
            inj2_kwargs = {}
            inj2_start_date = nsb_model.date_2nd_injection
            inj2_kwargs["start_date"] = inj2_start_date
            inj2_kwargs["end_date"] = inj2_start_date
            inj2_kwargs[
                "animal_weight_prior"
            ] = nsb_model.second_injection_weight_before
            inj2_kwargs[
                "animal_weight_post"
            ] = nsb_model.second_injection_weight_after
            inj2_kwargs["injection_duration"] = nsb_model.inj2_length_of_time
            # First injection anaesthetic
            inj2_anaesthetic_type = "isoflurane"
            inj2_anaesthetic_duration = nsb_model.second_injection_iso_duration
            inj2_anaesthetic_level = nsb_model.round2_inj_iso_level
            inj2_kwargs["anaesthesia"] = Anaesthetic.construct(
                type=inj2_anaesthetic_type,
                duration=inj2_anaesthetic_duration,
                level=inj2_anaesthetic_level,
            )
            inj2_kwargs["recovery_time"] = nsb_model.second_inj_recovery
            inj2_kwargs["workstation_id"] = nsb_model.workstation_2nd_injection
            inj2_kwargs["injection_hemisphere"] = self._map_hemisphere(
                nsb_model.hemisphere_2nd_inj
            )
            inj2_kwargs[
                "injection_coordinate_ml"
            ] = nsb_model.ml_2nd_inj.number
            inj2_kwargs[
                "injection_coordinate_ap"
            ] = nsb_model.ap_2nd_inj.number
            inj2_kwargs[
                "injection_coordinate_reference"
            ] = self._map_ap_info_to_coord_reference(nsb_model.ap_2nd_inj)
            inj2_kwargs[
                "injection_coordinate_depth"
            ] = nsb_model.dv_2nd_inj.number
            inj2_kwargs["injection_angle"] = nsb_model.inj2_angle0
            # Is this the same for 1st and 2nd injections?
            inj2_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
            # inj2_virus_strain = nsb_model.inj2_virus_strain_rt
            inj2_kwargs[
                "injection_materials"
            ] = self._map_virus_strain_to_materials(
                nsb_model.inj2_virus_strain_rt
            )
            if nsb_model.inj2_type == InjectionType.IONTOPHORESIS:
                inj2_kwargs["instrument_id"] = nsb_model.ionto_number_inj2
                inj2_kwargs["injection_current"] = nsb_model.inj2_current
                inj2_kwargs[
                    "alternating_current"
                ] = nsb_model.inj2_alternating_time
                injection2 = IontophoresisInjection.construct(**inj2_kwargs)
            elif nsb_model.inj2_type == InjectionType.NANOJECT:
                inj2_kwargs["instrument_id"] = nsb_model.nanoject_number_inj2
                inj2_kwargs["injection_volume"] = nsb_model.inj2_vol
                injection2 = NanojectInjection.construct(**inj2_kwargs)
            else:
                injection2 = BrainInjection.construct(**inj2_kwargs)
            procedures.append(injection2)

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
            ] = nsb_model.implant_id_coverslip_type.number
            cran_kwargs["dura_removed"] = nsb_model.hp_durotomy
            cran_kwargs["workstation_id"] = nsb_model.hp_work_station
            cran_kwargs["bregma_to_lambda_distance"] = nsb_model.breg_2_lamb
            craniotomy = Craniotomy.construct(**cran_kwargs)
            procedures.append(craniotomy)

        # If list of procedures is blank or unknown, create a basic procedure
        if (
            not nsb_model.has_inj_procedure()
            and not nsb_model.has_2nd_inj_procedure()
            and not nsb_model.has_hp_procedure()
            and not nsb_model.has_cran_procedure()
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

    @staticmethod
    def _map_auth_id_to_exp_name(
        nsb_author_id: Optional[str],
    ) -> Optional[str]:
        """Maps NSB Author ID to Experimenter name as "NSB" + ID"""
        return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"

    @staticmethod
    def _map_hemisphere(
        nsb_hemisphere: Optional[HemisphereType],
    ) -> Optional[Side]:
        if nsb_hemisphere is None:
            return None
        elif nsb_hemisphere == nsb_hemisphere.LEFT:
            return Side.LEFT
        elif nsb_hemisphere == nsb_hemisphere.RIGHT:
            return Side.RIGHT
        else:
            return None

    @staticmethod
    def _map_craniotomy_type(
        nsb_craniotomy: Optional[NSBCraniotomyType],
    ) -> Optional[CraniotomyType]:
        if nsb_craniotomy is None:
            return None
        elif nsb_craniotomy == nsb_craniotomy.VISUAL_CORTEX:
            return CraniotomyType.VISCTX
        elif nsb_craniotomy == nsb_craniotomy.FRONTAL_WINDOW:
            return CraniotomyType.THREE_MM
        elif (
            nsb_craniotomy == nsb_craniotomy.WHC_NP
            or nsb_craniotomy == nsb_craniotomy.WHC_2P
        ):
            return CraniotomyType.WHC
        else:
            return CraniotomyType.OTHER

    @staticmethod
    def _map_ap_info_to_coord_reference(
        nsb_virus_ap: Optional[NumberWithNotes],
    ) -> Optional[CoordinateReferenceLocation]:
        if nsb_virus_ap.notes is None:
            return None
        elif "lambda" in nsb_virus_ap.notes:
            return CoordinateReferenceLocation.LAMBDA
        else:
            return CoordinateReferenceLocation.BREGMA

    @staticmethod
    def _map_virus_strain_to_materials(
        virus_strain: Optional[str],
    ) -> Optional[InjectionMaterial]:
        if virus_strain is None:
            return None
        else:
            return InjectionMaterial.construct(full_genome_name=virus_strain)
