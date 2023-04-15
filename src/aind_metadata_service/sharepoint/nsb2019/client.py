from aind_metadata_service.sharepoint.nsb2019.models import (
    NSBList2019,
    HeadPostInfo,
)
from aind_data_schema.procedures import Headframe, Anaesthetic, Side, CoordinateReferenceLocation, InjectionMaterial
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from dateutil import parser
from typing import Optional
from datetime import date
import re
from dataclasses import dataclass
from enum import Enum


class ListClient:
    def __init__(
        self, client_context: ClientContext, subject_id: str, list_title: str
    ):
        self.subject_id = subject_id
        self.client_context = client_context
        self.list_title = list_title

    def get_list_of_procedures(self):
        subject_procedures = []
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
        for list_item in list_items:
            parsed_nsb_model = NSBList2019.parse_obj(list_item.to_json())
            self._map_nsb_model(parsed_nsb_model)
        return list_items

    def _map_nsb_model(self, nsb_model: NSBList2019):
        procedures = []
        subject_id = self.subject_id
        # lf = NSBList2019.ListField
        start_date = nsb_model.date_of_surgery
        end_date = start_date
        experimenter_full_name = self._map_auth_id_to_exp_name(
            nsb_model.author_id
        )
        iacuc_protocol = nsb_model.iacuc_protocol
        animal_weight_prior = nsb_model.weight_before_surgery
        animal_weight_post = nsb_model.weight_after_surgery
        procedure_types = nsb_model.procedure
        procedure_types = (
            []
            if procedure_types is None
            else procedure_types.split(
                NSBList2019.StringParserHelper.PROCEDURE_TYPE_SPLITTER
            )
        )

        # Check if headframe type procedure in list of procedures
        if (
            NSBList2019.ProcedureType.HP_ONLY in procedure_types
            or NSBList2019.ProcedureType.HP_TRANSCRANIAL in procedure_types
            or NSBList2019.ProcedureType.HEAD_PLANT in procedure_types
        ):
            hf_kwargs = ({
                "start_date": start_date,
                "end_date": end_date,
                "experimenter_full_name": experimenter_full_name,
                "iacuc_protocol": iacuc_protocol,
                "animal_weight_prior": animal_weight_prior,
                "animal_weight_post": animal_weight_post
            })
            headpost_type = nsb_model.get(lf.HEADPOST_TYPE)
            headpost_info = HeadPostInfo.from_headpost_type(
                headpost_type=headpost_type
            )
            hf_kwargs["headframe_type"] = headpost_type.headframe_type
            hf_kwargs["headframe_part_number"] = (
                headpost_info.headframe_part_number
            )
            hf_kwargs["well_type"] = headpost_info.well_type
            hf_kwargs["well_part_number"] = headpost_info.well_part_number
            hp_iso_level = nsb_model.get(lf.HP_ISO_LEVEL)
            anaesthetic_type = "isoflurane"
            anaesthetic = Anaesthetic.construct(
                type=anaesthetic_type,
                level=hp_iso_level,
            )
            hf_kwargs["anaesthesia"] = anaesthetic
            headframe_proc = Headframe.construct(**hf_kwargs)
            procedures.append(headframe_proc)

        # Check if injection type procedure in procedure_types
        if (
            NSBList2019.ProcedureType.STEREOTAXIC_INJECTION_COORDINATE
            in procedure_types
            or NSBList2019.ProcedureType.STEREOTAXIC_INJECTION
            in procedure_types
            or NSBList2019.ProcedureType.INJECTION in procedure_types
            or NSBList2019.ProcedureType.INJ in procedure_types
        ):
            # There could be one or two injections in the sharepoint listitem
            inj1_kwargs = {}
            inj1_start_date = self._map_iso_date_to_date(
                nsb_model.get(lf.DATE1ST_INJECTION)
            )
            inj1_kwargs["start_date"] = inj1_start_date
            inj1_kwargs["end_date"] = inj1_start_date
            inj1_kwargs["animal_weight_prior"] = self._map_float_str_to_float(
                nsb_model.get(lf.FIRST_INJECTION_WEIGHT_BEFOR)
            )
            inj1_kwargs["animal_weight_post"] = self._map_float_str_to_float(
                nsb_model.get(lf.FIRST_INJECTION_WEIGHT_AFTER)
            )
            inj1_kwargs["injection_duration"] = self._map_float_str_to_float(
                nsb_model.get(lf.INJ1_LENGHTOF_TIME)
            )
            # First injection anaesthetic
            inj1_anaesthetic_type = "isoflurane"
            inj1_anaesthetic_duration = self._map_float_str_to_float(
                    nsb_model.get(lf.FIRST_INJECTION_ISO_DURATION)
            )
            inj1_anaesthetic_level = self._map_float_str_to_float(
                nsb_model.get(lf.ROUND1_INJ_ISOLEVEL)
            )
            inj1_kwargs["anaesthesia"] = Anaesthetic.construct(
                type=inj1_anaesthetic_type,
                duration=inj1_anaesthetic_duration,
                level=inj1_anaesthetic_level,
            )
            inj1_kwargs["recovery_time"] = self._map_float_str_to_float(
                nsb_model.get(lf.FIRST_INJ_RECOVERY)
            )
            inj1_kwargs["workstation_id"] = self._filter_select_string(
                nsb_model.get(lf.WORK_STATION1ST_INJECTION)
            )
            inj1_type = nsb_model.get(lf.INJ1_TYPE)
            inj1_kwargs["injection_type"] = inj1_type
            inj1_kwargs["injection_hemisphere"] = self._map_hemisphere(
                nsb_model.get(lf.VIRUS_HEMISPHERE)
            )
            inj1_kwargs["injection_coordinate_ml"] = self._parse_inj_virus_info(
                nsb_model.get(lf.VIRUS_M_L)
            )
            inj1_kwargs["injection_coordinate_ap"] = self._parse_inj_virus_info(
                nsb_model.get(lf.VIRUS_A_P)
            )
            inj1_kwargs["injection_coordinate_reference"] = self._map_ap_info_to_coord_reference(
                nsb_model.get(lf.VIRUS_A_P)
            )
            inj1_kwargs["injection_coordinate_depth"] = self._parse_inj_virus_info(
                nsb_model.get(lf.VIRUS_D_V)
            )
            inj1_kwargs["injection_angle"] = self._parse_angle_str(nsb_model.get(lf.INJ1ANGLE0))
            inj1_kwargs["bregma_to_lambda_distance"] = self._map_float_str_to_float(
                nsb_model.get(lf.BREG2_LAMB)
            )
            inj1_virus_strain = nsb_model.get(lf.INJ1_VIRUS_STRAIN_RT)
            inj1_kwargs["injection_materials"] = None if inj1_virus_strain is None else InjectionMaterial.construct(
                full_genome_name=inj1_virus_strain
            )
            # If injection type is of
            if inj1_type is not None and inj1_type == NSBList2019.InjectionType.IONTO:
                inj1_instrument_id = nsb_model.get(lf.IONTO_NUMBER_INJ1)
            #     inj1_injection_current = parse_str_into_float(
            #     list_item.get_property(list_fields.INJ1_CURRENT)
            # )
                pass


        return None

    @staticmethod
    def _map_auth_id_to_exp_name(
        nsb_author_id: Optional[str],
    ) -> Optional[str]:
        """Maps NSB Author ID to Experimenter name as "NSB" + ID"""
        return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"

    @staticmethod
    def _map_iso_date_to_date(
        nsb_iso_date_str: Optional[str],
    ) -> Optional[date]:
        """Maps NSB date of surgery field to start date"""
        return (
            None
            if nsb_iso_date_str is None
            else parser.isoparse(nsb_iso_date_str)
        )

    @staticmethod
    def _filter_select_string(input: Optional[str]) -> Optional[str]:
        if input is None:
            return None
        elif input in ["Select...", "N/A", "NA"]:
            return None
        else:
            return input

    def _map_float_str_to_float(self, float_str: Optional[str]) -> Optional[float]:
        """This will coerce Optional[str] to Optional[float]"""
        filtered_str = self._filter_select_string(float_str)
        if filtered_str is None:
            return None
        try:
            return float(float_str)
        except ValueError:
            return None

    @staticmethod
    def _map_hemisphere(nsb_hemisphere: Optional[str]) -> Optional[Side]:
        if nsb_hemisphere is None:
            return None
        elif nsb_hemisphere.upper() == Side.LEFT.value.upper():
            return Side.LEFT
        elif nsb_hemisphere.upper() == Side.RIGHT.value.upper():
            return Side.RIGHT
        else:
            return None

    def _parse_inj_virus_info(self, virus_info: Optional[str]) -> Optional[float]:
        """Some fields look like '-3.5, notes' or '3.5, 4.6' """
        filtered_str = self._filter_select_string(virus_info)
        if filtered_str is None:
            return None
        else:
            split_str = filtered_str.split(",")
            return self._map_float_str_to_float(split_str[0])

    @staticmethod
    def _parse_angle_str(angle_info: Optional[str]) -> Optional[float]:
        """Angles look like '30 degrees'"""
        pattern1 = r"^(\d+)\s*(?:degrees)*"
        if angle_info is None or not re.match(pattern1, angle_info):
            return None
        else:
            return float(re.match(pattern1, angle_info).group(1))

    @staticmethod
    def _map_injection_length_of_time(inj_len_of_time_str: Optional[str]) -> Optional[float]:
        """NSB2019 has entries that look like '5' or '3min10sec' etc."""
        pattern1 = r"^(\d)+\s*(?:min)*$"
        pattern2 = r"^(\d+)\s*min\s*(\d+)\s*(?:sec)*"
        if inj_len_of_time_str is None:
            return None
        elif re.match(pattern1, inj_len_of_time_str):
            return float(re.match(pattern1, inj_len_of_time_str).group(1))
        elif re.match(pattern2, inj_len_of_time_str):
            minutes = re.match(pattern2, inj_len_of_time_str).group(1)
            seconds = re.match(pattern2, inj_len_of_time_str).group(2)
            return float(minutes) + float(seconds)/60
        else:
            return None

    @staticmethod
    def _map_ap_info_to_coord_reference(nsb_virus_ap: Optional[str]) -> Optional[CoordinateReferenceLocation]:
        if nsb_virus_ap is None:
            return None
        elif NSBList2019.InjStringParserHelper.ROSTAL_TO_LAMBDA in nsb_virus_ap:
            return CoordinateReferenceLocation.LAMBDA
        else:
            return CoordinateReferenceLocation.BREGMA

    @staticmethod
    def _parse_string_to_float(input_str: Optional[str], regex_pattern: str) -> Optional[float]:
        if input_str is None:
            return None
        else:
            return None
