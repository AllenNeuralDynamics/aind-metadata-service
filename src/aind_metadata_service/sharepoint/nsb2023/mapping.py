"""Maps client objects from NSB Sharepoint database to internal AIND models."""

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
    SubjectProcedure,
)
from office365.sharepoint.client_context import ClientContext

from aind_metadata_service.sharepoint.nsb2019.mapping import NSB2019Mapping
from aind_metadata_service.sharepoint.nsb2023.models import BurrHoleProcedure
from aind_metadata_service.sharepoint.nsb2023.models import (
    CraniotomyType as NSBCraniotomyType,
)
from aind_metadata_service.sharepoint.nsb2023.models import (
    HeadPostInfo2023,
    InjectionType,
    NSBList2023,
)


class NSB2023Mapping(NSB2019Mapping):
    """Provides methods to retrieve procedure information from sharepoint,
    parses the response into an intermediate data model, and maps that model
    into AIND internal Procedures model."""

    def get_procedures_from_sharepoint(
        self, subject_id: str, client_context: ClientContext, list_title: str
    ):
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
        labtrack_alias = NSBList2023.__fields__.get("labtracks_id").alias
        filter_string = f"{labtrack_alias} eq '{subject_id}'"
        list_view = client_context.web.lists.get_by_title(
            list_title
        ).views.get_by_title(getattr(NSBList2023, "_view_title"))
        client_context.load(list_view)
        client_context.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        client_context.load(list_items)
        client_context.execute_query()
        list_of_procedures = []
        for list_item in list_items:
            parsed_nsb_model = NSBList2023.parse_obj(list_item.to_json())
            procedures = self.map_nsb_model(parsed_nsb_model)
            list_of_procedures.extend(procedures)
        return list_of_procedures

    # flake8: noqa: C901
    def map_nsb_model(self, nsb_model: NSBList2023) -> List[SubjectProcedure]:
        """Maps an individual list item model into List[SubjectProcedures]"""
        procedures = []
        experimenter_full_name = self._map_auth_id_to_exp_name(
            nsb_model.author_id
        )
        iacuc_protocol = nsb_model.iacuc_protocol

        # Check if any headframe procedures
        if nsb_model.has_hp_procedure():
            hp_during = nsb_model.headpost_perform_during
            hf_surgery_during_info = nsb_model.surgery_during_info(hp_during)
            anaesthetic = Anaesthetic.construct(
                type="isoflurane",
                duration=(
                    hf_surgery_during_info.anaesthetic_duration_in_minutes
                ),
                level=hf_surgery_during_info.anaesthetic_level,
            )
            headpost_info = HeadPostInfo2023.from_hp_and_hp_type(
                hp=nsb_model.headpost, hp_type=nsb_model.headpost_type
            )

            headframe_procedure = Headframe.construct(
                start_date=self._map_datetime_to_date(
                    hf_surgery_during_info.start_date
                ),
                end_date=self._map_datetime_to_date(
                    hf_surgery_during_info.start_date
                ),
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=hf_surgery_during_info.weight_prior,
                animal_weight_post=hf_surgery_during_info.weight_post,
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
            cran_during_info = nsb_model.surgery_during_info(cran_during)
            anaesthetic = Anaesthetic.construct(
                type="isoflurane",
                duration=cran_during_info.anaesthetic_duration_in_minutes,
                level=cran_during_info.anaesthetic_level,
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
                start_date=self._map_datetime_to_date(
                    cran_during_info.start_date
                ),
                end_date=self._map_datetime_to_date(
                    cran_during_info.start_date
                ),
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=cran_during_info.weight_prior,
                animal_weight_post=cran_during_info.weight_post,
                craniotomy_type=craniotomy_type,
                craniotomy_size=craniotomy_size,
                anaesthesia=anaesthetic,
                workstation_id=cran_during_info.workstation_id,
                recovery_time=cran_during_info.recovery_time,
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
                burr_hole_info = nsb_model.burr_hole_info(
                    burr_hole_num=burr_hole_num
                )
                burr_during_info = nsb_model.surgery_during_info(
                    during=burr_hole_info.during,
                    inj_type=burr_hole_info.inj_type,
                )
                anaesthetic = Anaesthetic.construct(
                    type="isoflurane",
                    duration=burr_during_info.anaesthetic_duration_in_minutes,
                    level=burr_during_info.anaesthetic_level,
                )
                injection_materials = (
                    None
                    if burr_hole_info.virus_strain is None
                    else InjectionMaterial.construct(
                        full_genome_name=burr_hole_info.virus_strain
                    )
                )
                if burr_hole_info.inj_type == InjectionType.IONTOPHORESIS:
                    injection_proc = IontophoresisInjection.construct(
                        start_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        end_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=burr_during_info.weight_prior,
                        animal_weight_post=burr_during_info.weight_post,
                        workstation_id=burr_during_info.workstation_id,
                        injection_hemisphere=self._map_hemisphere(
                            burr_hole_info.hemisphere
                        ),
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_current=burr_hole_info.inj_current,
                        injection_duration=self._duration_to_minutes(
                            burr_hole_info.inj_duration
                        ),
                        alternating_current=burr_hole_info.alternating_current,
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        anaesthesia=anaesthetic,
                        bregma_to_lambda_distance=nsb_model.breg_2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                elif burr_hole_info.inj_type == InjectionType.NANOJECT:
                    injection_proc = NanojectInjection.construct(
                        start_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        end_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=burr_during_info.weight_prior,
                        animal_weight_post=burr_during_info.weight_post,
                        workstation_id=burr_during_info.workstation_id,
                        injection_hemisphere=self._map_hemisphere(
                            burr_hole_info.hemisphere
                        ),
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_current=burr_hole_info.inj_current,
                        injection_duration=self._duration_to_minutes(
                            burr_hole_info.inj_duration
                        ),
                        injection_volume=burr_hole_info.inj_volume,
                        alternating_current=burr_hole_info.alternating_current,
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        anaesthesia=anaesthetic,
                        bregma_to_lambda_distance=nsb_model.breg_2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                else:
                    injection_proc = BrainInjection.construct(
                        start_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        end_date=self._map_datetime_to_date(
                            burr_during_info.start_date
                        ),
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=burr_during_info.weight_prior,
                        animal_weight_post=burr_during_info.weight_post,
                        workstation_id=burr_during_info.workstation_id,
                        injection_hemisphere=self._map_hemisphere(
                            burr_hole_info.hemisphere
                        ),
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_duration=self._duration_to_minutes(
                            burr_hole_info.inj_duration
                        ),
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        anaesthesia=anaesthetic,
                        bregma_to_lambda_distance=nsb_model.breg_2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                procedures.append(injection_proc)
            if nsb_model.has_burr_hole_procedure(
                burr_hole_num=burr_hole_num,
                burr_hole_procedure=BurrHoleProcedure.FIBER_IMPLANT,
            ):
                probe_name = self._map_burr_hole_number_to_probe(burr_hole_num)
                burr_hole_info = nsb_model.burr_hole_info(
                    burr_hole_num=burr_hole_num
                )
                burr_during_info = nsb_model.surgery_during_info(
                    during=burr_hole_info.during,
                    inj_type=burr_hole_info.inj_type,
                )
                bregma_to_lambda_distance = nsb_model.breg_2_lamb
                anaesthetic = Anaesthetic.construct(
                    type="isoflurane",
                    duration=burr_during_info.anaesthetic_duration_in_minutes,
                    level=burr_during_info.anaesthetic_level,
                )
                ophys_probe = OphysProbe.construct(
                    name=probe_name,
                    stereotactic_coordinate_ml=burr_hole_info.coordinate_ml,
                    stereotactic_coordinate_ap=burr_hole_info.coordinate_ap,
                    stereotactic_coordinate_dv=(
                        burr_hole_info.fiber_implant_depth
                    ),
                    angle=burr_hole_info.angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=(
                        CoordinateReferenceLocation.BREGMA
                    ),
                )
                fiber_implant_proc = FiberImplant.construct(
                    start_date=self._map_datetime_to_date(
                        burr_during_info.start_date
                    ),
                    end_date=self._map_datetime_to_date(
                        burr_during_info.start_date
                    ),
                    experimenter_full_name=experimenter_full_name,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=burr_during_info.weight_prior,
                    animal_weight_post=burr_during_info.weight_post,
                    probes=ophys_probe,
                    anaesthesia=anaesthetic,
                )
                procedures.append(fiber_implant_proc)

        # Create generic procedure model if no specific procedures found
        if len(procedures) == 0:
            subject_procedure = SubjectProcedure.construct(
                start_date=self._map_datetime_to_date(
                    nsb_model.date_of_surgery
                ),
                end_date=self._map_datetime_to_date(nsb_model.date_of_surgery),
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=nsb_model.weight_before_surgery,
                animal_weight_post=nsb_model.weight_after_surgery,
            )
            procedures.append(subject_procedure)

        return procedures

    @staticmethod
    def _map_craniotomy_type(
        nsb_craniotomy: Optional[NSBCraniotomyType],
    ) -> Optional[CraniotomyType]:
        """Maps NSB CraniotomyType into AIND CraniotomyType"""
        if nsb_craniotomy == NSBCraniotomyType.FIVE_MM:
            return CraniotomyType.FIVE_MM
        elif nsb_craniotomy == NSBCraniotomyType.THREE_MM:
            return CraniotomyType.THREE_MM
        elif nsb_craniotomy == NSBCraniotomyType.WHC:
            return CraniotomyType.WHC
        else:
            return CraniotomyType.OTHER

    @staticmethod
    def _map_burr_hole_number_to_probe(
        burr_hole_num: int,
    ) -> Optional[ProbeName]:
        """Maps NSB Burr hole number into AIND ProbeName"""
        if burr_hole_num == 1:
            return ProbeName.PROBE_A
        elif burr_hole_num == 2:
            return ProbeName.PROBE_B
        elif burr_hole_num == 3:
            return ProbeName.PROBE_C
        elif burr_hole_num == 4:
            return ProbeName.PROBE_D
        else:
            return None
