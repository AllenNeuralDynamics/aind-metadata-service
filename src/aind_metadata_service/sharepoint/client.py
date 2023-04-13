"""Module to create client to connect to sharepoint database"""

from enum import Enum
from typing import List, Optional, Union

from aind_data_schema.procedures import (
    Anaesthetic,
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
    Procedures,
    SubjectProcedure,
)
from fastapi.responses import JSONResponse
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection

from aind_metadata_service.response_handler import Responses
from aind_metadata_service.sharepoint.nsb2019.models import \
    NSBList2019
from aind_metadata_service.sharepoint.nsb2023.models import NSBList2023
from aind_metadata_service.sharepoint.utils import (
    convert_hour_to_mins,
    convert_str_to_bool,
    map_choice,
    map_date_to_datetime,
    map_hemisphere,
    parse_str_into_float,
)


class ListVersions(Enum):
    """Enum class to handle different SharePoint list versions."""

    VERSION_2023 = {
        "list_title": "SWR 2023-Present",
        "view_title": "New Request",
    }
    VERSION_2019 = {
        "list_title": "SWR 2019-2022",
        "view_title": "New Request",
    }


class SharePointClient:
    """This class contains the api to connect to SharePoint db."""

    def __init__(
        self, site_url: str, client_id: str, client_secret: str
    ) -> None:
        """
        Initialize a client
        Parameters
        ----------
        site_url : str
           sharepoint site url
        client_id : str
            username for principal account to access sharepoint
        client_secret : str
            password for principal account to access sharepoint
        """
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = ClientCredential(self.client_id, self.client_secret)
        self.client_context = ClientContext(self.site_url).with_credentials(
            self.credentials
        )

    @staticmethod
    def _get_filter_string(version: ListVersions, subject_id: str) -> str:
        """
        Helper method to return a filter on the list
        Parameters
        ----------
        version : ListVersions
          Version of the SharePoint List being queried against
        subject_id : str
          ID of the subject being queried for

        Returns
        -------
        str
          A string to pass into a query filter

        """
        version_2019 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NSBList2019.ListField.LAB_TRACKS_ID}"
            f")"
        )
        version_2023 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NSBList2023.ListField.LAB_TRACKS_ID}"
            f")"
        )
        if version == ListVersions.VERSION_2019:
            filter_string = version_2019
        else:
            filter_string = version_2023
        return filter_string

    def get_procedure_info(
        self,
        subject_id: str,
    ) -> JSONResponse:
        """
        Primary interface. Maps a subject_id to a response.
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.

        Returns
        -------
        JSONResponse
          A response

        """
        # TODO: Add try to handle internal server error response.
        subject_procedures = []
        ctx = self.client_context
        for version in ListVersions:
            filter_string = self._get_filter_string(version, subject_id)
            list_view = ctx.web.lists.get_by_title(
                version["list_title"]
            ).views.get_by_title(version["view_title"])
            ctx.load(list_view)
            ctx.execute_query()
            list_items = list_view.get_items().filter(filter_string)
            ctx.load(list_items)
            ctx.execute_query()
            subject_procedures.extend(self._map_response(version, list_items))
        response = self._handle_response_from_sharepoint(
            subject_id=subject_id, subject_procedures=subject_procedures
        )
        return response

    def _map_response(self, version, list_items: ListItemCollection) -> list:
        """
        Maps sharepoint response to lists of procedures
        Parameters
        ----------
        version : ListVersions
           Version of the SharePoint List being queried against
        list_items : ListItemCollection
           SharePoint returns a ListItemCollection given a query
        Returns
        -------
        procedures : list
           Either an empty list or list of SubjectProcedures models
        """
        if version == ListVersions.VERSION_2023:
            procedures = self._map_2023_response(list_items)
        else:
            procedures = self._map_2019_response(list_items)
        return procedures

    @staticmethod
    def _handle_response_from_sharepoint(
        subject_id: str, subject_procedures=None
    ) -> JSONResponse:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        subject_procedures: None/list

        Returns
        -------
        JSONResponse
          Either a Procedures model or an error response

        """
        if subject_procedures:
            procedures = Procedures.construct(subject_id=subject_id)
            procedures.subject_procedures = subject_procedures
            response = Responses.model_response(procedures)
        else:
            response = Responses.no_data_found_response()
        return response

    def _map_2023_response(self, list_items: ListItemCollection) -> list:
        """Maps sharepoint response when 2023 version"""
        list_fields = NSBList2023.ListField
        subject_procedures = []
        str_helpers = NSBList2023.StringParserHelper
        nsb_proc_types = NSBList2023.ProcedureType
        for list_item in list_items:
            if list_item.get_property(list_fields.PROCEDURE):
                procedure = list_item.get_property(list_fields.PROCEDURE)
                procedure_types = []
                if str_helpers.WITH_HEADPOST in procedure:
                    procedure = procedure.replace(
                        str_helpers.WITH_HEADPOST, ""
                    )
                    procedure_types.append(nsb_proc_types.WITH_HEADPOST)
                if procedure != nsb_proc_types.INJECTION_FIBER_IMPLANT:
                    procedure_types.extend(
                        procedure.split(
                            str_helpers.PROCEDURE_TYPE_SPLITTER
                        )
                    )
                else:
                    procedure_types.append(procedure)
            else:
                procedure_types = []
                subject_procedures.append(
                    self._map_list_item_to_subject_procedure(list_item)
                )
            for procedure_type in procedure_types:
                if procedure_type in {
                    nsb_proc_types.WITH_HEADPOST,
                    nsb_proc_types.HP_ONLY,
                    nsb_proc_types.HP_TRANSCRANIAL,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_head_frame_2023(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.VISUAL_CTX_NP,
                    nsb_proc_types.VISUAL_CTX_2P,
                    nsb_proc_types.FRONTAL_CTX_2P,
                    nsb_proc_types.MOTOR_CTX,
                    nsb_proc_types.WHC_NP,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_craniotomy_2023(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.INJECTION,
                    nsb_proc_types.STEREOTAXIC_INJECTION,
                    nsb_proc_types.INJ,
                    nsb_proc_types.ISI_INJECTION,
                    nsb_proc_types.FIBER_OPTIC_IMPLANT,
                    nsb_proc_types.INJECTION_FIBER_IMPLANT,
                }:
                    subject_procedures.extend(self._map_burr_holes(list_item))
        return subject_procedures

    def _map_2019_response(self, list_items: ListItemCollection) -> list:
        """Maps sharepoint response when 2019 version"""
        list_fields = NSBList2019.ListField
        str_helpers = NSBList2019.StringParserHelper
        nsb_proc_types = NSBList2019.ProcedureType
        subject_procedures = []
        for list_item in list_items:
            if list_item.get_property(list_fields.PROCEDURE):
                procedure_types = list_item.get_property(
                    list_fields.PROCEDURE
                ).split(str_helpers.PROCEDURE_TYPE_SPLITTER)
            else:
                procedure_types = []
                subject_procedures.append(
                    self._map_list_item_to_subject_procedure(list_item)
                )
            for procedure_type in procedure_types:
                if procedure_type in {
                    nsb_proc_types.HEAD_PLANT,
                    nsb_proc_types.HP_ONLY,
                    nsb_proc_types.HP_TRANSCRANIAL,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_head_frame(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.STEREOTAXIC_INJECTION_COORDINATE,
                    nsb_proc_types.STEREOTAXIC_INJECTION,
                    nsb_proc_types.INJECTION,
                    nsb_proc_types.INJ,
                }:
                    subject_procedures.extend(
                        self._map_list_item_to_injections(list_item)
                    )
                if procedure_type == nsb_proc_types.OPTIC_FIBER_IMPLANT:
                    subject_procedures.append(
                        self._map_list_item_to_fiber_implant(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.WHOLE_HEMISPHERE_CRANIOTOMY_NP,
                    nsb_proc_types.C_MULTISCOPE,
                    nsb_proc_types.C_CAM,
                    nsb_proc_types.C,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_craniotomy(list_item)
                    )
        return subject_procedures

    def _map_list_item_to_subject_procedure(
        self, list_item: ClientObject
    ) -> SubjectProcedure:
        """Maps a Sharepoint ClientObject to generic SubjectProcedure model"""
        list_fields = NSBList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY)
        )
        subject_procedure = SubjectProcedure.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
        )
        return subject_procedure

    @staticmethod
    def _map_experimenter_name(nsb_author_id: Optional[str]) -> Optional[str]:
        """Maps Experimenter name as "NSB" + ID"""
        return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"

    @staticmethod
    def _map_1st_injection_anaesthesia(
        list_item: ClientObject, list_fields
    ) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for Injection"""
        anaesthetic_type = "isoflurane"
        duration = list_item.get_property(
            list_fields.FIRST_INJECTION_ISO_DURATION
        )
        level = list_item.get_property(list_fields.ROUND1_INJ_ISOLEVEL)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            duration=duration,
            level=level,
        )
        return anaesthetic

    @staticmethod
    def _map_injection_materials(full_genome_name):
        """Maps injection materials"""
        if full_genome_name:
            injection_materials = InjectionMaterial.construct(
                full_genome_name=full_genome_name
            )
        else:
            injection_materials = None
        return injection_materials

    @staticmethod
    def _map_inj_coordinate_reference(
        ap,
    ) -> Optional[CoordinateReferenceLocation]:
        """Maps coordinate reference location"""
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        if "rostral" in ap:
            coordinate_reference = CoordinateReferenceLocation.LAMBDA
        return coordinate_reference

    def _map_1st_injection(
        self, list_item: ClientObject, list_fields
    ) -> Union[NanojectInjection, IontophoresisInjection]:
        """Maps a SharePoint ClientObject to an Injection model"""
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE1ST_INJECTION)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(
                list_fields.FIRST_INJECTION_WEIGHT_BEFOR
            )
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(
                list_fields.FIRST_INJECTION_WEIGHT_AFTER
            )
        )
        anaesthesia = self._map_1st_injection_anaesthesia(
            list_item, list_fields
        )
        injection_duration = parse_str_into_float(
            list_item.get_property(list_fields.INJ1_LENGHTOF_TIME)
        )
        recovery_time = list_item.get_property(
            list_fields.FIRST_INJ_RECOVERY
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.WORK_STATION1ST_INJECTION)
        )
        injection_type = list_item.get_property(list_fields.INJ1_TYPE)
        injection_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.VIRUS_HEMISPHERE)
        )
        injection_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_M_L)
        )
        injection_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_A_P)
        )
        injection_coordinate_reference = self._map_inj_coordinate_reference(
            list_item.get_property(list_fields.VIRUS_A_P)
        )
        # TODO: handle 2 values for depth (for now using 1st value)
        injection_coordinate_depth = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_D_V)
        )
        injection_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ1ANGLE0)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        full_genome_name = list_item.get_property(
            list_fields.INJ1_VIRUS_STRAIN_RT
        )
        injection_materials = self._map_injection_materials(full_genome_name)
        if (
            injection_type
            == NSBList2019.InjectionType.IONTO
        ):
            instrument_id = list_item.get_property(
                list_fields.IONTO_NUMBER_INJ1
            )
            injection_current = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_CURRENT)
            )
            alternating_current = list_item.get_property(
                list_fields.INJ1_ALTERNATING_TIME
            )
            injection = IontophoresisInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                injection_duration=injection_duration,
                recovery_time=recovery_time,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_hemisphere=injection_hemisphere,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_angle=injection_angle,
                injection_type=injection_type,
                injection_current=injection_current,
                alternating_current=alternating_current,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_coordinate_reference=injection_coordinate_reference,
                injection_materials=injection_materials,
            )
        else:
            instrument_id = list_item.get_property(
                list_fields.NANOJECT_NUMBER_INJ10
            )
            injection_volume = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_VOL)
            )
            injection = NanojectInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                injection_duration=injection_duration,
                recovery_time=recovery_time,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_hemisphere=injection_hemisphere,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_angle=injection_angle,
                injection_type=injection_type,
                injection_volume=injection_volume,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_coordinate_reference=injection_coordinate_reference,
                injection_materials=injection_materials,
            )
        return injection

    @staticmethod
    def _map_2nd_injection_anaesthesia(
        list_item: ClientObject, list_fields
    ) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for Injection"""
        anaesthetic_type = "isoflurane"
        duration = list_item.get_property(
            list_fields.FIRST_INJECTION_ISO_DURATION
        )
        level = list_item.get_property(list_fields.ROUND2_INJ_ISOLEVEL)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            duration=duration,
            level=level,
        )
        return anaesthetic

    def _map_2nd_injection(
        self, list_item: ClientObject, list_fields
    ) -> Union[NanojectInjection, IontophoresisInjection]:
        """Maps Sharepoint ListItem to a 2nd Injection model"""
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE2ND_INJECTION)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(
                list_fields.SECOND_INJECTION_WEIGHT_BEFORE
            )
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(
                list_fields.SECOND_INJECTION_WEIGHT_AFTER
            )
        )
        anaesthesia = self._map_2nd_injection_anaesthesia(
            list_item, list_fields
        )
        injection_duration = parse_str_into_float(
            list_item.get_property(list_fields.INJ2_LENGHTOF_TIME)
        )
        recovery_time = list_item.get_property(
            list_fields.SECOND_INJ_RECOVER
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.WORK_STATION2ND_INJECTION)
        )
        injection_type = list_item.get_property(list_fields.INJ2_TYPE)
        injection_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.HEMISPHERE2ND_INJ)
        )
        injection_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.ML2ND_INJ)
        )
        injection_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.AP2ND_INJ)
        )
        injection_coordinate_reference = self._map_inj_coordinate_reference(
            list_item.get_property(list_fields.AP2ND_INJ)
        )
        # TODO: handle 2 values for depth (for now using 1st value)
        injection_coordinate_depth = parse_str_into_float(
            list_item.get_property(list_fields.DV2ND_INJ)
        )
        injection_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ2ANGLE0)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        full_genome_name = list_item.get_property(
            list_fields.INJ2_VIRUS_STRAIN_RT
        )
        injection_materials = self._map_injection_materials(full_genome_name)
        if (
            injection_type
            == NSBList2019.InjectionType.IONTO
        ):
            instrument_id = list_item.get_property(
                list_fields.IONTO_NUMBER_INJ2
            )
            injection_current = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_CURRENT)
            )
            alternating_current = list_item.get_property(
                list_fields.INJ2_ALTERNATING_TIME
            )
            injection = IontophoresisInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                injection_duration=injection_duration,
                recovery_time=recovery_time,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_hemisphere=injection_hemisphere,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_angle=injection_angle,
                injection_type=injection_type,
                injection_current=injection_current,
                alternating_current=alternating_current,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_coordinate_reference=injection_coordinate_reference,
                injection_materials=injection_materials,
            )
        else:
            instrument_id = list_item.get_property(
                list_fields.NANOJECT_NUMBER_INJ2
            )
            injection_volume = parse_str_into_float(
                list_item.get_property(list_fields.INJ2_VOL)
            )
            injection = NanojectInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=animal_weight_prior,
                animal_weight_post=animal_weight_post,
                anaesthesia=anaesthesia,
                injection_duration=injection_duration,
                recovery_time=recovery_time,
                workstation_id=workstation_id,
                instrument_id=instrument_id,
                injection_hemisphere=injection_hemisphere,
                injection_coordinate_ml=injection_coordinate_ml,
                injection_coordinate_ap=injection_coordinate_ap,
                injection_coordinate_depth=injection_coordinate_depth,
                injection_angle=injection_angle,
                injection_type=injection_type,
                injection_volume=injection_volume,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                injection_coordinate_reference=injection_coordinate_reference,
                injection_materials=injection_materials,
            )
        return injection

    def _map_list_item_to_injections(
        self, list_item: ClientObject
    ) -> List[Union[NanojectInjection, IontophoresisInjection]]:
        """Maps a Sharepoint ListItem to a list of Injection models"""
        injections = []
        list_fields = NSBList2019.ListField
        injection_1 = self._map_1st_injection(list_item, list_fields)
        injections.append(injection_1)
        # check if there's a 2nd injection in list item
        inj2round = list_item.get_property(list_fields.INJ2_ROUND)
        if map_choice(inj2round):
            injection_2 = self._map_2nd_injection(list_item, list_fields)
            injections.append(injection_2)
        return injections

    def _map_list_item_to_ophys_probe(
        self, list_item: ClientObject, list_fields
    ) -> List[OphysProbe]:
        """Maps a Sharepoint ListItem to list of OphysProbe models"""
        ophys_probes = []
        # TODO: missing fields manufacturer, part_number, core_diameter
        #  numerical_aperature, ferrule_material
        fiber_implant1 = list_item.get_property(
            list_fields.FIBER_IMPLANT1
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        if fiber_implant1:
            name = ProbeName.PROBE_A
            stereotactic_coordinate_ml = parse_str_into_float(
                list_item.get_property(list_fields.VIRUS_M_L)
            )
            stereotactic_coordinate_ap = parse_str_into_float(
                list_item.get_property(list_fields.VIRUS_A_P)
            )
            coordinate_reference = self._map_inj_coordinate_reference(
                list_item.get_property(list_fields.VIRUS_A_P)
            )
            stereotactic_coordinate_dv = parse_str_into_float(
                list_item.get_property(list_fields.FIBER_IMPLANT1_DV)
            )
            angle = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_ANGLE_V2)
            )
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
        fiber_implant2 = list_item.get_property(
            list_fields.FIBER_IMPLANT2
        )
        if fiber_implant2:
            name = ProbeName.PROBE_B
            stereotactic_coordinate_ml = parse_str_into_float(
                list_item.get_property(list_fields.ML2ND_INJ)
            )
            stereotactic_coordinate_ap = parse_str_into_float(
                list_item.get_property(list_fields.AP2ND_INJ)
            )
            coordinate_reference = self._map_inj_coordinate_reference(
                list_item.get_property(list_fields.AP2ND_INJ)
            )
            stereotactic_coordinate_dv = parse_str_into_float(
                list_item.get_property(list_fields.FIBER_IMPLANT2_DV)
            )
            angle = parse_str_into_float(
                list_item.get_property(list_fields.INJ2_ANGLE_V2)
            )
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
        return ophys_probes

    def _map_list_item_to_fiber_implant(
        self,
        list_item: ClientObject,
    ) -> FiberImplant:
        """Maps a SharePoint ListItem to a FiberImplant model"""
        list_fields = NSBList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY)
        )
        probes = self._map_list_item_to_ophys_probe(list_item, list_fields)
        fiber_implant = FiberImplant.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            probes=probes,
        )
        return fiber_implant

    @staticmethod
    def _map_hp_anaesthesia(list_item, list_fields) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for HP/craniotomy"""
        anaesthetic_type = "isoflurane"
        # TODO: duration
        level = list_item.get_property(list_fields.HP_ISO_LEVEL)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            level=level,
        )
        return anaesthetic

    @staticmethod
    def _map_craniotomy_type(sp_craniotomy_type) -> Optional[CraniotomyType]:
        """Maps craniotomy type"""
        CT = NSBList2019.CraniotomyType
        if sp_craniotomy_type:
            if sp_craniotomy_type == CT.VISUAL_CORTEX:
                return CraniotomyType.VISCTX
            elif sp_craniotomy_type == CT.FRONTAL_WINDOW:
                return CraniotomyType.THREE_MM
            elif sp_craniotomy_type in {
                CT.WHC_NP,
                CT.WHC_2P,
            }:
                return CraniotomyType.WHC
            else:
                return CraniotomyType.OTHER
        return None

    def _map_list_item_to_craniotomy(
        self, list_item: ClientObject
    ) -> Craniotomy:
        """Maps a SharePoint ListItem to a Craniotomy model"""
        # TODO: missing fields (implant_part_number, protective_material)
        list_fields = NSBList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY)
        )
        anaesthesia = self._map_hp_anaesthesia(list_item, list_fields)
        craniotomy_type = self._map_craniotomy_type(
            list_item.get_property(list_fields.CRANIOTOMY_TYPE)
        )
        if craniotomy_type == CraniotomyType.VISCTX:
            craniotomy_coordinates_reference = (
                CoordinateReferenceLocation.LAMBDA
            )
        else:
            craniotomy_coordinates_reference = None
        craniotomy_hemisphere = map_choice(
            list_item.get_property(list_fields.HP_LOC)
        )
        craniotomy_coordinates_ml = parse_str_into_float(
            list_item.get_property(list_fields.HP_M_L)
        )
        craniotomy_coordinates_ap = parse_str_into_float(
            list_item.get_property(list_fields.HP_A_P)
        )
        craniotomy_size = parse_str_into_float(
            list_item.get_property(list_fields.IMPLANT_ID_COVERSLIP_TYPE)
        )
        dura_removed = convert_str_to_bool(
            list_item.get_property(list_fields.HP_DUROTOMY)
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.HP_WORK_STATION)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        craniotomy = Craniotomy.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            anaesthesia=anaesthesia,
            craniotomy_type=craniotomy_type,
            craniotomy_hemisphere=craniotomy_hemisphere,
            craniotomy_coordinates_ml=craniotomy_coordinates_ml,
            craniotomy_coordinates_ap=craniotomy_coordinates_ap,
            craniotomy_size=craniotomy_size,
            dura_removed=dura_removed,
            workstation_id=workstation_id,
            bregma_to_lambda_distance=bregma_to_lambda_distance,
            craniotomy_coordinates_reference=craniotomy_coordinates_reference,
        )
        return craniotomy

    @staticmethod
    def _map_headpost_type(headpost_type: str):
        """Maps Sharepoint HeadPostType to fields in HeadFrame model"""
        if (
            headpost_type
            == NSBList2019.HeadPostType.CAM
        ):
            headframe_type = "CAM-style"
            headframe_part_number = "0160-100-10 Rev A"
            well_type = "CAM-style"
            well_part_number = None
        elif (
                headpost_type
                == NSBList2019.HeadPostType.NEUROPIXEL
        ):
            headframe_type = "Neuropixel-style"
            headframe_part_number = "0160-100-10"
            well_type = "Neuropixel-style"
            well_part_number = "0160-200-36"
        elif (
                headpost_type
                == NSBList2019.HeadPostType.MESO_NGC
        ):
            headframe_type = "NGC-style"
            headframe_part_number = "0160-100-10"
            well_type = "Mesoscope-style"
            well_part_number = "0160-200-20"
        elif (
                headpost_type
                == NSBList2019.HeadPostType.WHC_NP
        ):
            headframe_type = "WHC #42"
            headframe_part_number = "42"
            well_type = "Neuropixel-style"
            well_part_number = "0160-200-36"
        elif (
                headpost_type
                == NSBList2019.HeadPostType.NGC
        ):
            headframe_type = "NGC-style"
            headframe_part_number = "0160-100-10"
            well_type = None
            well_part_number = None
        elif (
                headpost_type
                == NSBList2019.HeadPostType.AI_HEADBAR
        ):
            headframe_type = "AI Straight Headbar"
            headframe_part_number = None
            well_type = None
            well_part_number = None
        else:
            return None, None, None, None
        return (
            headframe_type,
            headframe_part_number,
            well_type,
            well_part_number,
        )

    def _map_list_item_to_head_frame(
        self, list_item: ClientObject
    ) -> Headframe:
        """Maps a SharePoint ListItem to a HeadFrame model"""
        list_fields = NSBList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY)
        )
        anaesthesia = self._map_hp_anaesthesia(list_item, list_fields)
        headpost_type = list_item.get_property(list_fields.HEADPOST_TYPE)
        (
            headframe_type,
            headframe_part_number,
            well_type,
            well_part_number,
        ) = self._map_headpost_type(headpost_type)
        head_frame = Headframe.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            anaesthesia=anaesthesia,
            headframe_type=headframe_type,
            headframe_part_number=headframe_part_number,
            well_type=well_type,
            well_part_number=well_part_number,
        )
        return head_frame

    @staticmethod
    def _map_2023_anaesthesia(
        list_item, list_fields, surgery_during
    ) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level based on surgery order"""
        surgery_order = NSBList2023.SurgeryOrder
        anaesthetic_type = "isoflurane"
        if surgery_during == surgery_order.SECOND:
            duration = convert_hour_to_mins(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_ISO_DURATION
                )
            )
            level = parse_str_into_float(
                list_item.get_property(list_fields.ROUND1_INJ_ISOLEVEL)
            )
        else:
            # default is Initial Surgery
            duration = convert_hour_to_mins(
                list_item.get_property(list_fields.ISO_ON)
            )
            level = parse_str_into_float(
                list_item.get_property(list_fields.HP_ISO_LEVEL)
            )
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            duration=duration,
            level=level,
        )
        return anaesthetic

    @staticmethod
    def _map_initial_followup_date(list_item, list_fields, surgery_during):
        """Maps date of procedure based on surgery order"""
        surgery_order = NSBList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND:
            start_date = map_date_to_datetime(
                list_item.get_property(list_fields.DATE1ST_INJECTION)
            )
        else:
            start_date = map_date_to_datetime(
                list_item.get_property(list_fields.DATE_OF_SURGERY)
            )
        return start_date

    @staticmethod
    def _map_initial_followup_injection(
        list_item, list_fields, injection_type, surgery_during
    ):
        """
        Maps injection workstation_id, recovery_time, and instrument_id
        based on surgery order
        """
        injection_types = NSBList2023.InjectionType
        surgery_order = NSBList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND:
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.FIRST_INJ_RECOVERY)
            )
            if injection_type.strip() == injection_types.IONTO:
                instrument_id = map_choice(
                    list_item.get_property(list_fields.IONTO_NUMBER_INJ2)
                )
            else:
                instrument_id = map_choice(
                    list_item.get_property(
                        list_fields.NANOJECT_NUMBER_INJ2
                    )
                )
        else:
            # default is Initial Surgery
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.HP_RECOVERY)
            )
            if injection_type.strip() == injection_types.IONTO:
                instrument_id = map_choice(
                    list_item.get_property(list_fields.IONTO_NUMBER_INJ1)
                )
            else:
                instrument_id = map_choice(
                    list_item.get_property(
                        list_fields.NANOJECT_NUMBER_INJ10
                    )
                )
        return workstation_id, recovery_time, instrument_id

    @staticmethod
    def _map_initial_followup_craniotomy(
        list_item, list_fields, surgery_during
    ):
        """
        Maps craniotomy workstation_id and recovery_time based on
        surgery order
        """
        surgery_order = NSBList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND:
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.FIRST_INJ_RECOVERY)
            )
        else:
            # default is Initial Surgery
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.HP_RECOVERY)
            )
        return workstation_id, recovery_time

    @staticmethod
    def _map_initial_followup_weight(list_item, list_fields, surgery_during):
        """Maps before and after weight based on surgery order"""
        surgery_order = NSBList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND:
            animal_weight_prior = parse_str_into_float(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_WEIGHT_BEFOR
                )
            )
            animal_weight_post = parse_str_into_float(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_WEIGHT_AFTER
                )
            )
        else:
            animal_weight_prior = parse_str_into_float(
                list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER)
            )
            animal_weight_post = parse_str_into_float(
                list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY)
            )
        return animal_weight_prior, animal_weight_post

    def _map_burr_holes(
        self,
        list_item: ClientObject,
    ) -> List[Union[FiberImplant, IontophoresisInjection, NanojectInjection]]:
        """Maps SharePoint ListItem to list of FiberImplants/Injections"""
        list_fields = NSBList2023.ListField
        burr_procedures = []
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_1)):
            burr_procedures.extend(self._map_burr_hole_1(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_2)):
            burr_procedures.extend(self._map_burr_hole_2(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_3)):
            burr_procedures.extend(self._map_burr_hole_3(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_4)):
            burr_procedures.extend(self._map_burr_hole_4(list_item))
        return burr_procedures

    def _map_burr_hole_1(
        self,
        list_item: ClientObject,
    ) -> List[Union[IontophoresisInjection, NanojectInjection, FiberImplant]]:
        """Maps 1st burr hole to Injections and/or FiberImplants"""
        nsb_burr_types = NSBList2023.BurrHoleType
        list_fields = NSBList2023.ListField
        str_helpers = NSBList2023.StringParserHelper
        injection_types = NSBList2023.InjectionType
        burr_1_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_1):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_1).split(
                    str_helpers.BURR_TYPE_SPLITTER
                )
            )
        # map generic burr hole fields
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.VIRUS_HEMISPHERE)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_M_L)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_A_P)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ1_ANGLE_V2)
        )
        # map fields dependent on surgery order (initial or follow up)
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR1_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, burr_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, burr_during
        )
        end_date = start_date
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, burr_during
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION:
                injection_type = list_item.get_property(
                    list_fields.INJ1_TYPE
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.VIRUS_D_V)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ1_VIRUS_STRAIN_RT
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ1_CURRENT)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ1_ALTERNATING_TIME
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ1_IONTO_TIME
                    )
                    injection = IontophoresisInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_current=injection_current,
                        injection_duration=injection_duration,
                        alternating_current=alternating_current,
                        anaesthesia=anaesthesia,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                else:
                    injection_volume = parse_str_into_float(
                        list_item.get_property(
                            list_fields.INJ1VOLPERDEPTH
                        )
                    )
                    injection = NanojectInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_volume=injection_volume,
                        anaesthesia=anaesthesia,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                burr_1_procedures.append(injection)
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT:
                name = ProbeName.PROBE_A
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT1_DV)
                )
                ophys_probe = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=burr_coordinate_ml,
                    stereotactic_coordinate_ap=burr_coordinate_ap,
                    stereotactic_coordinate_dv=fiber_implant_depth,
                    angle=burr_angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                fiber_implant = FiberImplant.construct(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    probes=ophys_probe,
                    anaesthesia=anaesthesia,
                )
                burr_1_procedures.append(fiber_implant)
        return burr_1_procedures

    def _map_burr_hole_2(
        self,
        list_item: ClientObject,
    ) -> List[Union[IontophoresisInjection, NanojectInjection, FiberImplant]]:
        """Maps 2nd burr hole to Injections and/or FiberImplants"""
        nsb_burr_types = NSBList2023.BurrHoleType
        list_fields = NSBList2023.ListField
        str_helpers = NSBList2023.StringParserHelper
        injection_types = NSBList2023.InjectionType
        burr_2_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_2):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_2).split(
                    str_helpers.BURR_TYPE_SPLITTER
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.HEMISPHERE2ND_INJ)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.ML2ND_INJ)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.AP2ND_INJ)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ2_ANGLE_V2)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR2_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, burr_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, burr_during
        )
        end_date = start_date
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, burr_during
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION:
                injection_type = list_item.get_property(
                    list_fields.INJ2_TYPE
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.DV2ND_INJ)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ2_VIRUS_STRAIN_RT
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ2_CURRENT)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ2_ALTERNATING_TIME
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ2_IONTO_TIME
                    )
                    injection = IontophoresisInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_current=injection_current,
                        injection_duration=injection_duration,
                        alternating_current=alternating_current,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                else:
                    injection_volume = parse_str_into_float(
                        list_item.get_property(
                            list_fields.INJ2VOLPERDEPTH
                        )
                    )
                    injection = NanojectInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_volume=injection_volume,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                burr_2_procedures.append(injection)
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT:
                name = ProbeName.PROBE_B
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT2_DV)
                )
                ophys_probe = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=burr_coordinate_ml,
                    stereotactic_coordinate_ap=burr_coordinate_ap,
                    stereotactic_coordinate_dv=fiber_implant_depth,
                    angle=burr_angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                fiber_implant = FiberImplant.construct(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    probes=ophys_probe,
                    anaesthesia=anaesthesia,
                )
                burr_2_procedures.append(fiber_implant)
        return burr_2_procedures

    def _map_burr_hole_3(
        self,
        list_item: ClientObject,
    ) -> List[Union[IontophoresisInjection, NanojectInjection, FiberImplant]]:
        """Maps 3rd burr hole to Injections and/or FiberImplants"""
        nsb_burr_types = NSBList2023.BurrHoleType
        list_fields = NSBList2023.ListField
        str_helpers = NSBList2023.StringParserHelper
        injection_types = NSBList2023.InjectionType
        burr_3_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_3):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_3).split(
                    str_helpers.BURR_TYPE_SPLITTER
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.BURR3_HEMISPHERE)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_ML)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_AP)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_ANGLE)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR3_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, burr_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, burr_during
        )
        end_date = start_date
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, burr_during
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION:
                injection_type = list_item.get_property(
                    list_fields.INJ3_TYPE
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.BURR3_DV)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ_VIRUS_STRAIN_RT
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ3_CURRENT)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ3_ALTERNATING_TIME
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ3_IONTO_TIME
                    )
                    injection = IontophoresisInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_current=injection_current,
                        injection_duration=injection_duration,
                        alternating_current=alternating_current,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                else:
                    injection_volume = parse_str_into_float(
                        list_item.get_property(
                            list_fields.INJ3VOLPERDEPTH
                        )
                    )
                    injection = NanojectInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_volume=injection_volume,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                burr_3_procedures.append(injection)
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT:
                name = ProbeName.PROBE_C
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT3_D)
                )
                ophys_probe = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=burr_coordinate_ml,
                    stereotactic_coordinate_ap=burr_coordinate_ap,
                    stereotactic_coordinate_dv=fiber_implant_depth,
                    angle=burr_angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                fiber_implant = FiberImplant.construct(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    probes=ophys_probe,
                    anaesthesia=anaesthesia,
                )
                burr_3_procedures.append(fiber_implant)
        return burr_3_procedures

    def _map_burr_hole_4(
        self,
        list_item: ClientObject,
    ) -> List[Union[IontophoresisInjection, NanojectInjection, FiberImplant]]:
        """Maps 4th burr hole to Injections and/or FiberImplants"""
        nsb_burr_types = NSBList2023.BurrHoleType
        list_fields = NSBList2023.ListField
        str_helpers = NSBList2023.StringParserHelper
        injection_types = NSBList2023.InjectionType
        burr_4_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_4):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_4).split(
                    str_helpers.BURR_TYPE_SPLITTER
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.BURR4_HEMISPHERE)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_ML)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_AP)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_ANGLE)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR4_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, burr_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, burr_during
        )
        end_date = start_date
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, burr_during
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION:
                injection_type = list_item.get_property(
                    list_fields.INJ4_TYPE
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.BURR4_DV)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ4_VIRUS_STRAIN_RT
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ4_CURRENT)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ4_ALTERNATING_TIME
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ4_IONTO_TIME
                    )
                    injection = IontophoresisInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_current=injection_current,
                        injection_duration=injection_duration,
                        alternating_current=alternating_current,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                else:
                    injection_volume = parse_str_into_float(
                        list_item.get_property(
                            list_fields.INJ4VOLPERDEPTH
                        )
                    )
                    injection = NanojectInjection.construct(
                        start_date=start_date,
                        end_date=end_date,
                        experimenter_full_name=experimenter_full_name,
                        iacuc_protocol=iacuc_protocol,
                        animal_weight_prior=animal_weight_prior,
                        animal_weight_post=animal_weight_post,
                        procedure_type=injection_type,
                        workstation_id=workstation_id,
                        injection_hemisphere=burr_hemisphere,
                        injection_coordinate_ml=burr_coordinate_ml,
                        injection_coordinate_ap=burr_coordinate_ap,
                        injection_coordinate_depth=burr_coordinate_depth,
                        injection_angle=burr_angle,
                        injection_volume=injection_volume,
                        recovery_time=recovery_time,
                        instrument_id=instrument_id,
                        anaesthesia=anaesthesia,
                        bregma_to_lambda_distance=bregma_to_lambda_distance,
                        injection_coordinate_reference=coordinate_reference,
                        injection_materials=injection_materials,
                    )
                burr_4_procedures.append(injection)
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT:
                name = ProbeName.PROBE_D
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT4_D)
                )
                ophys_probe = OphysProbe.construct(
                    name=name,
                    stereotactic_coordinate_ml=burr_coordinate_ml,
                    stereotactic_coordinate_ap=burr_coordinate_ap,
                    stereotactic_coordinate_dv=fiber_implant_depth,
                    angle=burr_angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=coordinate_reference,
                )
                fiber_implant = FiberImplant.construct(
                    start_date=start_date,
                    end_date=end_date,
                    experimenter_full_name=experimenter_full_name,
                    iacuc_protocol=iacuc_protocol,
                    animal_weight_prior=animal_weight_prior,
                    animal_weight_post=animal_weight_post,
                    probes=ophys_probe,
                    anaesthesia=anaesthesia,
                )
                burr_4_procedures.append(fiber_implant)
        return burr_4_procedures

    def _map_list_item_to_craniotomy_2023(
        self,
        list_item: ClientObject,
    ) -> Craniotomy:
        """Maps a SharePoint ListItem to a Craniotomy model"""
        # TODO: missing fields (craniotomy coords,hemisphere)
        list_fields = NSBList2023.ListField
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        craniotomy_type = list_item.get_property(
            list_fields.CRANIOTOMY_TYPE
        )
        craniotomy_size = parse_str_into_float(craniotomy_type)
        craniotomy_during = map_choice(
            list_item.get_property(list_fields.CRANIOTOMY_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, craniotomy_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, craniotomy_during
        )
        end_date = start_date
        workstation_id, recovery_time = self._map_initial_followup_craniotomy(
            list_item, list_fields, craniotomy_during
        )
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, craniotomy_during
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB)
        )
        if craniotomy_type == CraniotomyType.FIVE_MM.value.replace(" ", ""):
            craniotomy_coordinates_reference = (
                CoordinateReferenceLocation.LAMBDA
            )
        else:
            craniotomy_coordinates_reference = None
        craniotomy = Craniotomy.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            craniotomy_type=craniotomy_type,
            craniotomy_size=craniotomy_size,
            anaesthesia=anaesthesia,
            workstation_id=workstation_id,
            recovery_time=recovery_time,
            bregma_to_lambda_distance=bregma_to_lambda_distance,
            craniotomy_coordinates_reference=craniotomy_coordinates_reference,
        )
        return craniotomy

    @staticmethod
    def _map_hp_part_number(headframe_type: str):
        """maps headframe_part_number from headframe_type"""
        headframe_types = NSBList2023.HeadFrameType
        if headframe_type == headframe_types.VISUAL_CTX:
            return "0160-100-10"
        elif headframe_type == headframe_types.WHC_NP:
            return "0160-100-42"
        elif headframe_type == headframe_types.FRONTAL_CTX:
            return "0160-100-46"
        elif headframe_type == headframe_types.MOTOR_CTX:
            return "0160-100-51"
        elif headframe_type == headframe_types.WHC_2P:
            return "0160-100-45"
        else:
            return None

    @staticmethod
    def _map_well_part_number(well_type: str):
        """maps well_part_number from well_type"""
        well_types = NSBList2023.WellType
        if well_type == well_types.CAM:
            return "Rev A"
        elif well_type == well_types.MESOSCOPE:
            return "0160-200-20"
        elif well_type == well_types.NEUROPIXEL:
            return "0160-200-36"
        elif well_type == well_types.WHC_NP:
            return "0160-055-08"
        elif well_type == well_types.WHC_2P:
            return "0160-200-62"
        else:
            return None

    def _map_list_item_to_head_frame_2023(
        self,
        list_item: ClientObject,
    ) -> Headframe:
        """Maps a SharePoint ListItem to a HeadFrame model"""
        list_fields = NSBList2023.ListField
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL
        )
        headframe_type = list_item.get_property(list_fields.HEADPOST)
        headframe_part_number = self._map_hp_part_number(headframe_type)
        well_type = list_item.get_property(list_fields.HEADPOST_TYPE)
        well_part_number = self._map_well_part_number(well_type)
        hp_during = map_choice(
            list_item.get_property(list_fields.HEADPOST_DURING)
        )
        anaesthesia = self._map_2023_anaesthesia(
            list_item, list_fields, hp_during
        )
        start_date = self._map_initial_followup_date(
            list_item, list_fields, hp_during
        )
        end_date = start_date
        (
            animal_weight_prior,
            animal_weight_post,
        ) = self._map_initial_followup_weight(
            list_item, list_fields, hp_during
        )
        head_frame = Headframe.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            headframe_type=headframe_type,
            headframe_part_number=headframe_part_number,
            well_type=well_type,
            well_part_number=well_part_number,
            anaesthesia=anaesthesia,
        )
        return head_frame
