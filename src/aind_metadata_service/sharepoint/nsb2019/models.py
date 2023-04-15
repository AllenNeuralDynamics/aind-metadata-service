from dataclasses import dataclass
from typing import Optional
from enum import Enum


class NSBList2019:
    """Class to contain helpful info to parse the 2019 SharePoint List"""

    VIEW_TITLE = "New Request"

    class StringParserHelper:
        """Enum class for SharePoint's response strings"""

        # Not really why, but some response fields return 'Select...'
        SELECT_STR = "Select..."
        PROCEDURE_TYPE_SPLITTER = "+"

    class InjStringParserHelper:
        """Some injections have this to indicate rostal info"""

        ROSTAL_TO_LAMBDA = "rostal to lambda"

    class ProcedureType:
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

    class InjectionType:
        """Enum class for Injection Types"""

        IONTO = "Iontophoresis"
        NANOJECT = "Nanoject (Pressure)"

    class CraniotomyType:
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

    class ListField:
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


@dataclass
class HeadPostInfo:
    headframe_type: Optional[str] = None
    headframe_part_number: Optional[str] = None
    well_type: Optional[str] = None
    well_part_number: Optional[str] = None

    @classmethod
    def from_headpost_type(cls, headpost_type: Optional[
        NSBList2019.ListField.HEADPOST_TYPE]):
        if headpost_type is None or headpost_type not in NSBList2019.HeadPostType.__members__.values():
            return cls()
        elif headpost_type == NSBList2019.HeadPostType.CAM:
            return cls(headframe_type="CAM-style",
                       headframe_part_number="0160-100-10 Rev A",
                       well_type="CAM-style")
        elif headpost_type == NSBList2019.HeadPostType.NEUROPIXEL:
            return cls(headframe_type="Neuropixel-style",
                       headframe_part_number="0160-100-10",
                       well_type="Neuropixel-style",
                       well_part_number="0160-200-36")
        elif headpost_type == NSBList2019.HeadPostType.MESO_NGC:
            return cls(headframe_type="NGC-style",
                       headframe_part_number="0160-100-10",
                       well_type="Mesoscope-style",
                       well_part_number="0160-200-20")
        elif headpost_type == NSBList2019.HeadPostType.WHC_NP:
            return cls(headframe_type="WHC #42",
                       headframe_part_number="42",
                       well_type="Neuropixel-style",
                       well_part_number="0160-200-36")
        elif headpost_type == NSBList2019.HeadPostType.NGC:
            return cls(headframe_type="NGC-style",
                       headframe_part_number="0160-100-10")
        elif headpost_type == NSBList2019.HeadPostType.AI_HEADBAR:
            return cls(headframe_type="AI Straight Headbar")
        else:
            return cls()
