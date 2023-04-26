"""Maps client objects from NSB Sharepoint database to internal AIND models."""

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
from aind_metadata_service.sharepoint.nsb2019.models import (
    HeadPostInfo,
    Hemisphere,
    InjectionType,
    NSBList2019,
)


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
    def map_nsb_model(self, nsb_model: NSBList2019) -> List[SubjectProcedure]:
        """Maps an individual list item model into List[SubjectProcedures]"""
        procedures = []
        start_date = self._map_datetime_to_date(nsb_model.date_of_surgery)
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
            inj1_start_date = self._map_datetime_to_date(
                nsb_model.date_1st_injection
            )
            inj1_kwargs["start_date"] = inj1_start_date
            inj1_kwargs["end_date"] = inj1_start_date
            inj1_kwargs[
                "animal_weight_prior"
            ] = nsb_model.first_injection_weight_before
            inj1_kwargs[
                "animal_weight_post"
            ] = nsb_model.first_injection_weight_after
            inj1_kwargs["injection_duration"] = self._duration_to_minutes(
                nsb_model.inj1_length_of_time
            )
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
            inj1_kwargs["injection_coordinate_ml"] = nsb_model.virus_ml
            inj1_kwargs["injection_coordinate_ap"] = nsb_model.virus_ap
            inj1_kwargs[
                "injection_coordinate_reference"
            ] = self._map_ap_info_to_coord_reference(nsb_model.virus_ap)
            inj1_kwargs["injection_coordinate_depth"] = nsb_model.virus_dv
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
            inj2_start_date = self._map_datetime_to_date(
                nsb_model.date_2nd_injection
            )
            inj2_kwargs["start_date"] = inj2_start_date
            inj2_kwargs["end_date"] = inj2_start_date
            inj2_kwargs[
                "animal_weight_prior"
            ] = nsb_model.second_injection_weight_before
            inj2_kwargs[
                "animal_weight_post"
            ] = nsb_model.second_injection_weight_after
            inj2_kwargs["injection_duration"] = self._duration_to_minutes(
                nsb_model.inj2_length_of_time
            )
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
            inj2_kwargs["injection_coordinate_ml"] = nsb_model.ml_2nd_inj
            inj2_kwargs["injection_coordinate_ap"] = nsb_model.ap_2nd_inj
            inj2_kwargs[
                "injection_coordinate_reference"
            ] = self._map_ap_info_to_coord_reference(nsb_model.ap_2nd_inj)
            inj2_kwargs["injection_coordinate_depth"] = nsb_model.dv_2nd_inj
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
            not nsb_model.has_inj_procedure()
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

    @staticmethod
    def _map_auth_id_to_exp_name(
        nsb_author_id: Optional[str],
    ) -> Optional[str]:
        """Maps NSB Author ID to Experimenter name as "NSB" + ID"""
        return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"

    @staticmethod
    def _map_hemisphere(
        nsb_hemisphere: Optional[Hemisphere],
    ) -> Optional[Side]:
        """Maps NSB Hemisphere to AIND Side"""
        if nsb_hemisphere == Hemisphere.LEFT:
            return Side.LEFT
        elif nsb_hemisphere == Hemisphere.RIGHT:
            return Side.RIGHT
        else:
            return None

    @staticmethod
    def _map_craniotomy_type(
        nsb_craniotomy: Optional[NSBCraniotomyType],
    ) -> Optional[CraniotomyType]:
        """Maps NSB CraniotomyType into AIND CraniotomyType"""
        if nsb_craniotomy == NSBCraniotomyType.VISUAL_CORTEX:
            return CraniotomyType.VISCTX
        elif nsb_craniotomy == NSBCraniotomyType.FRONTAL_WINDOW:
            return CraniotomyType.THREE_MM
        elif (
            nsb_craniotomy == NSBCraniotomyType.WHC_NP
            or nsb_craniotomy == NSBCraniotomyType.WHC_2P
        ):
            return CraniotomyType.WHC
        else:
            return CraniotomyType.OTHER

    @staticmethod
    def _map_nsb_craniotomy_type_to_size(
        cran_type: NSBCraniotomyType,
    ) -> Optional[float]:
        """Maps NSB CraniotomyType into size"""
        if cran_type == NSBCraniotomyType.VISUAL_CORTEX:
            return 5.0
        elif cran_type == NSBCraniotomyType.FRONTAL_WINDOW:
            return 3.0
        else:
            return None

    @staticmethod
    def _map_ap_info_to_coord_reference(
        _: None,
    ) -> Optional[CoordinateReferenceLocation]:
        """Maps NSB virus ap into AIND CoordinateReferenceLocation"""
        return None

    @staticmethod
    def _map_virus_strain_to_materials(
        virus_strain: Optional[str],
    ) -> Optional[InjectionMaterial]:
        """Maps NASB virus strain into AIND InjectionMaterials"""
        if virus_strain is None:
            return None
        else:
            return InjectionMaterial.construct(full_genome_name=virus_strain)

    @staticmethod
    def _map_datetime_to_date(dt: datetime) -> Optional[date]:
        """Maps datetime like '2020-10-10 00:00:00' into date like
        '2020-10-10'"""
        if dt is None:
            return None
        else:
            return dt.date()

    @staticmethod
    def _duration_to_minutes(duration: Optional[timedelta]) -> Optional[float]:
        """Converts Optional[timedelta] into an Optional[float]"""
        return None if duration is None else duration.total_seconds() / 60
