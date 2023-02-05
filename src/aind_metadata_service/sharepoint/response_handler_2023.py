"""Module to handle 2023 sharepoint response and map to procedures"""

from enum import Enum

from aind_data_schema.procedures import (
    Craniotomy,
    FiberImplant,
    Headframe,
    IontophoresisInjection,
)
from dateutil import parser
from office365.runtime.client_object import ClientObject
from office365.sharepoint.listitems.collection import ListItemCollection


class NeurosurgeryAndBehaviorList2023:
    """Class to contain helpful info to parse the 2023 SharePoint List"""

    class StringParserHelper(Enum):
        """Enum class for SharePoint's response strings"""

        # Not really why, but some response fields return 'Select...'
        SELECT_STR = "Select..."
        PROCEDURE_TYPE_SPLITTER = "+"

    class ProcedureCategory(Enum):
        """Enum class for 2023 SharePoint's Procedure Category"""

        HEADPOST_ONLY = "Headpost Only"
        INJECTION = "Injection"
        FIBER_OPTIC_IMPLANT = "Fiber Optic Implant"
        CRANIAL_WINDOW = "Cranial Window"

    class ProcedureType(Enum):
        """Enum class for 2023 SharePoint's Specific Procedure Type"""
        INJECTION = "Injection"
        INJ = "INJ"
        WITH_HEADPOST = "with Headpost"
        FIBER_OPTIC_IMPLANT = "Fiber Optic Implant"
        CTX = "Ctx"
        WHC_NP = "WHC NP"

    class ListField(Enum):
        """Enum class for fields in List Item object response"""

        FILE_SYSTEM_OBJECT_TYPE = "FileSystemObjectType"
        ID = "Id"
        SERVER_REDIRECTED_EMBED_URI = "ServerRedirectedEmbedUri"
        SERVER_REDIRECTED_EMBED_URL = "ServerRedirectedEmbedUrl"
        TITLE = "Title"
        PI_ID = "PIId"
        PI_STRING_ID = "PIStringId"
        LAB_TRACKS_REQUESTOR = "LabTracks_x0020_Requestor"
        PROJECT_ID_TE = "Project_x0020_ID_x0020__x0028_te"
        IACUC_PROTOCOL = "IACUC_x0020_Protocol_x0020__x002"
        DATE_RANGE_START = "DateRangeStart"
        LIGHT_CYCLE = "Light_x0020_Cycle"
        LIMS_REQUIRED = "LIMs_x0020_Required"
        LIMS_PROJECT_CODE = "Lims_x0020_Project_x0020_Code"
        LIM_STASKFLOW1 = "LIMStaskflow1"
        TEST_ID = "Test1Id"
        TEST_STRING_ID = "Test1StringId"
        DATE_OF_SURGERY = "Date_x0020_of_x0020_Surgery"
        HP_WORK_STATION = "HpWorkStation"
        TEST_1ST_ROUND_ID = "TEST_x0020_1st_x0020_Round_x0020Id"
        TEST_1ST_ROUND_STRING_ID = "TEST_x0020_1st_x0020_Round_x0020StringId"
        DATE1ST_INJECTION = "Date1stInjection"
        WORK_STATION1ST_INJECTION = "WorkStation1stInjection"
        LAB_TRACKS_GROUP = "LabTracks_x0020_Group"
        LAB_TRACKS_ID = "LabTracks_x0020_ID1"
        PEDIGREE_NAME = "PedigreeName"
        SEX = "Sex"
        DATE_OF_BIRTH = "Date_x0020_of_x0020_Birth"
        WEIGHT_BEFORE_SURGER = "Weight_x0020_before_x0020_Surger"
        WEIGHT_AFTER_SURGERY = "Weight_x0020_after_x0020_Surgery"
        ISO_ON = "Iso_x0020_On"
        HP_ISO_LEVEL = "HPIsoLevel"
        HP_RECOVERY = "HPRecovery"
        FIRST_INJECTION_WEIGHT_BEFOR = "FirstInjectionWeightBefor"
        FIRST_INJECTION_WEIGHT_AFTER = "FirstInjectionWeightAfter"
        FIRST_INJECTION_ISO_DURATION = "FirstInjectionIsoDuration"
        ROUND1_INJ_ISOLEVEL = "Round1InjIsolevel"
        FIRST_INJ_RECOVERY = "FirstInjRecovery"
        BREG2_LAMB = "Breg2Lamb"
        SURGERY_STATUS = "SurgeryStatus"
        LONG_REQUESTOR_COMMENTS = "LongRequestorComments"
        PROCEDURE_SLOTS = "Procedure_x0020_Slots"
        PROCEDURE_FAMILY = "Procedure_x0020_Family"
        PROCEDURE_T2 = "Procedure_x0020_T2"
        PROCEDURE = "Procedure"
        HEADPOST = "Headpost"
        HEADPOST_TYPE = "HeadpostType"
        CRANIOTOMY_TYPE = "CraniotomyType"
        IMPLANT_ID_COVERSLIP_TYPE = "ImplantIDCoverslipType"
        BURR_HOLE_1 = "Burr_x0020_hole_x0020_1"
        INJ1_VIRUS_STRAIN_RT = "Inj1VirusStrain_rt"
        BURR1_VIRUS_BIOSAFTE = "Burr1_x0020_Virus_x0020_Biosafte"
        INJ1_STORAGE_LOCATION = "Inj1StorageLocation"
        INJ1_TYPE = "Inj1Type"
        VIRUS_HEMISPHERE = "Virus_x0020_Hemisphere"
        INJ1_ANGLE_V2 = "Inj1Angle_v2"
        INJ1VOLPERDEPTH = "inj1volperdepth"
        INJ1_CURRENT = "Inj1Current"
        INJ1_ALTERNATING_TIME = "Inj1AlternatingTime"
        RET_SETTING0 = "retSetting0"
        INJ1_IONTO_TIME = "Inj1IontoTime"
        VIRUS_M_L = "Virus_x0020_M_x002f_L"
        VIRUS_A_P = "Virus_x0020_A_x002f_P"
        VIRUS_D_V = "Virus_x0020_D_x002f_V"
        FIBER_IMPLANT1_LENGT = "Fiber_x0020_Implant1_x0020_Lengt"
        FIBER_IMPLANT1_DV = "FiberImplant1DV"
        BURR_HOLE_2 = "Burr_x0020_hole_x0020_2"
        INJ2_VIRUS_STRAIN_RT = "Inj2VirusStrain_rt"
        BURR2_VIRUS_BIOSAFTE = "Burr2_x0020_Virus_x0020_Biosafte"
        INJ2_STORAGE_LOCATION = "Inj2StorageLocation"
        INJ2_TYPE = "Inj2Type"
        HEMISPHERE2ND_INJ = "Hemisphere2ndInj"
        INJ2_ANGLE_V2 = "Inj2Angle_v2"
        INJ2VOLPERDEPTH = "inj2volperdepth"
        INJ2_CURRENT = "Inj2Current"
        INJ2_ALTERNATING_TIME = "Inj2AlternatingTime"
        RET_SETTING1 = "retSetting1"
        INJ2_IONTO_TIME = "Inj2IontoTime"
        ML2ND_INJ = "ML2ndInj"
        AP2ND_INJ = "AP2ndInj"
        DV2ND_INJ = "DV2ndInj"
        FIBER_IMPLANT2_LENGT = "Fiber_x0020_Implant2_x0020_Lengt"
        FIBER_IMPLANT2_DV = "FiberImplant2DV"
        BURR_HOLE_3 = "Burr_x0020_hole_x0020_3"
        INJ_VIRUS_STRAIN_RT = "InjVirusStrain_rt"
        BURR3_VIRUS_BIOSAFTE = "Burr3_x0020_Virus_x0020_Biosafet"
        INJ3_STORAGE_LOCATION = "Inj3StorageLocation"
        INJ3_TYPE = "Inj3Type"
        BURR3_HEMISPHERE = "Burr_x0020_3_x0020_Hemisphere"
        BURR3_ANGLE = "Burr_x0020_3_x0020_Angle"
        BURR3_AP = "Burr3_x0020_A_x002f_P"
        BURR3_ML = "Burr3_x0020_M_x002f_L"
        BURR3_DV = "Burr3_x0020_D_x002f_V"
        INJ3VOLPERDEPTH = "inj3volperdepth"
        INJ3_CURRENT = "Inj3Current"
        INJ3_ALTERNATING_TIME = "Inj3AlternatingTime"
        INJ3_RET_SETTING = "Inj3retSetting"
        INJ3_IONTO_TIME = "Inj3IontoTime"
        FIBER_IMPLANT3_LENGT = "Fiber_x0020_Implant3_x0020_Lengt"
        FIBER_IMPLANT3_D = "Fiber_x0020_Implant3_x0020_D_x00"
        BURR_HOLE_4 = "Burr_x0020_hole_x0020_4"
        INJ4_VIRUS_STRAIN_RT = "Inj4VirusStrain_rt"
        BURR4_VIRUS_BIOSAFTE = "Burr4_x0020_Virus_x0020_Biosafte"
        INJ4_STORAGE_LOCATION = "Inj4StorageLocation"
        INJ4_TYPE = "Inj4Type"
        BURR4_HEMISPHERE = "Burr_x0020_4_x0020_Hemisphere"
        BURR4_ANGLE = "Burr_x0020_4_x0020_Angle"
        INJ4VOLPERDEPTH = "Inj4volperdepth"
        INJ4_CURRENT = "Inj4Current"
        INJ4_ALTERNATING_TIME = "Inj4AlternatingTime"
        INJ4_RET_SETTING = "Inj4retSetting"
        INJ4_IONTO_TIME = "Inj4IontoTime"
        BURR4_AP = "Burr4_x0020_A_x002f_P"
        BURR4_ML = "Burr4_x0020_M_x002f_L"
        BURR4_DV = "Burr4_x0020_D_x002f_V"
        FIBER_IMPLANT4_LENGT = "Fiber_x0020_Implant4_x0020_Lengt"
        FIBER_IMPLANT4_D = "Fiber_x0020_Implant4_x0020_D_x00"
        COM_DUROTOMY = "ComDurotomy"
        COM_SWELLING = "ComSwelling"
        COM_SINUSBLEED = "ComSinusbleed"
        COM_DAMAGE = "ComDamage"
        COM_WINDOW = "ComWindow"
        COM_COPLANAR = "ComCoplanar"
        CONTUSION = "Contusion"
        IONTO_NUMBER_INJ1 = "IontoNumberInj1"
        NANOJECT_NUMBER_INJ10 = "NanojectNumberInj10"
        IONTO_NUMBER_INJ2 = "IontoNumberInj2"
        NANOJECT_NUMBER_INJ2 = "NanojectNumberInj2"
        HP_SURGEON_COMMENTS = "HPSurgeonComments"
        AGE_AT_INJECTION = "Age_x0020_at_x0020_Injection"
        CONTENT_TYPE_ID = "ContentTypeId"
        COMPLIANCE_ASSET_ID = "ComplianceAssetId"
        CREATED = "Created"
        ID2 = "ID"
        MODIFIED = "Modified"
        AUTHOR_ID = "AuthorId"
        EDITOR_ID = "EditorId"
        ODATA_UI_VERSION_STRING = "OData__UIVersionString"
        ATTACHMENTS = "Attachments"
        GUID = "GUID"


class ResponseHandler2023:
    def handle_response_2023(self, list_items: ListItemCollection,
                              head_frames, injections, fiber_implants, craniotomies):
        """Handles sharepoint response when 2019 version"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        nsb_proc_categories = NeurosurgeryAndBehaviorList2023.ProcedureCategory
        for list_item in list_items:
            if list_item.get_property(list_fields.PROCEDURE.value):
                procedure_category = list_item.get_property(list_fields.PROCEDURE_FAMILY.value)
            else:
                procedure_category = None
            if procedure_category == nsb_proc_categories.HEADPOST_ONLY.value:
                    head_frames.append(
                        self._map_list_item_to_head_frame(list_item)
                    )
            if procedure_category == nsb_proc_categories.CRANIAL_WINDOW.value:
                craniotomies.append(
                    self._map_list_item_to_craniotomy(list_item)
                )
            if procedure_category == nsb_proc_categories.INJECTION.value:
                injections.append(
                    self._map_list_item_to_injection(list_item)
                )
            if procedure_category == nsb_proc_categories.FIBER_OPTIC_IMPLANT.value:
                fiber_implants.append(
                    self._map_list_item_to_fiber_implant(list_item)
                )
            # TODO: map based on specific procedure types
        return head_frames, injections, fiber_implants, craniotomies

    @staticmethod
    def _map_list_item_to_injection(list_item: ClientObject):
        """Maps a SharePoint ClientObject to an Injection model"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        injection = IontophoresisInjection.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
        )
        return injection

    @staticmethod
    def _map_list_item_to_fiber_implant(
            list_item: ClientObject,
    ) -> FiberImplant:
        """Maps a SharePoint ListItem to a FiberImplant model"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        fiber_implant = FiberImplant.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
        )
        return fiber_implant

    @staticmethod
    def _map_list_item_to_craniotomy(
            list_item: ClientObject
    ) -> Craniotomy:
        """Maps a SharePoint ListItem to a Craniotomy model"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        craniotomy = Craniotomy.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
        )
        return craniotomy

    @staticmethod
    def _map_list_item_to_head_frame(
            list_item: ClientObject
    ) -> Headframe:
        """Maps a SharePoint ListItem to a HeadFrame model"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        head_frame = Headframe.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
        )
        return head_frame

