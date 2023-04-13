from aind_metadata_service.sharepoint.nsb2019.models import NSBList2019
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from dateutil import parser
from typing import Optional
from datetime import date
from dataclasses import dataclass
from enum import Enum


@dataclass
class HeadPostInfo:
    headframe_type: Optional[str] = None
    headframe_part_number: Optional[str]  = None
    well_type: Optional[str] = None
    well_part_number: Optional[str] = None

class NSBHeadPostType(Enum):



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
            f"{NSBList2019.ListField.LAB_TRACKS_ID})"
        )
        list_view = self.client_context.web.lists.get_by_title(
            self.list_title
        ).views.get_by_title(NSBList2019.VIEW_TITLE)
        self.client_context.load(list_view)
        self.client_context.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        self.client_context.load(list_items)
        self.client_context.execute_query()
        for list_item in list_items:
            self._map_list_item(list_item.to_json())
        return list_items

    def _map_list_item(self, list_item: dict):
        subject_id = self.subject_id
        lf = NSBList2019.ListField
        start_date = (
            self._map_date_of_surg_to_start_date(
                list_item.get(lf.DATE_OF_SURGERY)
            )
        )
        end_date = start_date
        experimenter_full_name = (
            self._map_auth_id_to_exp_name(list_item.get(lf.AUTHOR_ID))
        )
        iaucuc_protocol = list_item.get(lf.IACUC_PROTOCOL)
        animal_weight_prior = self._map_float_str_to_float(list_item.get(lf.WEIGHT_BEFORE_SURGER))
        animal_weight_post = self._map_float_str_to_float(list_item.get(lf.WEIGHT_AFTER_SURGERY))
        hp_iso_level = list_item.get(lf.HP_ISO_LEVEL)
        # anaesthesia=
        return None

    @staticmethod
    def _map_auth_id_to_exp_name(nsb_author_id: Optional[str]) -> Optional[str]:
        """Maps NSB Author ID to Experimenter name as "NSB" + ID"""
        return "NSB" if nsb_author_id is None else f"NSB-{nsb_author_id}"

    @staticmethod
    def _map_date_of_surg_to_start_date(nsb_date_of_surg: Optional[str]) -> Optional[date]:
        """Maps NSB date of surgery field to start date"""
        return None if nsb_date_of_surg is None else parser.isoparse(nsb_date_of_surg)

    @staticmethod
    def _map_float_str_to_float(float_str: Optional[str]) -> Optional[float]:
        """This will coerce Optional[str] to Optional[float]"""
        return None if float_str is None else float(float_str)


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
