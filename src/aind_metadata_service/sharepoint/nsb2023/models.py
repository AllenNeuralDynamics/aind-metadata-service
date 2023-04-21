"""Data Models for NSB 2023 Sharepoint ListItem"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Extra, Field, SecretStr, validator

from aind_metadata_service.sharepoint.nsb2019.models import (
    HeadPostInfo,
    Hemisphere,
    InjectionType,
    NumberWithNotes,
    Sex,
)


class CraniotomyType(Enum):
    """Enum class for Craniotomy Types"""

    FIVE_MM = "5mm"
    THREE_MM = "3mm"
    WHC = "WHC"


class HeadPost(Enum):
    """Enum class for HeadPost"""

    AI_HEADBAR = "AI Straight bar"
    OTHER = "Other (add details in requestor comments)"
    WHC_NP = "WHC NP"
    VISUAL_CTX = "Visual Ctx"
    FRONTAL_CTX = "Frontal Ctx"
    MOTOR_CTX = "Motor Ctx"


class HeadPostType(Enum):
    """Enum class for HeadPostType"""

    NEUROPIXEL = "Neuropixel"
    MESOSCOPE = "Mesoscope"
    NO_WELL = "No Well"
    OTHER = "Other (See requestor comments)"
    CAM = "Scientifica (CAM)"
    WHC_NP = "WHC NP"


class BurrHoleProcedure(Enum):
    """Enum class for BurrHoleProcedure"""

    INJECTION = "Injection"
    FIBER_IMPLANT = "Fiber Implant"


class During(Enum):
    """Enum class for Initial/FollowUp classifiers"""

    INITIAL_SURGERY = "Initial Surgery"
    FOLLOW_UP_SURGERY = "Follow up Surgery"


class HeadPostInfo2023(HeadPostInfo):
    """Extends HeadPostInfo data container to include extra constructor"""

    @classmethod
    def from_hp_and_hp_type(
        cls, hp: Optional[HeadPost], hp_type: Optional[HeadPostType]
    ):
        """Construct HeadPostInfo2023 from headpost and headpost_type"""
        headframe_type = hp
        well_type = hp_type
        if hp == HeadPost.VISUAL_CTX:
            headframe_part_number = "0160-100-10"
        elif hp == HeadPost.WHC_NP:
            headframe_part_number = "0160-100-42"
        elif hp == HeadPost.FRONTAL_CTX:
            headframe_part_number = "0160-100-46"
        elif hp == HeadPost.MOTOR_CTX:
            headframe_part_number = "0160-100-51"
        else:
            headframe_part_number = None
        if hp_type == HeadPostType.CAM:
            well_part_number = "Rev A"
        elif hp_type == HeadPostType.MESOSCOPE:
            well_part_number = "0160-200-20"
        elif hp_type == HeadPostType.NEUROPIXEL:
            well_part_number = "0160-200-36"
        elif hp_type == HeadPostType.WHC_NP:
            well_part_number = "0160-055-08"
        else:
            well_part_number = None
        return cls(
            headframe_type=headframe_type,
            headframe_part_number=headframe_part_number,
            well_type=well_type,
            well_part_number=well_part_number,
        )


@dataclass
class BurrHoleInfo:
    """Container for burr hole information"""

    hemisphere: Optional[Hemisphere] = None
    coordinate_ml: Optional[float] = None
    coordinate_ap: Optional[float] = None
    coordinate_depth: Optional[float] = None
    angle: Optional[float] = None
    during: Optional[During] = None
    inj_type: Optional[InjectionType] = None
    virus_strain: Optional[str] = None
    inj_current: Optional[float] = None
    alternating_current: Optional[str] = None
    inj_duration: Optional[timedelta] = None
    inj_volume: Optional[float] = None
    fiber_implant_depth: Optional[float] = None


@dataclass
class SurgeryDuringInfo:
    """Container for information related to surgeries during initial or
    follow-up sessions"""

    anaesthetic_duration_in_minutes: Optional[int] = None
    anaesthetic_level: Optional[float] = None
    start_date: Optional[datetime] = None
    workstation_id: Optional[str] = None
    recovery_time: Optional[float] = None
    weight_prior: Optional[float] = None
    weight_post: Optional[float] = None
    instrument_id: Optional[str] = None


class NSBList2023(BaseModel, extra=Extra.allow):
    """Data model for NSB 2023 ListItem"""

    _view_title = "New Request"

    ap_2nd_inj: Optional[NumberWithNotes] = Field(
        default=None, alias="AP2ndInj"
    )
    age_at_injection: Optional[float] = Field(
        default=None, alias="Age_x0020_at_x0020_Injection"
    )
    attachments: Optional[bool] = Field(default=None, alias="Attachments")
    author_id: Optional[int] = Field(default=None, alias="AuthorId")
    breg_2_lamb: Optional[float] = Field(default=None, alias="Breg2Lamb")
    burr1_injection_devi: Optional[str] = Field(
        default=None, alias="Burr1_x0020_Injection_x0020_Devi"
    )
    burr1_perform_during: Optional[During] = Field(
        default=None, alias="Burr1_x0020_Perform_x0020_During"
    )
    burr1_virus_biosafte: Optional[str] = Field(
        default=None, alias="Burr1_x0020_Virus_x0020_Biosafte"
    )
    burr2_injection_devi: Optional[str] = Field(
        default=None, alias="Burr2_x0020_Injection_x0020_Devi"
    )
    burr2_perform_during: Optional[During] = Field(
        default=None, alias="Burr2_x0020_Perform_x0020_During"
    )
    burr2_status: Optional[str] = Field(
        default=None, alias="Burr2_x0020_Status"
    )
    burr2_virus_biosafte: Optional[str] = Field(
        default=None, alias="Burr2_x0020_Virus_x0020_Biosafte"
    )
    burr3_ap: Optional[float] = Field(
        default=None, alias="Burr3_x0020_A_x002f_P"
    )
    burr3_dv: Optional[float] = Field(
        default=None, alias="Burr3_x0020_D_x002f_V"
    )
    burr3_injection_devi: Optional[str] = Field(
        default=None, alias="Burr3_x0020_Injection_x0020_Devi"
    )
    burr3_ml: Optional[float] = Field(
        default=None, alias="Burr3_x0020_M_x002f_L"
    )
    burr3_perform_during: Optional[During] = Field(
        default=None, alias="Burr3_x0020_Perform_x0020_During"
    )
    burr3_status: Optional[str] = Field(
        default=None, alias="Burr3_x0020_Status"
    )
    burr3_virus_biosafet: Optional[str] = Field(
        default=None, alias="Burr3_x0020_Virus_x0020_Biosafet"
    )
    burr4_ap: Optional[float] = Field(
        default=None, alias="Burr4_x0020_A_x002f_P"
    )
    burr4_dv: Optional[float] = Field(
        default=None, alias="Burr4_x0020_D_x002f_V"
    )
    burr4_injection_devi: Optional[str] = Field(
        default=None, alias="Burr4_x0020_Injection_x0020_Devi"
    )
    burr4_ml: Optional[float] = Field(
        default=None, alias="Burr4_x0020_M_x002f_L"
    )
    burr4_perform_during: Optional[During] = Field(
        default=None, alias="Burr4_x0020_Perform_x0020_During"
    )
    burr4_status: Optional[str] = Field(
        default=None, alias="Burr4_x0020_Status"
    )
    burr4_virus_biosafte: Optional[str] = Field(
        default=None, alias="Burr4_x0020_Virus_x0020_Biosafte"
    )
    burr_3_angle: Optional[float] = Field(
        default=None, alias="Burr_x0020_3_x0020_Angle"
    )
    burr_3_hemisphere: Optional[Hemisphere] = Field(
        default=None, alias="Burr_x0020_3_x0020_Hemisphere"
    )
    burr_4_angle: Optional[float] = Field(
        default=None, alias="Burr_x0020_4_x0020_Angle"
    )
    burr_4_hemisphere: Optional[Hemisphere] = Field(
        default=None, alias="Burr_x0020_4_x0020_Hemisphere"
    )
    burr_hole_1_st: Optional[str] = Field(
        default=None, alias="Burr_x0020_Hole_x0020_1_x0020_st"
    )
    burr_hole_1: Optional[List[BurrHoleProcedure]] = Field(
        default=None, alias="Burr_x0020_hole_x0020_1"
    )
    burr_hole_2: Optional[List[BurrHoleProcedure]] = Field(
        default=None, alias="Burr_x0020_hole_x0020_2"
    )
    burr_hole_3: Optional[List[BurrHoleProcedure]] = Field(
        default=None, alias="Burr_x0020_hole_x0020_3"
    )
    burr_hole_4: Optional[List[BurrHoleProcedure]] = Field(
        default=None, alias="Burr_x0020_hole_x0020_4"
    )
    com_coplanar: Optional[str] = Field(default=None, alias="ComCoplanar")
    com_damage: Optional[str] = Field(default=None, alias="ComDamage")
    com_durotomy: Optional[str] = Field(default=None, alias="ComDurotomy")
    com_sinusbleed: Optional[str] = Field(default=None, alias="ComSinusbleed")
    com_swelling: Optional[str] = Field(default=None, alias="ComSwelling")
    com_window: Optional[str] = Field(default=None, alias="ComWindow")
    compliance_asset_id: Optional[str] = Field(
        default=None, alias="ComplianceAssetId"
    )
    content_type_id: Optional[str] = Field(default=None, alias="ContentTypeId")
    contusion: Optional[str] = Field(default=None, alias="Contusion")
    craniotomy_type: Optional[CraniotomyType] = Field(
        default=None, alias="CraniotomyType"
    )
    craniotomy_perform_during: Optional[During] = Field(
        default=None, alias="Craniotomy_x0020_Perform_x0020_D"
    )
    created: Optional[datetime] = Field(default=None, alias="Created")
    dv_2nd_inj: Optional[NumberWithNotes] = Field(
        default=None, alias="DV2ndInj"
    )
    date_1st_injection: Optional[datetime] = Field(
        default=None, alias="Date1stInjection"
    )
    date_range_start: Optional[datetime] = Field(
        default=None, alias="DateRangeStart"
    )
    date_of_birth: Optional[datetime] = Field(
        default=None, alias="Date_x0020_of_x0020_Birth"
    )
    date_of_surgery: Optional[datetime] = Field(
        default=None, alias="Date_x0020_of_x0020_Surgery"
    )
    editor_id: Optional[int] = Field(default=None, alias="EditorId")
    fiber_implant1_dv: Optional[float] = Field(
        default=None, alias="FiberImplant1DV"
    )
    fiber_implant2_dv: Optional[float] = Field(
        default=None, alias="FiberImplant2DV"
    )
    fiber_implant1_length: Optional[NumberWithNotes] = Field(
        default=None, alias="Fiber_x0020_Implant1_x0020_Lengt"
    )
    fiber_implant2_length: Optional[NumberWithNotes] = Field(
        default=None, alias="Fiber_x0020_Implant2_x0020_Lengt"
    )
    fiber_implant3_d: Optional[float] = Field(
        default=None, alias="Fiber_x0020_Implant3_x0020_D_x00"
    )
    fiber_implant3_length: Optional[NumberWithNotes] = Field(
        default=None, alias="Fiber_x0020_Implant3_x0020_Lengt"
    )
    fiber_implant4_d: Optional[float] = Field(
        default=None, alias="Fiber_x0020_Implant4_x0020_D_x00"
    )
    fiber_implant4_length: Optional[NumberWithNotes] = Field(
        default=None, alias="Fiber_x0020_Implant4_x0020_Lengt"
    )
    file_system_object_type: Optional[int] = Field(
        default=None, alias="FileSystemObjectType"
    )
    first_inj_recovery: Optional[int] = Field(
        default=None, alias="FirstInjRecovery"
    )
    first_injection_iso_duration: Optional[timedelta] = Field(
        default=None, alias="FirstInjectionIsoDuration"
    )
    first_injection_weight_after: Optional[float] = Field(
        default=None, alias="FirstInjectionWeightAfter"
    )
    first_injection_weight_before: Optional[float] = Field(
        default=None, alias="FirstInjectionWeightBefor"
    )
    guid: Optional[str] = Field(default=None, alias="GUID")
    hp_iso_level: Optional[float] = Field(default=None, alias="HPIsoLevel")
    hp_recovery: Optional[float] = Field(default=None, alias="HPRecovery")
    hp_surgeon_comments: Optional[str] = Field(
        default=None, alias="HPSurgeonComments"
    )
    headpost: Optional[HeadPost] = Field(default=None, alias="Headpost")
    headpost_type: Optional[HeadPostType] = Field(
        default=None, alias="HeadpostType"
    )
    headpost_perform_during: Optional[During] = Field(
        default=None, alias="Headpost_x0020_Perform_x0020_Dur"
    )
    hemisphere_2nd_inj: Optional[Hemisphere] = Field(
        default=None, alias="Hemisphere2ndInj"
    )
    hp_work_station: Optional[str] = Field(default=None, alias="HpWorkStation")
    iacuc_protocol: Optional[str] = Field(
        default=None, alias="IACUC_x0020_Protocol_x0020__x002"
    )
    id: Optional[int] = Field(default=None, alias="ID")
    id2: Optional[int] = Field(default=None, alias="Id")
    implant_id_coverslip_type: Optional[NumberWithNotes] = Field(
        default=None, alias="ImplantIDCoverslipType"
    )
    inj1_alternating_time: Optional[str] = Field(
        default=None, alias="Inj1AlternatingTime"
    )
    inj1_angle_v2: Optional[float] = Field(default=None, alias="Inj1Angle_v2")
    inj1_current: Optional[float] = Field(default=None, alias="Inj1Current")
    inj1_ionto_time: Optional[timedelta] = Field(
        default=None, alias="Inj1IontoTime"
    )
    inj1_storage_location: Optional[str] = Field(
        default=None, alias="Inj1StorageLocation"
    )
    inj1_type: Optional[InjectionType] = Field(default=None, alias="Inj1Type")
    inj1_virus_strain_rt: Optional[str] = Field(
        default=None, alias="Inj1VirusStrain_rt"
    )
    inj2_alternating_time: Optional[str] = Field(
        default=None, alias="Inj2AlternatingTime"
    )
    inj2_angle_v2: Optional[float] = Field(default=None, alias="Inj2Angle_v2")
    inj2_current: Optional[float] = Field(default=None, alias="Inj2Current")
    inj2_ionto_time: Optional[timedelta] = Field(
        default=None, alias="Inj2IontoTime"
    )
    inj2_storage_location: Optional[str] = Field(
        default=None, alias="Inj2StorageLocation"
    )
    inj2_type: Optional[InjectionType] = Field(default=None, alias="Inj2Type")
    inj2_virus_strain_rt: Optional[str] = Field(
        default=None, alias="Inj2VirusStrain_rt"
    )
    inj3_alternating_time: Optional[str] = Field(
        default=None, alias="Inj3AlternatingTime"
    )
    inj3_current: Optional[float] = Field(default=None, alias="Inj3Current")
    inj3_ionto_time: Optional[timedelta] = Field(
        default=None, alias="Inj3IontoTime"
    )
    inj3_storage_location: Optional[str] = Field(
        default=None, alias="Inj3StorageLocation"
    )
    inj3_type: Optional[InjectionType] = Field(default=None, alias="Inj3Type")
    inj3_ret_setting: Optional[str] = Field(
        default=None, alias="Inj3retSetting"
    )
    inj3_vol_per_depth: Optional[NumberWithNotes] = Field(
        default=None, alias="Inj3volperdepth"
    )
    inj4_alternating_time: Optional[str] = Field(
        default=None, alias="Inj4AlternatingTime"
    )
    inj4_current: Optional[float] = Field(default=None, alias="Inj4Current")
    inj4_ionto_time: Optional[timedelta] = Field(
        default=None, alias="Inj4IontoTime"
    )
    inj4_storage_location: Optional[str] = Field(
        default=None, alias="Inj4StorageLocation"
    )
    inj4_type: Optional[InjectionType] = Field(default=None, alias="Inj4Type")
    inj4_virus_strain_rt: Optional[str] = Field(
        default=None, alias="Inj4VirusStrain_rt"
    )
    inj4_ret_setting: Optional[str] = Field(
        default=None, alias="Inj4retSetting"
    )
    inj4_vol_per_depth: Optional[NumberWithNotes] = Field(
        default=None, alias="Inj4volperdepth"
    )
    inj_virus_strain_rt: Optional[str] = Field(
        default=None, alias="InjVirusStrain_rt"
    )
    ionto_number_inj1: Optional[str] = Field(
        default=None, alias="IontoNumberInj1"
    )
    ionto_number_inj2: Optional[str] = Field(
        default=None, alias="IontoNumberInj2"
    )
    iso_on: Optional[timedelta] = Field(default=None, alias="Iso_x0020_On")
    lims_project: Optional[str] = Field(default=None, alias="LIMSProject")
    lims_taskflow: Optional[str] = Field(default=None, alias="LIMSTaskflow")
    lims_required: Optional[str] = Field(
        default=None, alias="LIMs_x0020_Required"
    )
    labtracks_group: Optional[str] = Field(
        default=None, alias="LabTracks_x0020_Group"
    )
    labtracks_id: Optional[str] = Field(
        default=None, alias="LabTracks_x0020_ID1"
    )
    labtracks_requestor: Optional[SecretStr] = Field(
        default=None, alias="LabTracks_x0020_Requestor"
    )
    light_cycle: Optional[str] = Field(default=None, alias="LightCycle")
    long_requestor_comments: Optional[str] = Field(
        default=None, alias="LongRequestorComments"
    )
    ml_2nd_inj: Optional[NumberWithNotes] = Field(
        default=None, alias="ML2ndInj"
    )
    modified: Optional[datetime] = Field(default=None, alias="Modified")
    nanoject_number_inj10: Optional[str] = Field(
        default=None, alias="NanojectNumberInj10"
    )
    nanoject_number_inj2: Optional[str] = Field(
        default=None, alias="NanojectNumberInj2"
    )
    odata_ui_version_string: Optional[str] = Field(
        default=None, alias="OData__UIVersionString"
    )
    odata_of_burr: Optional[str] = Field(
        default=None, alias="OData__x0023__x0020_of_x0020_Burr_x002"
    )
    pi_id: Optional[int] = Field(default=None, alias="PIId")
    pi_string_id: Optional[str] = Field(default=None, alias="PIStringId")
    pedigree_name: Optional[str] = Field(default=None, alias="PedigreeName")
    procedure: Optional[str] = Field(default=None, alias="Procedure")
    procedure_family: Optional[str] = Field(
        default=None, alias="Procedure_x0020_Family"
    )
    procedure_slots: Optional[str] = Field(
        default=None, alias="Procedure_x0020_Slots"
    )
    procedure_t2: Optional[str] = Field(
        default=None, alias="Procedure_x0020_T2"
    )
    project_id: Optional[str] = Field(default=None, alias="ProjectID")
    round1_inj_iso_level: Optional[float] = Field(
        default=None, alias="Round1InjIsolevel"
    )
    server_redirected_embed_uri: Optional[str] = Field(
        default=None, alias="ServerRedirectedEmbedUri"
    )
    server_redirected_embed_url: Optional[str] = Field(
        default=None, alias="ServerRedirectedEmbedUrl"
    )
    sex: Optional[Sex] = Field(default=None, alias="Sex")
    surgery_status: Optional[str] = Field(default=None, alias="SurgeryStatus")
    test_1st_round_id: Optional[str] = Field(
        default=None, alias="TEST_x0020_1st_x0020_Round_x0020Id"
    )
    test_1st_round_string_id: Optional[str] = Field(
        default=None, alias="TEST_x0020_1st_x0020_Round_x0020StringId"
    )
    test1_id: Optional[int] = Field(default=None, alias="Test1Id")
    test1_string_id: Optional[str] = Field(default=None, alias="Test1StringId")
    title: Optional[str] = Field(default=None, alias="Title")
    virus_ap: Optional[NumberWithNotes] = Field(
        default=None, alias="Virus_x0020_A_x002f_P"
    )
    virus_dv: Optional[NumberWithNotes] = Field(
        default=None, alias="Virus_x0020_D_x002f_V"
    )
    virus_hemisphere: Optional[Hemisphere] = Field(
        default=None, alias="Virus_x0020_Hemisphere"
    )
    virus_ml: Optional[NumberWithNotes] = Field(
        default=None, alias="Virus_x0020_M_x002f_L"
    )
    weight_after_surgery: Optional[float] = Field(
        default=None, alias="Weight_x0020_after_x0020_Surgery"
    )
    weight_before_surgery: Optional[float] = Field(
        default=None, alias="Weight_x0020_before_x0020_Surger"
    )
    work_station_1st_injection: Optional[str] = Field(
        default=None, alias="WorkStation1stInjection"
    )
    inj1_vol_per_depth: Optional[float] = Field(
        default=None, alias="inj1volperdepth"
    )
    inj2_vol_per_depth: Optional[float] = Field(
        default=None, alias="inj2volperdepth"
    )
    ret_setting0: Optional[str] = Field(default=None, alias="retSetting0")
    ret_setting1: Optional[str] = Field(default=None, alias="retSetting1")

    @validator(
        "age_at_injection",
        "breg_2_lamb",
        "burr3_ap",
        "burr3_dv",
        "burr3_ml",
        "burr4_ap",
        "burr4_dv",
        "burr4_ml",
        "fiber_implant1_dv",
        "fiber_implant2_dv",
        "fiber_implant3_d",
        "fiber_implant4_d",
        "first_injection_iso_duration",
        "first_injection_weight_after",
        "first_injection_weight_before",
        "hp_iso_level",
        "hp_recovery",
        "iso_on",
        "round1_inj_iso_level",
        "weight_after_surgery",
        "weight_before_surgery",
        "inj1_vol_per_depth",
        "inj2_vol_per_depth",
        pre=True,
    )
    def parse_basic_num_str_to_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        """Parse a number from a string. Can be like -3.6mm, 2.5E5, etc."""
        pattern = r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))"
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1)
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    @validator(
        "burr1_injection_devi",
        "burr1_virus_biosafte",
        "burr2_injection_devi",
        "burr2_status",
        "burr2_virus_biosafte",
        "burr3_injection_devi",
        "burr3_status",
        "burr3_virus_biosafet",
        "burr4_injection_devi",
        "burr4_status",
        "burr4_virus_biosafte",
        "burr_hole_1_st",
        "com_coplanar",
        "com_damage",
        "com_durotomy",
        "com_sinusbleed",
        "com_swelling",
        "com_window",
        "compliance_asset_id",
        "content_type_id",
        "contusion",
        "guid",
        "hp_surgeon_comments",
        "hp_work_station",
        "iacuc_protocol",
        "inj1_alternating_time",
        "inj1_storage_location",
        "inj1_virus_strain_rt",
        "inj2_alternating_time",
        "inj2_storage_location",
        "inj2_virus_strain_rt",
        "inj3_alternating_time",
        "inj3_storage_location",
        "inj3_ret_setting",
        "inj4_alternating_time",
        "inj4_storage_location",
        "inj4_virus_strain_rt",
        "inj4_ret_setting",
        "inj_virus_strain_rt",
        "ionto_number_inj1",
        "ionto_number_inj2",
        "lims_project",
        "lims_taskflow",
        "lims_required",
        "labtracks_group",
        "labtracks_id",
        "light_cycle",
        "long_requestor_comments",
        "nanoject_number_inj10",
        "nanoject_number_inj2",
        "odata_ui_version_string",
        "odata_of_burr",
        "pi_string_id",
        "pedigree_name",
        "procedure",
        "procedure_family",
        "procedure_slots",
        "procedure_t2",
        "project_id",
        "server_redirected_embed_uri",
        "server_redirected_embed_url",
        "surgery_status",
        "test_1st_round_id",
        "test_1st_round_string_id",
        "test1_string_id",
        "title",
        "work_station_1st_injection",
        "ret_setting0",
        "ret_setting1",
        pre=True,
    )
    def filter_select_str(cls, v: Optional[str]) -> Optional[str]:
        """Filter out strings that contain 'Select', etc."""
        strings_to_filter = [
            "Select...",
            "N/A",
            "NA",
            "None",
            "Select if applicable...",
        ]
        if type(v) is str and v in strings_to_filter:
            return None
        else:
            return v

    @validator(
        "ap_2nd_inj",
        "dv_2nd_inj",
        "fiber_implant1_length",
        "fiber_implant2_length",
        "fiber_implant3_length",
        "fiber_implant4_length",
        "implant_id_coverslip_type",
        "inj3_vol_per_depth",
        "inj4_vol_per_depth",
        "ml_2nd_inj",
        "virus_ap",
        "virus_dv",
        "virus_ml",
        pre=True,
    )
    def parse_numeric_with_notes(cls, v: Union[str, None]) -> NumberWithNotes:
        """Match like '0.25' or '-4.72, rostral to lambda' or
        '5mm stacked coverslip' or '30 degrees'"""
        pattern1 = r"^([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))$"
        pattern2 = r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))([,\w].*)"
        if type(v) is str and re.match(pattern1, v):
            return NumberWithNotes(
                raw_input=v, number=re.match(pattern1, v).group(1)
            )
        elif type(v) is str and re.match(pattern2, v):
            return NumberWithNotes(
                raw_input=v,
                number=re.match(pattern2, v).group(1),
                notes=re.match(pattern2, v).group(2),
            )
        else:
            return NumberWithNotes(raw_input=v)

    @validator(
        "burr_3_angle",
        "burr_4_angle",
        "inj1_angle_v2",
        "inj2_angle_v2",
        pre=True,
    )
    def parse_angle_str_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        """Parses string like '30 degrees' into a float"""
        pattern = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))\s*"
            r"(?:deg|degs|degree|degrees){0,1}\s*$"
        )
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1)
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    @validator(
        "inj1_current",
        "inj2_current",
        "inj3_current",
        "inj4_current",
        pre=True,
    )
    def parse_current_str_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        """Parses strings like 3.5 or 3.5uA into 3.5. Will map strings like
        3.5min to None"""
        pattern = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))(\s*uA\s*)*$"
        )
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1)
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    @validator(
        "burr1_perform_during",
        "burr2_perform_during",
        "burr3_perform_during",
        "burr4_perform_during",
        "craniotomy_perform_during",
        "headpost_perform_during",
        pre=True,
    )
    def parse_during_type(cls, v: Optional[str]) -> Optional[During]:
        """Parses string into a During model"""
        if type(v) is str and v in [e.value for e in During]:
            return During(v)
        else:
            return None

    @validator("craniotomy_type", pre=True)
    def parse_craniotomy_type(
        cls, v: Optional[str]
    ) -> Optional[CraniotomyType]:
        """Match like 'Visual Cortex 5mm'"""
        if type(v) is str and v in [e.value for e in CraniotomyType]:
            return CraniotomyType(v)
        else:
            return None

    @validator("headpost", pre=True)
    def parse_headpost(cls, v: Optional[str]) -> Optional[HeadPost]:
        """Parses string into a HeadPost model"""
        if type(v) is str and v in [e.value for e in HeadPost]:
            return HeadPost(v)
        else:
            return None

    @validator("headpost_type", pre=True)
    def parse_headpost_type(cls, v: Optional[str]) -> Optional[HeadPostType]:
        """Parses string into a HeadPostType model"""
        if type(v) is str and v in [e.value for e in HeadPostType]:
            return HeadPostType(v)
        else:
            return None

    @validator("sex", pre=True)
    def parse_sex_type(cls, v: Optional[str]) -> Optional[Sex]:
        """Parses string into a Sex model"""
        if type(v) is str and v in [e.value for e in Sex]:
            return Sex(v)
        else:
            return None

    @validator(
        "burr_3_hemisphere",
        "burr_4_hemisphere",
        "hemisphere_2nd_inj",
        "virus_hemisphere",
        pre=True,
    )
    def parse_hemisphere_type(cls, v: Optional[str]) -> Optional[Hemisphere]:
        """Parses string into a Hemisphere model"""
        if type(v) is str and v in [e.value for e in Hemisphere]:
            return Hemisphere(v)
        else:
            return None

    @validator("inj1_type", "inj2_type", "inj3_type", "inj4_type", pre=True)
    def parse_injection_type(cls, v: Optional[str]) -> Optional[InjectionType]:
        """Parses string into a InjectionType model"""
        if type(v) is str and v in [e.value for e in InjectionType]:
            return InjectionType(v)
        else:
            return None

    @validator(
        "inj1_ionto_time",
        "inj2_ionto_time",
        "inj3_ionto_time",
        "inj4_ionto_time",
        pre=True,
    )
    def parse_time_length(
        cls, v: Union[str, int, float, None]
    ) -> Optional[timedelta]:
        """Parses time length string into timedelta"""
        pattern1 = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))\s*"
            r"(?:min|mins|minute|minutes){0,1}\s*$"
        )
        pattern2 = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))\s*"
            r"(?:min|mins|minute|minutes){1}\s*(\d+)\s*"
            r"(?:sec|secs|second|seconds)(?:/depth|/location)*$"
        )
        if type(v) is str and re.match(pattern1, v):
            minutes = float(re.match(pattern1, v).group(1))
            return timedelta(minutes=minutes)
        elif type(v) is str and re.match(pattern2, v):
            minutes = float(re.match(pattern2, v).group(1))
            seconds = float(re.match(pattern2, v).group(2))
            return timedelta(minutes=minutes, seconds=seconds)
        elif type(v) is int or type(v) is float:
            return timedelta(minutes=v)
        else:
            return None

    @validator("first_injection_iso_duration", "iso_on", pre=True)
    def parse_hours_to_timedelta(
        cls, v: Union[float, str, None]
    ) -> Optional[timedelta]:
        """Parses hours string into timedelta"""
        if v is None:
            return None
        else:
            return timedelta(hours=float(v))

    @validator(
        "burr_hole_1", "burr_hole_2", "burr_hole_3", "burr_hole_4", pre=True
    )
    def parse_burr_hole(
        cls, v: Optional[str]
    ) -> Optional[List[BurrHoleProcedure]]:
        """Parses string into a BurrHoleProcedure model"""
        if v is None:
            return None
        else:
            burr_hole_procedures = []
            if BurrHoleProcedure.INJECTION.value in v:
                burr_hole_procedures.append(BurrHoleProcedure.INJECTION)
            if BurrHoleProcedure.FIBER_IMPLANT.value in v:
                burr_hole_procedures.append(BurrHoleProcedure.FIBER_IMPLANT)
            return burr_hole_procedures

    def has_hp_procedure(self) -> bool:
        """Is there a headpost procedure?"""
        if self.procedure is None:
            return False
        elif (
            "Headpost" in self.procedure
            or "HP Only" in self.procedure
            or "HP Transcranial" in self.procedure
        ):
            return True
        else:
            return False

    def has_burr_hole_procedure(
        self, burr_hole_num: int, burr_hole_procedure: BurrHoleProcedure
    ) -> bool:
        """
        Is there a burr hole procedure?
        Parameters
        ----------
        burr_hole_num : int
          Burr Hole Number (1 through 4)
        burr_hole_procedure : BurrHoleProcedure
          Procedure Type (Fiber Implant or Injection)

        Returns
        -------
        bool

        """
        burr_hole_procedures = getattr(self, f"burr_hole_{burr_hole_num}")
        if burr_hole_procedures is None:
            return False
        elif burr_hole_procedure in burr_hole_procedures:
            return True
        else:
            return False

    def has_cran_procedure(self) -> bool:
        """Is there a craniotomy procedure?"""
        if self.procedure is not None and (
            "Visual Ctx" in self.procedure
            or "Motor Ctx" in self.procedure
            or "Frontal Ctx" in self.procedure
            or "WHC NP" in self.procedure
        ):
            return True
        else:
            return False

    def burr_hole_info(self, burr_hole_num: int) -> BurrHoleInfo:
        """
        Compiles burr hole information from NSB data
        Parameters
        ----------
        burr_hole_num : int
          Burr hole number

        Returns
        -------
        BurrHoleInfo

        """
        if burr_hole_num == 1:
            return BurrHoleInfo(
                hemisphere=self.virus_hemisphere,
                coordinate_ml=self.virus_ml.number,
                coordinate_ap=self.virus_ap.number,
                coordinate_depth=self.virus_dv.number,
                angle=self.inj1_angle_v2,
                during=self.burr1_perform_during,
                inj_type=self.inj1_type,
                virus_strain=self.inj1_virus_strain_rt,
                inj_current=self.inj1_current,
                alternating_current=self.inj1_alternating_time,
                inj_duration=self.inj1_ionto_time,
                inj_volume=self.inj1_vol_per_depth,
                fiber_implant_depth=self.fiber_implant1_dv,
            )
        elif burr_hole_num == 2:
            return BurrHoleInfo(
                hemisphere=self.hemisphere_2nd_inj,
                coordinate_ml=self.ml_2nd_inj.number,
                coordinate_ap=self.ap_2nd_inj.number,
                coordinate_depth=self.dv_2nd_inj.number,
                angle=self.inj2_angle_v2,
                during=self.burr2_perform_during,
                inj_type=self.inj2_type,
                virus_strain=self.inj2_virus_strain_rt,
                inj_current=self.inj2_current,
                alternating_current=self.inj2_alternating_time,
                inj_duration=self.inj2_ionto_time,
                inj_volume=self.inj2_vol_per_depth,
                fiber_implant_depth=self.fiber_implant2_dv,
            )
        elif burr_hole_num == 3:
            return BurrHoleInfo(
                hemisphere=self.burr_3_hemisphere,
                coordinate_ml=self.burr3_ml,
                coordinate_ap=self.burr3_ap,
                coordinate_depth=self.burr3_dv,
                angle=self.burr_3_angle,
                during=self.burr3_perform_during,
                inj_type=self.inj3_type,
                virus_strain=self.inj_virus_strain_rt,
                inj_current=self.inj3_current,
                alternating_current=self.inj3_alternating_time,
                inj_duration=self.inj3_ionto_time,
                inj_volume=self.inj3_vol_per_depth,
                fiber_implant_depth=self.fiber_implant3_d,
            )
        elif burr_hole_num == 4:
            return BurrHoleInfo(
                hemisphere=self.burr_4_hemisphere,
                coordinate_ml=self.burr4_ml,
                coordinate_ap=self.burr4_ap,
                coordinate_depth=self.burr4_dv,
                angle=self.burr_4_angle,
                during=self.burr4_perform_during,
                inj_type=self.inj4_type,
                virus_strain=self.inj4_virus_strain_rt,
                inj_current=self.inj4_current,
                alternating_current=self.inj4_alternating_time,
                inj_duration=self.inj4_ionto_time,
                inj_volume=self.inj4_vol_per_depth,
                fiber_implant_depth=self.fiber_implant4_d,
            )
        else:
            return BurrHoleInfo()

    def surgery_during_info(
        self, during: During, inj_type: Optional[InjectionType] = None
    ) -> SurgeryDuringInfo:
        """
        Compiles burr hole information from NSB data
        Parameters
        ----------
        during : During
          Initial or Follow up
        inj_type : Optional[InjectionType]
          Injection type during the surgery. Default is None.

        Returns
        -------
        SurgeryDuringInfo

        """
        if during == During.FOLLOW_UP_SURGERY:
            if inj_type == InjectionType.NANOJECT:
                instrument_id = self.nanoject_number_inj2
            elif inj_type == InjectionType.IONTOPHORESIS:
                instrument_id = self.ionto_number_inj2
            else:
                instrument_id = None
            return SurgeryDuringInfo(
                anaesthetic_duration_in_minutes=None
                if self.first_injection_iso_duration is None
                else self.first_injection_iso_duration.total_seconds() / 60,
                anaesthetic_level=self.round1_inj_iso_level,
                start_date=self.date_1st_injection,
                workstation_id=self.work_station_1st_injection,
                recovery_time=self.first_inj_recovery,
                weight_prior=self.first_injection_weight_before,
                weight_post=self.first_injection_weight_after,
                instrument_id=instrument_id,
            )
        elif during == During.INITIAL_SURGERY:
            if inj_type == InjectionType.NANOJECT:
                instrument_id = self.nanoject_number_inj10
            elif inj_type == InjectionType.IONTOPHORESIS:
                instrument_id = self.ionto_number_inj1
            else:
                instrument_id = None
            return SurgeryDuringInfo(
                anaesthetic_duration_in_minutes=None
                if self.iso_on is None
                else self.iso_on.total_seconds() / 60,
                anaesthetic_level=self.hp_iso_level,
                start_date=self.date_of_surgery,
                workstation_id=self.work_station_1st_injection,
                recovery_time=self.hp_recovery,
                weight_prior=self.weight_before_surgery,
                weight_post=self.weight_after_surgery,
                instrument_id=instrument_id,
            )
        else:
            return SurgeryDuringInfo()
