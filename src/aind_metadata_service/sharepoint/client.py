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
from aind_metadata_service.sharepoint.utils import (
    convert_hour_to_mins,
    convert_str_to_bool,
    map_choice,
    map_date_to_datetime,
    map_hemisphere,
    parse_str_into_float,
)


class NeurosurgeryAndBehaviorList2023:
    """Class to contain helpful info to parse the 2023 SharePoint List"""

    class StringParserHelper(Enum):
        """Enum class for SharePoint's response strings"""

        # Not really why, but some response fields return 'Select...'
        SELECT_STR = "Select..."
        PROCEDURE_TYPE_SPLITTER = "+"
        WITH_HEADPOST = " (with Headpost)"
        BURR_TYPE_SPLITTER = "&"

    class ProcedureType(Enum):
        """Enum class for 2023 SharePoint's Specific Procedure Type"""

        STEREOTAXIC_INJECTION = "Stereotaxic Injection"
        ISI_INJECTION = "ISI-guided Injection"
        FIBER_OPTIC_IMPLANT = "Fiber Optic Implant"
        INJECTION = "Injection"
        INJ = "INJ"
        WITH_HEADPOST = "with Headpost"
        WHC_NP = "WHC NP"
        HP_ONLY = "HP Only"
        HP_TRANSCRANIAL = "HP Transcranial"
        VISUAL_CTX_2P = "Visual Ctx 2P"
        FRONTAL_CTX_2P = "Frontal Ctx 2P"
        MOTOR_CTX = "Motor Ctx"
        VISUAL_CTX_NP = "Visual Ctx NP"
        INJECTION_FIBER_IMPLANT = "Injection+Fiber Optic Implant"

    class BurrHoleType(Enum):
        """Enum class for 2023 SharePoint's BurrHole Procedures"""

        INJECTION = "Injection"
        FIBER_IMPLANT = "Fiber Implant"
        INJECTION_FIBER_IMPLANT = "Injection & Fiber Implant"

    class InjectionType(Enum):
        """Enum class of Injection Types"""

        IONTO = "Iontophoresis"
        NANOJECT = "Nanoject (Pressure)"

    class HeadFrameType(Enum):
        """Enum class for Headframe Types"""

        VISUAL_CTX = "Visual Ctx"
        FRONTAL_CTX = "Frontal Ctx"
        MOTOR_CTX = "Motor Ctx"
        WHC_2P = "WHC 2P"
        WHC_NP = "WHC NP"
        AI_STRAIGHT_BAR = "AI Straight bar"
        OTHER = "Other"

    class WellType(Enum):
        """Enum class for Well Types"""

        NO_WELL = "No Well"
        CAM = "Scientifica (CAM)"
        MESOSCOPE = "Mesoscope"
        NEUROPIXEL = "Neuropixel"
        WHC_2P = "WHC 2P"
        WHC_NP = "WHC NP"
        OTHER = "Other"

    class SurgeryOrder(Enum):
        """Enum class for Initial/FollowUp classifiers"""

        INITIAL = "Initial Surgery"
        SECOND = "Follow up Surgery"

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
        BURR1_DURING = "Burr1_x0020_Perform_x0020_During"
        BURR2_DURING = "Burr2_x0020_Perform_x0020_During"
        BURR3_DURING = "Burr3_x0020_Perform_x0020_During"
        BURR4_DURING = "Burr4_x0020_Perform_x0020_During"
        HEADPOST_DURING = "Headpost_x0020_Perform_x0020_Dur"
        CRANIOTOMY_DURING = "Craniotomy_x0020_Perform_x0020_D"


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
        HP_ONLY = "HP Only"
        HP_TRANSCRANIAL = "HP Transcranial (for ISI)"
        STEREOTAXIC_INJECTION_COORDINATE = "Stereotaxic Injection (Coordinate)"
        STEREOTAXIC_INJECTION = "Stereotaxic Injection"
        INJECTION = "Injection"
        INJ = "INJ"
        OPTIC_FIBER_IMPLANT = "Optic Fiber Implant"
        WHOLE_HEMISPHERE_CRANIOTOMY_NP = "WHC NP"
        C_CAM = "C CAM"
        C_MULTISCOPE = "C Multiscope"
        C = "C"

    class InjectionType(Enum):
        """Enum class for Injection Types"""

        IONTO = "Iontophoresis"
        NANOJECT = "Nanoject (Pressure)"

    class CraniotomyType(Enum):
        """Enum class for Craniotomy Types"""

        VISUAL_CORTEX = "Visual Cortex 5mm"
        FRONTAL_WINDOW = "Frontal Window 3mm"
        WHC_NP = "WHC NP"
        WHC_2P = "WHC 2P"

    class HeadPostType(Enum):
        """Enum class for HeadPost Types"""

        CAM = "CAM-style headframe (0160-100-10 Rev A)"
        NEUROPIXEL = "Neuropixel-style headframe (0160-100-10/0160-200-36)"
        MESO_NGC = (
            "Mesoscope-style well with NGC-style headframe"
            " (0160-200-20/0160-100-10)"
        )
        WHC_NP = "WHC #42 with Neuropixel well and well cap"
        NGC = "NGC-style headframe, no well (0160-100-10)"
        AI_HEADBAR = "AI Straight Headbar"

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
            f"{NeurosurgeryAndBehaviorList2019.ListField.LAB_TRACKS_ID.value}"
            f")"
        )
        version_2023 = (
            f"substringof("
            f"'{subject_id}', "
            f"{NeurosurgeryAndBehaviorList2023.ListField.LAB_TRACKS_ID.value}"
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
                version.value["list_title"]
            ).views.get_by_title(version.value["view_title"])
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
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        subject_procedures = []
        str_helpers = NeurosurgeryAndBehaviorList2023.StringParserHelper
        nsb_proc_types = NeurosurgeryAndBehaviorList2023.ProcedureType
        for list_item in list_items:
            if list_item.get_property(list_fields.PROCEDURE.value):
                procedure = list_item.get_property(list_fields.PROCEDURE.value)
                procedure_types = []
                if str_helpers.WITH_HEADPOST.value in procedure:
                    procedure = procedure.replace(
                        str_helpers.WITH_HEADPOST.value, ""
                    )
                    procedure_types.append(nsb_proc_types.WITH_HEADPOST.value)
                if procedure != nsb_proc_types.INJECTION_FIBER_IMPLANT.value:
                    procedure_types.extend(
                        procedure.split(
                            str_helpers.PROCEDURE_TYPE_SPLITTER.value
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
                    nsb_proc_types.WITH_HEADPOST.value,
                    nsb_proc_types.HP_ONLY.value,
                    nsb_proc_types.HP_TRANSCRANIAL.value,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_head_frame_2023(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.VISUAL_CTX_NP.value,
                    nsb_proc_types.VISUAL_CTX_2P.value,
                    nsb_proc_types.FRONTAL_CTX_2P.value,
                    nsb_proc_types.MOTOR_CTX.value,
                    nsb_proc_types.WHC_NP.value,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_craniotomy_2023(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.INJECTION.value,
                    nsb_proc_types.STEREOTAXIC_INJECTION.value,
                    nsb_proc_types.INJ.value,
                    nsb_proc_types.ISI_INJECTION.value,
                    nsb_proc_types.FIBER_OPTIC_IMPLANT.value,
                    nsb_proc_types.INJECTION_FIBER_IMPLANT.value,
                }:
                    subject_procedures.extend(self._map_burr_holes(list_item))
        return subject_procedures

    def _map_2019_response(self, list_items: ListItemCollection) -> list:
        """Maps sharepoint response when 2019 version"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        str_helpers = NeurosurgeryAndBehaviorList2019.StringParserHelper
        nsb_proc_types = NeurosurgeryAndBehaviorList2019.ProcedureType
        subject_procedures = []
        for list_item in list_items:
            if list_item.get_property(list_fields.PROCEDURE.value):
                procedure_types = list_item.get_property(
                    list_fields.PROCEDURE.value
                ).split(str_helpers.PROCEDURE_TYPE_SPLITTER.value)
            else:
                procedure_types = []
                subject_procedures.append(
                    self._map_list_item_to_subject_procedure(list_item)
                )
            for procedure_type in procedure_types:
                if procedure_type in {
                    nsb_proc_types.HEAD_PLANT.value,
                    nsb_proc_types.HP_ONLY.value,
                    nsb_proc_types.HP_TRANSCRANIAL.value,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_head_frame(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.STEREOTAXIC_INJECTION_COORDINATE.value,
                    nsb_proc_types.STEREOTAXIC_INJECTION.value,
                    nsb_proc_types.INJECTION.value,
                    nsb_proc_types.INJ.value,
                }:
                    subject_procedures.extend(
                        self._map_list_item_to_injections(list_item)
                    )
                if procedure_type == nsb_proc_types.OPTIC_FIBER_IMPLANT.value:
                    subject_procedures.append(
                        self._map_list_item_to_fiber_implant(list_item)
                    )
                if procedure_type in {
                    nsb_proc_types.WHOLE_HEMISPHERE_CRANIOTOMY_NP.value,
                    nsb_proc_types.C_MULTISCOPE.value,
                    nsb_proc_types.C_CAM.value,
                    nsb_proc_types.C.value,
                }:
                    subject_procedures.append(
                        self._map_list_item_to_craniotomy(list_item)
                    )
        return subject_procedures

    def _map_list_item_to_subject_procedure(
        self, list_item: ClientObject
    ) -> SubjectProcedure:
        """Maps a Sharepoint ClientObject to generic SubjectProcedure model"""
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER.value)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY.value)
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
    def _map_experimenter_name(list_item: ClientObject, list_fields) -> str:
        """Maps Experimenter name as "NSB" + ID"""
        author_id = list_item.get_property(list_fields.AUTHOR_ID.value)
        if author_id:
            return "NSB-" + str(author_id)
        else:
            return "NSB"

    @staticmethod
    def _map_1st_injection_anaesthesia(
        list_item: ClientObject, list_fields
    ) -> Optional[Anaesthetic]:
        """Maps anaesthesic type, duration, level for Injection"""
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
            list_item.get_property(list_fields.DATE1ST_INJECTION.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(
                list_fields.FIRST_INJECTION_WEIGHT_BEFOR.value
            )
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(
                list_fields.FIRST_INJECTION_WEIGHT_AFTER.value
            )
        )
        anaesthesia = self._map_1st_injection_anaesthesia(
            list_item, list_fields
        )
        injection_duration = parse_str_into_float(
            list_item.get_property(list_fields.INJ1_LENGHTOF_TIME.value)
        )
        recovery_time = list_item.get_property(
            list_fields.FIRST_INJ_RECOVERY.value
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.WORK_STATION1ST_INJECTION.value)
        )
        injection_type = list_item.get_property(list_fields.INJ1_TYPE.value)
        injection_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.VIRUS_HEMISPHERE.value)
        )
        injection_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_M_L.value)
        )
        injection_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_A_P.value)
        )
        injection_coordinate_reference = self._map_inj_coordinate_reference(
            list_item.get_property(list_fields.VIRUS_A_P.value)
        )
        # TODO: handle 2 values for depth (for now using 1st value)
        injection_coordinate_depth = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_D_V.value)
        )
        injection_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ1ANGLE0.value)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        full_genome_name = list_item.get_property(
            list_fields.INJ1_VIRUS_STRAIN_RT.value
        )
        injection_materials = self._map_injection_materials(full_genome_name)
        if (
            injection_type
            == NeurosurgeryAndBehaviorList2019.InjectionType.IONTO.value
        ):
            instrument_id = list_item.get_property(
                list_fields.IONTO_NUMBER_INJ1.value
            )
            injection_current = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_CURRENT.value)
            )
            alternating_current = list_item.get_property(
                list_fields.INJ1_ALTERNATING_TIME.value
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
                list_fields.NANOJECT_NUMBER_INJ10.value
            )
            injection_volume = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_VOL.value)
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
            list_fields.FIRST_INJECTION_ISO_DURATION.value
        )
        level = list_item.get_property(list_fields.ROUND2_INJ_ISOLEVEL.value)
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
            list_item.get_property(list_fields.DATE2ND_INJECTION.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(
                list_fields.SECOND_INJECTION_WEIGHT_BEFORE.value
            )
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(
                list_fields.SECOND_INJECTION_WEIGHT_AFTER.value
            )
        )
        anaesthesia = self._map_2nd_injection_anaesthesia(
            list_item, list_fields
        )
        injection_duration = parse_str_into_float(
            list_item.get_property(list_fields.INJ2_LENGHTOF_TIME.value)
        )
        recovery_time = list_item.get_property(
            list_fields.SECOND_INJ_RECOVER.value
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.WORK_STATION2ND_INJECTION.value)
        )
        injection_type = list_item.get_property(list_fields.INJ2_TYPE.value)
        injection_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.HEMISPHERE2ND_INJ.value)
        )
        injection_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.ML2ND_INJ.value)
        )
        injection_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.AP2ND_INJ.value)
        )
        injection_coordinate_reference = self._map_inj_coordinate_reference(
            list_item.get_property(list_fields.AP2ND_INJ.value)
        )
        # TODO: handle 2 values for depth (for now using 1st value)
        injection_coordinate_depth = parse_str_into_float(
            list_item.get_property(list_fields.DV2ND_INJ.value)
        )
        injection_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ2ANGLE0.value)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        full_genome_name = list_item.get_property(
            list_fields.INJ2_VIRUS_STRAIN_RT.value
        )
        injection_materials = self._map_injection_materials(full_genome_name)
        if (
            injection_type
            == NeurosurgeryAndBehaviorList2019.InjectionType.IONTO.value
        ):
            instrument_id = list_item.get_property(
                list_fields.IONTO_NUMBER_INJ2.value
            )
            injection_current = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_CURRENT.value)
            )
            alternating_current = list_item.get_property(
                list_fields.INJ2_ALTERNATING_TIME.value
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
                list_fields.NANOJECT_NUMBER_INJ2.value
            )
            injection_volume = parse_str_into_float(
                list_item.get_property(list_fields.INJ2_VOL.value)
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
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        injection_1 = self._map_1st_injection(list_item, list_fields)
        injections.append(injection_1)
        # check if there's a 2nd injection in list item
        inj2round = list_item.get_property(list_fields.INJ2_ROUND.value)
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
            list_fields.FIBER_IMPLANT1.value
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        if fiber_implant1:
            name = ProbeName.PROBE_A.value
            stereotactic_coordinate_ml = parse_str_into_float(
                list_item.get_property(list_fields.VIRUS_M_L.value)
            )
            stereotactic_coordinate_ap = parse_str_into_float(
                list_item.get_property(list_fields.VIRUS_A_P.value)
            )
            coordinate_reference = self._map_inj_coordinate_reference(
                list_item.get_property(list_fields.VIRUS_A_P.value)
            )
            stereotactic_coordinate_dv = parse_str_into_float(
                list_item.get_property(list_fields.FIBER_IMPLANT1_DV.value)
            )
            angle = parse_str_into_float(
                list_item.get_property(list_fields.INJ1_ANGLE_V2.value)
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
            list_fields.FIBER_IMPLANT2.value
        )
        if fiber_implant2:
            name = ProbeName.PROBE_B.value
            stereotactic_coordinate_ml = parse_str_into_float(
                list_item.get_property(list_fields.ML2ND_INJ.value)
            )
            stereotactic_coordinate_ap = parse_str_into_float(
                list_item.get_property(list_fields.AP2ND_INJ.value)
            )
            coordinate_reference = self._map_inj_coordinate_reference(
                list_item.get_property(list_fields.AP2ND_INJ.value)
            )
            stereotactic_coordinate_dv = parse_str_into_float(
                list_item.get_property(list_fields.FIBER_IMPLANT2_DV.value)
            )
            angle = parse_str_into_float(
                list_item.get_property(list_fields.INJ2_ANGLE_V2.value)
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
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER.value)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY.value)
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
        level = list_item.get_property(list_fields.HP_ISO_LEVEL.value)
        anaesthetic = Anaesthetic.construct(
            type=anaesthetic_type,
            level=level,
        )
        return anaesthetic

    @staticmethod
    def _map_craniotomy_type(sp_craniotomy_type) -> Optional[CraniotomyType]:
        """Maps craniotomy type"""
        CT = NeurosurgeryAndBehaviorList2019.CraniotomyType
        if sp_craniotomy_type:
            if sp_craniotomy_type == CT.VISUAL_CORTEX.value:
                return CraniotomyType.VISCTX
            elif sp_craniotomy_type == CT.FRONTAL_WINDOW.value:
                return CraniotomyType.THREE_MM
            elif sp_craniotomy_type in {
                CT.WHC_NP.value,
                CT.WHC_2P.value,
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
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER.value)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY.value)
        )
        anaesthesia = self._map_hp_anaesthesia(list_item, list_fields)
        craniotomy_type = self._map_craniotomy_type(
            list_item.get_property(list_fields.CRANIOTOMY_TYPE.value)
        )
        if craniotomy_type == CraniotomyType.VISCTX:
            craniotomy_coordinates_reference = (
                CoordinateReferenceLocation.LAMBDA
            )
        else:
            craniotomy_coordinates_reference = None
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
            list_item.get_property(list_fields.IMPLANT_ID_COVERSLIP_TYPE.value)
        )
        dura_removed = convert_str_to_bool(
            list_item.get_property(list_fields.HP_DUROTOMY.value)
        )
        workstation_id = map_choice(
            list_item.get_property(list_fields.HP_WORK_STATION.value)
        )
        bregma_to_lambda_distance = parse_str_into_float(
            list_item.get_property(list_fields.BREG2_LAMB.value)
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
            == NeurosurgeryAndBehaviorList2019.HeadPostType.CAM.value
        ):
            headframe_type = "CAM-style"
            headframe_part_number = "0160-100-10 Rev A"
            well_type = "CAM-style"
            well_part_number = None
        elif (
            headpost_type
            == NeurosurgeryAndBehaviorList2019.HeadPostType.NEUROPIXEL.value
        ):
            headframe_type = "Neuropixel-style"
            headframe_part_number = "0160-100-10"
            well_type = "Neuropixel-style"
            well_part_number = "0160-200-36"
        elif (
            headpost_type
            == NeurosurgeryAndBehaviorList2019.HeadPostType.MESO_NGC.value
        ):
            headframe_type = "NGC-style"
            headframe_part_number = "0160-100-10"
            well_type = "Mesoscope-style"
            well_part_number = "0160-200-20"
        elif (
            headpost_type
            == NeurosurgeryAndBehaviorList2019.HeadPostType.WHC_NP.value
        ):
            headframe_type = "WHC #42"
            headframe_part_number = "42"
            well_type = "Neuropixel-style"
            well_part_number = "0160-200-36"
        elif (
            headpost_type
            == NeurosurgeryAndBehaviorList2019.HeadPostType.NGC.value
        ):
            headframe_type = "NGC-style"
            headframe_part_number = "0160-100-10"
            well_type = None
            well_part_number = None
        elif (
            headpost_type
            == NeurosurgeryAndBehaviorList2019.HeadPostType.AI_HEADBAR.value
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
        list_fields = NeurosurgeryAndBehaviorList2019.ListField
        start_date = map_date_to_datetime(
            list_item.get_property(list_fields.DATE_OF_SURGERY.value)
        )
        end_date = start_date
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        animal_weight_prior = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER.value)
        )
        animal_weight_post = parse_str_into_float(
            list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY.value)
        )
        anaesthesia = self._map_hp_anaesthesia(list_item, list_fields)
        headpost_type = list_item.get_property(list_fields.HEADPOST_TYPE.value)
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
        surgery_order = NeurosurgeryAndBehaviorList2023.SurgeryOrder
        anaesthetic_type = "isoflurane"
        if surgery_during == surgery_order.SECOND.value:
            duration = convert_hour_to_mins(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_ISO_DURATION.value
                )
            )
            level = parse_str_into_float(
                list_item.get_property(list_fields.ROUND1_INJ_ISOLEVEL.value)
            )
        else:
            # default is Initial Surgery
            duration = convert_hour_to_mins(
                list_item.get_property(list_fields.ISO_ON.value)
            )
            level = parse_str_into_float(
                list_item.get_property(list_fields.HP_ISO_LEVEL.value)
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
        surgery_order = NeurosurgeryAndBehaviorList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND.value:
            start_date = map_date_to_datetime(
                list_item.get_property(list_fields.DATE1ST_INJECTION.value)
            )
        else:
            start_date = map_date_to_datetime(
                list_item.get_property(list_fields.DATE_OF_SURGERY.value)
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
        injection_types = NeurosurgeryAndBehaviorList2023.InjectionType
        surgery_order = NeurosurgeryAndBehaviorList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND.value:
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION.value
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.FIRST_INJ_RECOVERY.value)
            )
            if injection_type.strip() == injection_types.IONTO.value:
                instrument_id = map_choice(
                    list_item.get_property(list_fields.IONTO_NUMBER_INJ2.value)
                )
            else:
                instrument_id = map_choice(
                    list_item.get_property(
                        list_fields.NANOJECT_NUMBER_INJ2.value
                    )
                )
        else:
            # default is Initial Surgery
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION.value
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.HP_RECOVERY.value)
            )
            if injection_type.strip() == injection_types.IONTO.value:
                instrument_id = map_choice(
                    list_item.get_property(list_fields.IONTO_NUMBER_INJ1.value)
                )
            else:
                instrument_id = map_choice(
                    list_item.get_property(
                        list_fields.NANOJECT_NUMBER_INJ10.value
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
        surgery_order = NeurosurgeryAndBehaviorList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND.value:
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION.value
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.FIRST_INJ_RECOVERY.value)
            )
        else:
            # default is Initial Surgery
            workstation_id = map_choice(
                list_item.get_property(
                    list_fields.WORK_STATION1ST_INJECTION.value
                )
            )
            recovery_time = parse_str_into_float(
                list_item.get_property(list_fields.HP_RECOVERY.value)
            )
        return workstation_id, recovery_time

    @staticmethod
    def _map_initial_followup_weight(list_item, list_fields, surgery_during):
        """Maps before and after weight based on surgery order"""
        surgery_order = NeurosurgeryAndBehaviorList2023.SurgeryOrder
        if surgery_during == surgery_order.SECOND.value:
            animal_weight_prior = parse_str_into_float(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_WEIGHT_BEFOR.value
                )
            )
            animal_weight_post = parse_str_into_float(
                list_item.get_property(
                    list_fields.FIRST_INJECTION_WEIGHT_AFTER.value
                )
            )
        else:
            animal_weight_prior = parse_str_into_float(
                list_item.get_property(list_fields.WEIGHT_BEFORE_SURGER.value)
            )
            animal_weight_post = parse_str_into_float(
                list_item.get_property(list_fields.WEIGHT_AFTER_SURGERY.value)
            )
        return animal_weight_prior, animal_weight_post

    def _map_burr_holes(
        self,
        list_item: ClientObject,
    ) -> List[Union[FiberImplant, IontophoresisInjection, NanojectInjection]]:
        """Maps SharePoint ListItem to list of FiberImplants/Injections"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        burr_procedures = []
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_1.value)):
            burr_procedures.extend(self._map_burr_hole_1(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_2.value)):
            burr_procedures.extend(self._map_burr_hole_2(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_3.value)):
            burr_procedures.extend(self._map_burr_hole_3(list_item))
        if map_choice(list_item.get_property(list_fields.BURR_HOLE_4.value)):
            burr_procedures.extend(self._map_burr_hole_4(list_item))
        return burr_procedures

    def _map_burr_hole_1(
        self,
        list_item: ClientObject,
    ) -> List[Union[IontophoresisInjection, NanojectInjection, FiberImplant]]:
        """Maps 1st burr hole to Injections and/or FiberImplants"""
        nsb_burr_types = NeurosurgeryAndBehaviorList2023.BurrHoleType
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        str_helpers = NeurosurgeryAndBehaviorList2023.StringParserHelper
        injection_types = NeurosurgeryAndBehaviorList2023.InjectionType
        burr_1_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_1.value):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_1.value).split(
                    str_helpers.BURR_TYPE_SPLITTER.value
                )
            )
        # map generic burr hole fields
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.VIRUS_HEMISPHERE.value)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_M_L.value)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.VIRUS_A_P.value)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ1_ANGLE_V2.value)
        )
        # map fields dependent on surgery order (initial or follow up)
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR1_DURING.value)
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
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION.value:
                injection_type = list_item.get_property(
                    list_fields.INJ1_TYPE.value
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.VIRUS_D_V.value)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ1_VIRUS_STRAIN_RT.value
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO.value:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ1_CURRENT.value)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ1_ALTERNATING_TIME.value
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ1_IONTO_TIME.value
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
                            list_fields.INJ1VOLPERDEPTH.value
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
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT.value:
                name = ProbeName.PROBE_A.value
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT1_DV.value)
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
        nsb_burr_types = NeurosurgeryAndBehaviorList2023.BurrHoleType
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        str_helpers = NeurosurgeryAndBehaviorList2023.StringParserHelper
        injection_types = NeurosurgeryAndBehaviorList2023.InjectionType
        burr_2_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_2.value):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_2.value).split(
                    str_helpers.BURR_TYPE_SPLITTER.value
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.HEMISPHERE2ND_INJ.value)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.ML2ND_INJ.value)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.AP2ND_INJ.value)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.INJ2_ANGLE_V2.value)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR2_DURING.value)
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
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION.value:
                injection_type = list_item.get_property(
                    list_fields.INJ2_TYPE.value
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.DV2ND_INJ.value)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ2_VIRUS_STRAIN_RT.value
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO.value:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ2_CURRENT.value)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ2_ALTERNATING_TIME.value
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ2_IONTO_TIME.value
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
                            list_fields.INJ2VOLPERDEPTH.value
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
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT.value:
                name = ProbeName.PROBE_B.value
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT2_DV.value)
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
        nsb_burr_types = NeurosurgeryAndBehaviorList2023.BurrHoleType
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        str_helpers = NeurosurgeryAndBehaviorList2023.StringParserHelper
        injection_types = NeurosurgeryAndBehaviorList2023.InjectionType
        burr_3_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_3.value):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_3.value).split(
                    str_helpers.BURR_TYPE_SPLITTER.value
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.BURR3_HEMISPHERE.value)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_ML.value)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_AP.value)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.BURR3_ANGLE.value)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR3_DURING.value)
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
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION.value:
                injection_type = list_item.get_property(
                    list_fields.INJ3_TYPE.value
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.BURR3_DV.value)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ_VIRUS_STRAIN_RT.value
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO.value:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ3_CURRENT.value)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ3_ALTERNATING_TIME.value
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ3_IONTO_TIME.value
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
                            list_fields.INJ3VOLPERDEPTH.value
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
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT.value:
                name = ProbeName.PROBE_C.value
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT3_D.value)
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
        nsb_burr_types = NeurosurgeryAndBehaviorList2023.BurrHoleType
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        str_helpers = NeurosurgeryAndBehaviorList2023.StringParserHelper
        injection_types = NeurosurgeryAndBehaviorList2023.InjectionType
        burr_4_procedures = []
        procedure_types = []
        if list_item.get_property(list_fields.BURR_HOLE_4.value):
            procedure_types.extend(
                list_item.get_property(list_fields.BURR_HOLE_4.value).split(
                    str_helpers.BURR_TYPE_SPLITTER.value
                )
            )
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        burr_hemisphere = map_hemisphere(
            list_item.get_property(list_fields.BURR4_HEMISPHERE.value)
        )
        burr_coordinate_ml = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_ML.value)
        )
        burr_coordinate_ap = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_AP.value)
        )
        burr_angle = parse_str_into_float(
            list_item.get_property(list_fields.BURR4_ANGLE.value)
        )
        burr_during = map_choice(
            list_item.get_property(list_fields.BURR4_DURING.value)
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
            list_item.get_property(list_fields.BREG2_LAMB.value)
        )
        coordinate_reference = CoordinateReferenceLocation.BREGMA
        for procedure in procedure_types:
            if procedure.strip() == nsb_burr_types.INJECTION.value:
                injection_type = list_item.get_property(
                    list_fields.INJ4_TYPE.value
                )
                burr_coordinate_depth = parse_str_into_float(
                    list_item.get_property(list_fields.BURR4_DV.value)
                )
                (
                    workstation_id,
                    recovery_time,
                    instrument_id,
                ) = self._map_initial_followup_injection(
                    list_item, list_fields, injection_type, burr_during
                )
                full_genome_name = list_item.get_property(
                    list_fields.INJ4_VIRUS_STRAIN_RT.value
                )
                injection_materials = self._map_injection_materials(
                    full_genome_name
                )
                if injection_type.strip() == injection_types.IONTO.value:
                    injection_current = parse_str_into_float(
                        list_item.get_property(list_fields.INJ4_CURRENT.value)
                    )
                    alternating_current = list_item.get_property(
                        list_fields.INJ4_ALTERNATING_TIME.value
                    )
                    injection_duration = list_item.get_property(
                        list_fields.INJ4_IONTO_TIME.value
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
                            list_fields.INJ4VOLPERDEPTH.value
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
            elif procedure.strip() == nsb_burr_types.FIBER_IMPLANT.value:
                name = ProbeName.PROBE_D.value
                fiber_implant_depth = parse_str_into_float(
                    list_item.get_property(list_fields.FIBER_IMPLANT4_D.value)
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
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        craniotomy_type = list_item.get_property(
            list_fields.CRANIOTOMY_TYPE.value
        )
        craniotomy_size = parse_str_into_float(craniotomy_type)
        craniotomy_during = map_choice(
            list_item.get_property(list_fields.CRANIOTOMY_DURING.value)
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
            list_item.get_property(list_fields.BREG2_LAMB.value)
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
        headframe_types = NeurosurgeryAndBehaviorList2023.HeadFrameType
        if headframe_type == headframe_types.VISUAL_CTX.value:
            return "0160-100-10"
        elif headframe_type == headframe_types.WHC_NP.value:
            return "0160-100-42"
        elif headframe_type == headframe_types.FRONTAL_CTX.value:
            return "0160-100-46"
        elif headframe_type == headframe_types.MOTOR_CTX.value:
            return "0160-100-51"
        elif headframe_type == headframe_types.WHC_2P.value:
            return "0160-100-45"
        else:
            return None

    @staticmethod
    def _map_well_part_number(well_type: str):
        """maps well_part_number from well_type"""
        well_types = NeurosurgeryAndBehaviorList2023.WellType
        if well_type == well_types.CAM.value:
            return "Rev A"
        elif well_type == well_types.MESOSCOPE.value:
            return "0160-200-20"
        elif well_type == well_types.NEUROPIXEL.value:
            return "0160-200-36"
        elif well_type == well_types.WHC_NP.value:
            return "0160-055-08"
        elif well_type == well_types.WHC_2P.value:
            return "0160-200-62"
        else:
            return None

    def _map_list_item_to_head_frame_2023(
        self,
        list_item: ClientObject,
    ) -> Headframe:
        """Maps a SharePoint ListItem to a HeadFrame model"""
        list_fields = NeurosurgeryAndBehaviorList2023.ListField
        experimenter_full_name = self._map_experimenter_name(
            list_item, list_fields
        )
        iacuc_protocol = list_item.get_property(
            list_fields.IACUC_PROTOCOL.value
        )
        headframe_type = list_item.get_property(list_fields.HEADPOST.value)
        headframe_part_number = self._map_hp_part_number(headframe_type)
        well_type = list_item.get_property(list_fields.HEADPOST_TYPE.value)
        well_part_number = self._map_well_part_number(well_type)
        hp_during = map_choice(
            list_item.get_property(list_fields.HEADPOST_DURING.value)
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
