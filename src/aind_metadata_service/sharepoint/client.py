"""Module to create client to connect to sharepoint database"""

from enum import Enum
from typing import Optional

from aind_data_schema.procedures import (
    Anaesthetic,
    Craniotomy,
    FiberImplant,
    Headframe,
    IontophoresisInjection,
    NanojectInjection,
    Procedures,
)
from dateutil import parser
from fastapi.responses import JSONResponse
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_object import ClientObject
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection

from aind_metadata_service.response_handler import Responses
from aind_metadata_service.sharepoint.utils import (
    convert_str_to_bool,
    convert_str_to_time,
    map_choice,
    map_hemisphere,
    parse_str_into_float,
)


class NeurosurgeryAndBehaviorList2019:
    """Class to contain helpful info to parse the 2019 SharePoint List"""

    class StringParserHelper(Enum):
        """Enum class for SharePoint's response strings"""

        # Not really why, but some response fields return 'Select...'
        SELECT_STR = "Select..."
        PROCEDURE_TYPE_SPLITTER = "+"

    class ProcedureType(Enum):
        """Enum class for SharePoint's Procedure Type"""

        HEAD_PLANT = "HP"
        STEREOTAXIC_INJECTION = "Stereotaxic Injection (Coordinate)"
        INJECTION = "Injection"
        INJ = "INJ"
        OPTIC_FIBER_IMPLANT = "Optic Fiber Implant"
        HP_TRANSCRANIAL = "HP Transcranial (for ISI)"
        WHC_NP = "WHC NP"
        C_CAM = "C CAM"
        C_MULTISCOPE = "C Multiscope"
        C = "C"

    class InjectionType(Enum):
        """Enum class for Injection Types"""

        IONTO = "Iontophoresis"
        NANOJECT = "Nanoject (Pressure)"

    class ListField(Enum):
        """Enum class for fields in List Item object response"""

        FILE_SYSTEM_OBJECT_TYPE = "FileSystemObjectType"
        ID = "Id"
        SERVER_REDIRECTED_EMBED_URI = "ServerRedirectedEmbedUri"
        SERVER_REDIRECTED_EMBED_URL = "ServerRedirectedEmbedUrl"
        CONTENT_TYPE_ID = "ContentTypeId"
        TITLE = "Title"
        PI_ID = "PIId"
        PI_STRING_ID = "PIStringId"
        LAB_TRACKS_REQUESTOR = "LabTracks_x0020_Requestor"
        PROJECT_ID_TE = "Project_x0020_ID_x0020__x0028_te"
        IACUC_PROTOCOL = "IACUC_x0020_Protocol_x0020__x002"
        PROCEDURE = "Procedure"
        LIGHT_CYCLE = "Light_x0020_Cycle"
        LI_MS_REQUIRED = "LIMs_x0020_Required"
        LAB_TRACKS_GROUP = "LabTracks_x0020_Group"
        LAB_TRACKS_ID = "LabTracks_x0020_ID"
        DATE_OF_SURGERY = "Date_x0020_of_x0020_Surgery"
        LIMS_PROJECT_CODE = "Lims_x0020_Project_x0020_Code"
        VIRUS_M_L = "Virus_x0020_M_x002f_L"
        VIRUS_A_P = "Virus_x0020_A_x002f_P"
        VIRUS_D_V = "Virus_x0020_D_x002f_V"
        VIRUS_HEMISPHERE = "Virus_x0020_Hemisphere"
        HP_M_L = "HP_x0020_M_x002f_L"
        HP_A_P = "HP_x0020_A_x002f_P"
        HP_DIAMETER = "HP_x0020_Diameter"
        ISO_ON = "Iso_x0020_On"
        CAGE = "Cage"
        SEX = "Sex"
        DATE_OF_BIRTH = "Date_x0020_of_x0020_Birth"
        WEIGHT_BEFORE_SURGER = "Weight_x0020_before_x0020_Surger"
        WEIGHT_AFTER_SURGERY = "Weight_x0020_after_x0020_Surgery"
        PEDIGREE_NAME = "PedigreeName"
        BREG2_LAMB = "Breg2Lamb"
        HEADPOST_TYPE = "HeadpostType"
        DATE_RANGE_START = "DateRangeStart"
        DATE_RANGE_END = "DateRangeEnd"
        HP_LOC = "HpLoc"
        HP_PERF = "HpPerf"
        HP_DUROTOMY = "HPDurotomy"
        HP_PREV_INJECT = "HpPrevInject"
        ML2ND_INJ = "ML2ndInj"
        AP2ND_INJ = "AP2ndInj"
        DV2ND_INJ = "DV2ndInj"
        HEMISPHERE2ND_INJ = "Hemisphere2ndInj"
        HP_WORK_STATION = "HpWorkStation"
        SURGERY_STATUS = "SurgeryStatus"
        COM_DUROTOMY = "ComDurotomy"
        COM_SWELLING = "ComSwelling"
        COM_SINUSBLEED = "ComSinusbleed"
        COM_DURING1ST_INJ = "ComDuring1stInj"
        COM_DURING2ND_INJ = "ComDuring2ndInj"
        COM_DAMAGE = "ComDamage"
        COM_WINDOW = "ComWindow"
        COM_COPLANAR = "ComCoplanar"
        COM_AFTER1ST_INJ = "ComAfter1stInj"
        COM_AFTER2ND_INJ = "ComAfter2ndInj"
        WORK_STATION1ST_INJECTION = "WorkStation1stInjection"
        WORK_STATION2ND_INJECTION = "WorkStation2ndInjection"
        DATE1ST_INJECTION = "Date1stInjection"
        DATE2ND_INJECTION = "Date2ndInjection"
        INJ1_STORAGE_LOCATION = "Inj1StorageLocation"
        INJ2_STORAGE_LOCATION = "Inj2StorageLocation"
        INJ1_TYPE = "Inj1Type"
        INJ2_TYPE = "Inj2Type"
        INJ1_VOL = "Inj1Vol"
        INJ2_VOL = "Inj2Vol"
        INJ1_LENGHTOF_TIME = "Inj1LenghtofTime"
        INJ2_LENGHTOF_TIME = "Inj2LenghtofTime"
        INJ1_CURRENT = "Inj1Current"
        INJ2_CURRENT = "Inj2Current"
        INJ1_ALTERNATING_TIME = "Inj1AlternatingTime"
        INJ2_ALTERNATING_TIME = "Inj2AlternatingTime"
        FIRST_INJECTION_WEIGHT_BEFOR = "FirstInjectionWeightBefor"
        FIRST_INJECTION_WEIGHT_AFTER = "FirstInjectionWeightAfter"
        FIRST_INJECTION_ISO_DURATION = "FirstInjectionIsoDuration"
        SECOND_INJECTION_WEIGHT_BEFORE = "SecondInjectionWeightBefore"
        SECOND_INJECTION_WEIGHT_AFTER = "SecondInjectionWeightAfter"
        SECOND_INJECTION_ISO_DURATION = "SecondInjectionIsoDuration"
        INJ1_ROUND = "Inj1Round"
        INJ2_ROUND = "Inj2Round"
        HP_ISO_LEVEL = "HPIsoLevel"
        ROUND1_INJ_ISOLEVEL = "Round1InjIsolevel"
        ROUND2_INJ_ISOLEVEL = "Round2InjIsolevel"
        TEST1_ID = "Test1Id"
        TEST1_STRING_ID = "Test1StringId"
        TEST_2ND_ROUND_ID = "TEST_x0020_2nd_x0020_Round_x0020Id"
        TEST_2ND_ROUND_STRING_ID = "TEST_x0020_2nd_x0020_Round_x0020StringId"
        TEST_1ST_ROUND_ID = "TEST_x0020_1st_x0020_Round_x0020Id"
        TEST_1ST_ROUND_STRING_ID = "TEST_x0020_1st_x0020_Round_x0020StringId"
        ODATA_HP_REQUESTOR = "OData__x0031_HP_x0020_Requestor_x0020_"
        ISSUE = "Issue"
        TOUCH_UP_STATUS = "Touch_x0020_Up_x0020_Status"
        TOUCH_UP_SURGEON_ID = "Touch_x0020_Up_x0020_SurgeonId"
        TOUCH_UP_SURGEON_STRING_ID = "Touch_x0020_Up_x0020_SurgeonStringId"
        TOUCH_UP_COMP = "Touch_x0020_Up_x0020__x0020_Comp"
        EXUDATE_SEVERITY = "Exudate_x0020_Severity"
        SCABBING = "Scabbing"
        EYE_ISSUE = "Eye_x0020_Issue"
        EYE_AFFECTED = "Eye_x0020_Affected"
        TOUCH_UP_WEIGHT = "Touch_x0020_Up_x0020_Weight_x002"
        LIMS_LINK = "LIMS_x0020_link"
        HP_INJ = "HP_x0020__x0026__x0020_Inj"
        FIELD30 = "field30"
        FIELD50 = "field50"
        LIM_STASKFLOW1 = "LIMStaskflow1"
        COMPLIANCE_ASSET_ID = "ComplianceAssetId"
        CREATED = "Created"
        AUTHOR_ID = "AuthorId"
        EDITOR_ID = "EditorId"
        MODIFIED = "Modified"
        HP_REQUESTOR_COMMENTS_PLAINTEXT = "HPRequestorCommentsPlaintext"
        NANOJECT_NUMBER_INJ2 = "NanojectNumberInj2"
        NANOJECT_NUMBER_INJ10 = "NanojectNumberInj10"
        IONTO_NUMBER_INJ1 = "IontoNumberInj1"
        IONTO_NUMBER_INJ2 = "IontoNumberInj2"
        IONTO_NUMBER_HPINJ = "IontoNumberHPINJ"
        INJ1VOLPERDEPTH = "inj1volperdepth"
        INJ2VOLPERDEPTH = "inj2volperdepth"
        INJ1ANGLE0 = "Inj1angle0"
        INJ2ANGLE0 = "Inj2angle0"
        CONTUSION = "Contusion"
        HP_SURGEON_COMMENTS = "HPSurgeonComments"
        ST_ROUND_INJECTION_COMMENTS = "stRoundInjectionComments"
        ND_ROUNG_INJECTION_COMMENTS = "ndRoungInjectionComments"
        FIRST_ROUND_IONTO_ISSUE = "FirstRoundIontoIssue"
        HP_RECOVERY = "HPRecovery"
        FIRST_INJ_RECOVERY = "FirstInjRecovery"
        SECOND_INJ_RECOVER = "SecondInjRecover"
        SECOND_ROUND_IONTO_ISSUE = "SecondRoundIontoIssue"
        LONG_SURGEON_COMMENTS = "LongSurgeonComments"
        LONG1ST_ROUND_INJ_CMTS = "Long1stRoundInjCmts"
        LONG2ND_RND_INJ_CMTS = "Long2ndRndInjCmts"
        LONG_REQUESTOR_COMMENTS = "LongRequestorComments"
        INJ1_VIRUS_STRAIN_RT = "Inj1VirusStrain_rt"
        INJ2_VIRUS_STRAIN_RT = "Inj2VirusStrain_rt"
        RET_SETTING0 = "retSetting0"
        RET_SETTING1 = "retSetting1"
        START_OF_WEEK = "Start_x0020_Of_x0020_Week"
        END_OF_WEEK = "End_x0020_of_x0020_Week"
        AGE_AT_INJECTION = "Age_x0020_at_x0020_Injection"
        CRANIOTOMY_TYPE = "CraniotomyType"
        IMPLANT_ID_COVERSLIP_TYPE = "ImplantIDCoverslipType"
        INJ1_ANGLE_V2 = "Inj1Angle_v2"
        INJ2_ANGLE_V2 = "Inj2Angle_v2"
        FIBER_IMPLANT1 = "FiberImplant1"
        FIBER_IMPLANT1_DV = "FiberImplant1DV"
        FIBER_IMPLANT2 = "FiberImplant2"
        FIBER_IMPLANT2_DV = "FiberImplant2DV"
        ID2 = "ID"  # For some reason ID and Id are present in response
        ODATA_UI_VERSION_STRING = "OData__UIVersionString"
        ATTACHMENTS = "Attachments"
        GUID = "GUID"


class ListVersions(Enum):
    """Enum class to handle different SharePoint list versions."""

    VERSION_2019 = {
        "list_title": "SWR 2019-Present",
        "view_title": "New Request",
    }
    DEFAULT = {"list_title": "SWR 2019-Present", "view_title": "New Request"}


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
          Which version of the backend is being queried
        subject_id : str
          ID of the subject being queried for

        Returns
        -------
        str
          A string to pass into a query filter

        """
        default = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2019.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        version_2019 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2019.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        # TODO: Handle other versions
        filter_string = default
        if version == ListVersions.VERSION_2019:
            filter_string = version_2019
        return filter_string

    def get_procedure_info(
        self,
        subject_id: str,
        version: ListVersions = ListVersions.VERSION_2019,
    ) -> JSONResponse:
        """
        Primary interface. Maps a subject_id to a response.
        Parameters
        ----------
        subject_id : str
          ID of the subject being queried for.
        version : ListVersions
          Version of the SharePoint List being queried against

        Returns
        -------
        JSONResponse
          A response

        """
        # TODO: Add try to handle internal server error response.
        filter_string = self._get_filter_string(version, subject_id)
        ctx = self.client_context
        list_view = ctx.web.lists.get_by_title(
            version.value["list_title"]
        ).views.get_by_title(version.value["view_title"])
        ctx.load(list_view)
        ctx.execute_query()
        list_items = list_view.get_items().filter(filter_string)
        ctx.load(list_items)
        ctx.execute_query()
        response = self._handle_response_from_sharepoint(
            list_items, subject_id=subject_id
        )

        return response

    # TODO: Refactor to make less complex?
    def _handle_response_from_sharepoint(  # noqa: C901
        self, list_items: ListItemCollection, subject_id: str
    ) -> JSONResponse:
        """
        Maps the response from SharePoint into a Procedures model
        Parameters
        ----------
        list_items : ListItemCollection
          SharePoint returns a ListItemCollection given a query
        subject_id : str
          ID of the subject being queried for.

        Returns
        -------
        JSONResponse
          Either a Procedures model or an error response

        """
        if list_items:
            list_fields = NeurosurgeryAndBehaviorList2019.ListField
            str_helpers = NeurosurgeryAndBehaviorList2019.StringParserHelper
            nsb_proc_types = NeurosurgeryAndBehaviorList2019.ProcedureType
            procedures = Procedures.construct(subject_id=subject_id)
            head_frames = []
            injections = []
            fiber_implants = []
            craniotomies = []
            for list_item in list_items:
                if list_item.get_property(list_fields.PROCEDURE.value):
                    procedure_types = list_item.get_property(
                        list_fields.PROCEDURE.value
                    ).split(str_helpers.PROCEDURE_TYPE_SPLITTER.value)
                else:
                    procedure_types = []
                for procedure_type in procedure_types:
                    if procedure_type == nsb_proc_types.HEAD_PLANT.value:
                        head_frames.append(
                            self._map_list_item_to_head_frame(list_item)
                        )
                    if procedure_type in {
                        nsb_proc_types.STEREOTAXIC_INJECTION.value,
                        nsb_proc_types.INJECTION.value,
                        nsb_proc_types.INJ.value,
                    }:
                        injections.append(
                            self._map_list_item_to_injection(list_item)
                        )
                    if (
                        procedure_type
                        == nsb_proc_types.OPTIC_FIBER_IMPLANT.value
                    ):
                        fiber_implants.append(
                            self._map_list_item_to_fiber_implant(list_item)
                        )
                    if procedure_type in {
                        nsb_proc_types.WHC_NP.value,
                        nsb_proc_types.C_MULTISCOPE.value,
                        nsb_proc_types.C_CAM.value,
                        nsb_proc_types.C.value,
                    }:
                        craniotomies.append(
                            self._map_list_item_to_craniotomy(list_item)
                        )
                if head_frames:
                    procedures.headframes = head_frames
                if injections:
                    procedures.injections = injections
                if fiber_implants:
                    procedures.fiber_implants = fiber_implants
                if craniotomies:
                    procedures.craniotomies = craniotomies
            response = Responses.model_response(procedures)
        else:
            response = Responses.no_data_found_response()
        return response

    @staticmethod
    def _map_injection_anaesthesia(list_item) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for Injection"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        anaesthetic_type = "isoflurane"
        duration = list_item.get_property(
            list_fields.FIRST_INJECTION_ISO_DURATION.value
        )
        level = list_item.get_property(list_fields.ROUND1_INJ_ISOLEVEL.value)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            duration=duration,
            level=level,
        )
        return anaesthetic

    def _map_list_item_to_injection(self, list_item: ClientObject):
        """Maps a SharePoint ClientObject to an Injection model"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight = list_item.get_property(
            list_fields.WEIGHT_BEFORE_SURGER.value
        )
        # TODO: all fields after this have diff field names for 2nd inj
        anaesthesia = self._map_injection_anaesthesia(list_item)
        injection_duration = convert_str_to_time(
            list_item.get_property(list_fields.INJ1_LENGHTOF_TIME.value)
        )
        recovery_time = list_item.get_property(
            list_fields.FIRST_INJ_RECOVERY.value
        )
        workstation_id = list_item.get_property(
            list_fields.WORK_STATION1ST_INJECTION.value
        )
        injection_type = list_item.get_property(list_fields.INJ1_TYPE.value)
        injection_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.VIRUS_HEMISPHERE.value)
        )
        injection_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_M_L.value)
        )
        # TODO: handle direction for coordinate ap
        injection_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_A_P.value)
        )
        # TODO: handle 2 values for depth (for now using 1st value)
        injection_coordinate_depth = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_D_V.value)
        )
        injection_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ1ANGLE0.value)
        )
        if (
            injection_type
            == NeurosurgeryAndBehaviorList2019.InjectionType.IONTO.value
        ):
            instrument_id = list_item.get_property(
                list_fields.IONTO_NUMBER_INJ1.value
            )
            injection_current = list_item.get_property(
                list_fields.INJ1_CURRENT.value
            )
            alternating_current = list_item.get_property(
                list_fields.INJ1_ALTERNATING_TIME.value
            )
            injection = IontophoresisInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight=animal_weight,
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
            )
        else:
            instrument_id = list_item.get_property(
                list_fields.NANOJECT_NUMBER_INJ10.value
            )
            injection_volume = list_item.get_property(
                list_fields.INJ1_VOL.value
            )
            injection = NanojectInjection.construct(
                start_date=start_date,
                end_date=end_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight=animal_weight,
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
            )
        return injection

    @staticmethod
    def _map_list_item_to_fiber_implant(
        list_item: ClientObject,
    ) -> FiberImplant:
        """Maps a SharePoint ListItem to a FiberImplant model"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = list_item.get_property(list_fields.DATE_RANGE_START.value)
        end_date = list_item.get_property(list_fields.DATE_RANGE_END.value)
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
    def _map_hp_anaesthesia(list_item, list_fields) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for HP/craniotomy"""
        anaesthetic_type = "isoflurane"
        # TODO: duration
        level = list_item.get_property(list_fields.HP_ISO_LEVEL.value)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            level=level,
        )
        return anaesthetic

    def _map_list_item_to_craniotomy(
        self, list_item: ClientObject
    ) -> Craniotomy:
        """Maps a SharePoint ListItem to a Craniotomy model"""
        # TODO: missing fields (implant_part_number, protective_material)
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = parser.isoparse(
            list_item.get_property(list_fields.DATE_OF_SURGERY.value)
        ).date()
        end_date = start_date
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight = list_item.get_property(
            list_fields.WEIGHT_BEFORE_SURGER.value
        )
        anaesthesia = self._map_hp_anaesthesia(list_item, list_fields)
        craniotomy_type = list_item.get_property(
            list_fields.CRANIOTOMY_TYPE.value
        )
        # TODO: handle size and coords by craniotomy_type ?
        craniotomy_hemisphere = map_choice(
            list_item.get_property(list_fields.HP_LOC.value)
        )
        craniotomy_coordinates_ml = parse_str_into_float(
            list_item.get_property(list_fields.HP_M_L.value)
        )
        craniotomy_coordinates_ap = parse_str_into_float(
            list_item.get_property(list_fields.HP_A_P.value)
        )
        craniotomy_size = parse_str_into_float(
            list_item.get_property(list_fields.HP_DIAMETER.value)
        )
        dura_removed = convert_str_to_bool(
            list_item.get_property(list_fields.HP_DUROTOMY.value)
        )
        workstation_id = list_item.get_property(
            list_fields.HP_WORK_STATION.value
        )
        craniotomy = Craniotomy.construct(
            type=craniotomy_type,
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
            iacuc_protocol=iacuc_protocol,
            animal_weight=animal_weight,
            anaesthesia=anaesthesia,
            craniotomy_hemisphere=craniotomy_hemisphere,
            craniotomy_coordinates_ml=craniotomy_coordinates_ml,
            craniotomy_coordinates_ap=craniotomy_coordinates_ap,
            craniotomy_size=craniotomy_size,
            dura_removed=dura_removed,
            workstation_id=workstation_id,
        )
        return craniotomy

    @staticmethod
    def _map_list_item_to_head_frame(list_item: ClientObject) -> Headframe:
        """Maps a SharePoint ListItem to a HeadFrame model"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = list_item.get_property(list_fields.DATE_RANGE_START.value)
        end_date = list_item.get_property(list_fields.DATE_RANGE_END.value)
        experimenter_full_name = list_item.get_property(
            list_fields.LAB_TRACKS_REQUESTOR.value
        )
        head_frame = Headframe.construct(
            start_date=start_date,
            end_date=end_date,
            experimenter_full_name=experimenter_full_name,
        )
        return head_frame
