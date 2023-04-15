from typing import Optional, Union, Tuple
from pydantic import BaseModel, Extra, Field, validator
from datetime import datetime
import re


class NSBList2019(BaseModel, extra=Extra.allow):

    _view_title = "New Request"

    ap_2nd_inj: Optional[Tuple[float, Optional[str]]] = Field(
        default=None, alias="AP2ndInj"
    )
    age_at_injection: Optional[float] = Field(
        default=None, alias="Age_x0020_at_x0020_Injection"
    )
    attachments: Optional[bool] = Field(default=None, alias="Attachments")
    author_id: Optional[int] = Field(default=None, alias="AuthorId")
    breg_2_lamb: Optional[float] = Field(default=None, alias="Breg2Lamb")
    cage: Optional[str] = Field(default=None, alias="Cage")
    com_after_1st_inj: Optional[str] = Field(
        default=None, alias="ComAfter1stInj"
    )
    com_after_2nd_inj: Optional[str] = Field(
        default=None, alias="ComAfter2ndInj"
    )
    com_coplanar: Optional[str] = Field(default=None, alias="ComCoplanar")
    com_damage: Optional[str] = Field(default=None, alias="ComDamage")
    com_during_1st_inj: Optional[str] = Field(
        default=None, alias="ComDuring1stInj"
    )
    com_during_2nd_inj: Optional[str] = Field(
        default=None, alias="ComDuring2ndInj"
    )
    com_durotomy: Optional[str] = Field(default=None, alias="ComDurotomy")
    com_sinusbleed: Optional[str] = Field(default=None, alias="ComSinusbleed")
    com_swelling: Optional[str] = Field(default=None, alias="ComSwelling")
    com_window: Optional[str] = Field(default=None, alias="ComWindow")
    compliance_asset_id: Optional[str] = Field(
        default=None, alias="ComplianceAssetId"
    )
    content_type_id: Optional[str] = Field(default=None, alias="ContentTypeId")
    contusion: Optional[str] = Field(default=None, alias="Contusion")
    craniotomy_type: Optional[Tuple[str, float]] = Field(
        default=None, alias="CraniotomyType"
    )
    created: Optional[datetime] = Field(default=None, alias="Created")
    dv_2nd_inj: Optional[float] = Field(default=None, alias="DV2ndInj")
    date_1st_injection: Optional[datetime] = Field(
        default=None, alias="Date1stInjection"
    )
    date_2nd_injection: Optional[datetime] = Field(
        default=None, alias="Date2ndInjection"
    )
    date_range_end: Optional[datetime] = Field(
        default=None, alias="DateRangeEnd"
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
    end_of_week: Optional[datetime] = Field(
        default=None, alias="End_x0020_of_x0020_Week"
    )
    exudate_severity: Optional[str] = Field(
        default=None, alias="Exudate_x0020_Severity"
    )
    eye_affected: Optional[str] = Field(
        default=None, alias="Eye_x0020_Affected"
    )
    eye_issue: Optional[str] = Field(default=None, alias="Eye_x0020_Issue")
    fiber_implant1: Optional[str] = Field(default=None, alias="FiberImplant1")
    fiber_implant1_dv: Optional[str] = Field(
        default=None, alias="FiberImplant1DV"
    )
    fiber_implant2: Optional[str] = Field(default=None, alias="FiberImplant2")
    fiber_implant2_dv: Optional[str] = Field(
        default=None, alias="FiberImplant2DV"
    )
    file_system_object_type: Optional[int] = Field(
        default=None, alias="FileSystemObjectType"
    )
    first_inj_recovery: Optional[int] = Field(
        default=None, alias="FirstInjRecovery"
    )
    first_injection_iso_duration: Optional[float] = Field(
        default=None, alias="FirstInjectionIsoDuration"
    )
    first_injection_weight_after: Optional[float] = Field(
        default=None, alias="FirstInjectionWeightAfter"
    )
    first_injection_weight_before: Optional[float] = Field(
        default=None, alias="FirstInjectionWeightBefor"
    )
    first_round_ionto_issue: Optional[str] = Field(
        default=None, alias="FirstRoundIontoIssue"
    )
    guid: Optional[str] = Field(default=None, alias="GUID")
    hp_durotomy: Optional[str] = Field(default=None, alias="HPDurotomy")
    hp_iso_level: Optional[float] = Field(default=None, alias="HPIsoLevel")
    hp_recovery: Optional[float] = Field(default=None, alias="HPRecovery")
    hp_requestor_comments_plaintext: Optional[str] = Field(
        default=None, alias="HPRequestorCommentsPlaintext"
    )
    hp_surgeon_comments: Optional[str] = Field(
        default=None, alias="HPSurgeonComments"
    )
    hp_ap: Optional[float] = Field(default=None, alias="HP_x0020_A_x002f_P")
    hp_diameter: Optional[float] = Field(
        default=None, alias="HP_x0020_Diameter"
    )
    hp_ml: Optional[float] = Field(default=None, alias="HP_x0020_M_x002f_L")
    hp_inj: Optional[str] = Field(
        default=None, alias="HP_x0020__x0026__x0020_Inj"
    )
    headpost_type: Optional[str] = Field(default=None, alias="HeadpostType")
    hemisphere_2nd_inj: Optional[str] = Field(
        default=None, alias="Hemisphere2ndInj"
    )
    hp_loc: Optional[str] = Field(default=None, alias="HpLoc")
    hp_perf: Optional[str] = Field(default=None, alias="HpPerf")
    hp_prev_inject: Optional[str] = Field(default=None, alias="HpPrevInject")
    hp_work_station: Optional[str] = Field(default=None, alias="HpWorkStation")
    iacuc_protocol: Optional[str] = Field(
        default=None, alias="IACUC_x0020_Protocol_x0020__x002"
    )
    id1: Optional[int] = Field(default=None, alias="ID")
    id2: Optional[int] = Field(default=None, alias="Id")
    implant_id_coverslip_type: Optional[Tuple[float, Optional[str]]] = Field(
        default=None, alias="ImplantIDCoverslipType"
    )
    inj1_alternating_time: Optional[str] = Field(
        default=None, alias="Inj1AlternatingTime"
    )
    inj1_angle_v2: Optional[float] = Field(default=None, alias="Inj1Angle_v2")
    inj1_current: Optional[float] = Field(default=None, alias="Inj1Current")
    inj1_length_of_time: Optional[float] = Field(
        default=None, alias="Inj1LenghtofTime"
    )
    inj1_round: Optional[str] = Field(default=None, alias="Inj1Round")
    inj1_storage_location: Optional[str] = Field(
        default=None, alias="Inj1StorageLocation"
    )
    inj1_type: Optional[str] = Field(default=None, alias="Inj1Type")
    inj1_virus_strain_rt: Optional[str] = Field(
        default=None, alias="Inj1VirusStrain_rt"
    )
    inj1_vol: Optional[float] = Field(default=None, alias="Inj1Vol")
    inj1_angle0: Optional[float] = Field(default=None, alias="Inj1angle0")
    inj2_alternating_time: Optional[str] = Field(
        default=None, alias="Inj2AlternatingTime"
    )
    inj2_angle_v2: Optional[float] = Field(default=None, alias="Inj2Angle_v2")
    inj2_current: Optional[float] = Field(default=None, alias="Inj2Current")
    inj2_length_of_time: Optional[float] = Field(
        default=None, alias="Inj2LenghtofTime"
    )
    inj2_round: Optional[str] = Field(default=None, alias="Inj2Round")
    inj2_storage_location: Optional[str] = Field(
        default=None, alias="Inj2StorageLocation"
    )
    inj2_type: Optional[str] = Field(default=None, alias="Inj2Type")
    inj2_virus_strain_rt: Optional[str] = Field(
        default=None, alias="Inj2VirusStrain_rt"
    )
    inj2_vol: Optional[float] = Field(default=None, alias="Inj2Vol")
    inj2_angle0: Optional[float] = Field(default=None, alias="Inj2angle0")
    ionto_number_hpinj: Optional[str] = Field(
        default=None, alias="IontoNumberHPINJ"
    )
    ionto_number_inj1: Optional[str] = Field(
        default=None, alias="IontoNumberHPINJ"
    )
    ionto_number_inj2: Optional[str] = Field(
        default=None, alias="IontoNumberHPINJ"
    )
    iso_on: Optional[float] = Field(default=None, alias="Iso_x0020_On")
    issue: Optional[str] = Field(default=None, alias="Issue")
    lims_link: Optional[str] = Field(default=None, alias="LIMS_x0020_link")
    lims_task_flow1: Optional[str] = Field(default=None, alias="LIMStaskflow1")
    lims_required: Optional[str] = Field(
        default=None, alias="LIMs_x0020_Required"
    )
    labtracks_group: Optional[str] = Field(
        default=None, alias="LabTracks_x0020_Group"
    )
    labtracks_id: Optional[str] = Field(
        default=None, alias="LabTracks_x0020_ID"
    )
    labtracks_requestor: Optional[str] = Field(
        default=None, alias="LabTracks_x0020_Requestor"
    )
    light_cycle: Optional[str] = Field(default=None, alias="Light_x0020_Cycle")
    lims_project_code: Optional[str] = Field(
        default=None, alias="Lims_x0020_Project_x0020_Code"
    )
    long_1st_round_inj_cmts: Optional[str] = Field(
        default=None, alias="Long1stRoundInjCmts"
    )
    long_2nd_rnd_inj_cmts: Optional[str] = Field(
        default=None, alias="Long2ndRndInjCmts"
    )
    long_requestor_comments: Optional[str] = Field(
        default=None, alias="LongRequestorComments"
    )
    long_surgeon_comments: Optional[str] = Field(
        default=None, alias="LongSurgeonComments"
    )
    ml_2nd_inj: Optional[float] = Field(default=None, alias="ML2ndInj")
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
    odata_hp_requestor: Optional[str] = Field(
        default=None, alias="OData__x0031_HP_x0020_Requestor_x0020_"
    )
    piid: Optional[int] = Field(default=None, alias="PIId")
    pi_string_id: Optional[str] = Field(default=None, alias="PIStringId")
    pedigree_name: Optional[str] = Field(default=None, alias="PedigreeName")
    procedure: Optional[str] = Field(default=None, alias="Procedure")
    project_id_te: Optional[str] = Field(
        default=None, alias="Project_x0020_ID_x0020__x0028_te"
    )
    round1_inj_iso_level: Optional[float] = Field(
        default=None, alias="Round1InjIsolevel"
    )
    round2_inj_iso_level: Optional[float] = Field(
        default=None, alias="Round2InjIsolevel"
    )
    scabbing: Optional[str] = Field(default=None, alias="Scabbing")
    second_inj_recovery: Optional[int] = Field(
        default=None, alias="SecondInjRecover"
    )
    second_injection_iso_duration: Optional[float] = Field(
        default=None, alias="SecondInjectionIsoDuration"
    )
    second_injection_weight_after: Optional[float] = Field(
        default=None, alias="SecondInjectionWeightAfter"
    )
    second_injection_weight_before: Optional[float] = Field(
        default=None, alias="SecondInjectionWeightBefore"
    )
    second_round_ionto_issue: Optional[str] = Field(
        default=None, alias="SecondRoundIontoIssue"
    )
    server_redirected_embed_uri: Optional[str] = Field(
        default=None, alias="ServerRedirectedEmbedUri"
    )
    server_redirected_embed_url: Optional[str] = Field(
        default=None, alias="ServerRedirectedEmbedUrl"
    )
    start_of_week: Optional[datetime] = Field(
        default=None, alias="Start_x0020_Of_x0020_Week"
    )
    surgery_status: Optional[str] = Field(default=None, alias="SurgeryStatus")
    test_1st_round_id: Optional[int] = Field(
        default=None, alias="TEST_x0020_1st_x0020_Round_x0020Id"
    )
    test_1st_round_string_id: Optional[str] = Field(
        default=None, alias="TEST_x0020_1st_x0020_Round_x0020StringId"
    )
    test_2nd_round_id: Optional[int] = Field(
        default=None, alias="TEST_x0020_2nd_x0020_Round_x0020Id"
    )
    test_2nd_round_string_id: Optional[str] = Field(
        default=None, alias="TEST_x0020_2nd_x0020_Round_x0020StringId"
    )
    test1_id: Optional[int] = Field(default=None, alias="Test1Id")
    test1_string_id: Optional[str] = Field(default=None, alias="Test1StringId")
    title: Optional[str] = Field(default=None, alias="Title")
    touch_up_status: Optional[str] = Field(
        default=None, alias="Touch_x0020_Up_x0020_Status"
    )
    touch_up_surgeon_id: Optional[int] = Field(
        default=None, alias="Touch_x0020_Up_x0020_SurgeonId"
    )
    touch_up_surgeon_string_id: Optional[str] = Field(
        default=None, alias="Touch_x0020_Up_x0020_SurgeonStringId"
    )
    touch_up_weight: Optional[float] = Field(
        default=None, alias="Touch_x0020_Up_x0020_Weight_x002"
    )
    touch_up_comp: Optional[str] = Field(
        default=None, alias="Touch_x0020_Up_x0020__x0020_Comp"
    )
    virus_ap: Optional[Tuple[float, Optional[str]]] = Field(
        default=None, alias="Virus_x0020_A_x002f_P"
    )
    virus_dv: Optional[Tuple[float, Optional[str]]] = Field(
        default=None, alias="Virus_x0020_D_x002f_V"
    )
    virus_hemisphere: Optional[str] = Field(
        default=None, alias="Virus_x0020_Hemisphere"
    )
    virus_ml: Optional[Tuple[float, Optional[str]]] = Field(
        default=None, alias="Virus_x0020_M_x002f_L"
    )
    weight_after_surgery: Optional[float] = Field(
        default=None, alias="Weight_x0020_after_x0020_Surgery"
    )
    weight_before_surgery: Optional[float] = Field(
        default=None, alias="Weight_x0020_before_x0020_Surger"
    )
    workstation_1st_injection: Optional[str] = Field(
        default=None, alias="WorkStation1stInjection"
    )
    workstation_2nd_injection: Optional[str] = Field(
        default=None, alias="WorkStation2ndInjection"
    )
    # The rest of these fields seem like legacy mistakes
    field30: Optional[float] = Field(default=None, alias="field30")
    field50: Optional[float] = Field(default=None, alias="field50")
    inj1_vol_per_depth: Optional[float] = Field(
        default=None, alias="inj1volperdepth"
    )
    inj2_vol_per_depth: Optional[float] = Field(
        default=None, alias="inj2volperdepth"
    )
    nd_round_injection_comments: Optional[str] = Field(
        default=None, alias="ndRoungInjectionComments"
    )
    ret_setting0: Optional[str] = Field(default=None, alias="retSetting0")
    ret_setting1: Optional[str] = Field(default=None, alias="retSetting1")
    st_round_injection_comments: Optional[str] = Field(
        default=None, alias="stRoundInjectionComments"
    )

    @validator(
        "age_at_injection",
        "breg_2_lamb",
        "dv_2nd_inj",
        "first_injection_iso_duration",
        "first_injection_weight_after",
        "first_injection_weight_before",
        "hp_iso_level",
        "hp_recovery",
        "hp_ap",
        "hp_diameter",
        "hp_ml",
        "inj1_vol",
        "inj2_vol",
        "ml_2nd_inj",
        "round1_inj_iso_level",
        "round2_inj_iso_level",
        "second_injection_iso_duration",
        "second_injection_weight_after",
        "second_injection_weight_before",
        "touch_up_weight",
        "weight_after_surgery",
        "weight_before_surgery",
        "field30",
        "field50",
        "inj1_vol_per_depth",
        "inj2_vol_per_depth",
        pre=True,
    )
    def parse_basic_num_str_to_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        pattern = r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))"
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1)
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    @validator(
        "cage",
        "com_after_1st_inj",
        "com_after_2nd_inj",
        "com_coplanar",
        "com_damage",
        "com_during_1st_inj",
        "com_during_2nd_inj",
        "com_durotomy",
        "com_sinusbleed",
        "com_swelling",
        "com_window",
        "compliance_asset_id",
        "content_type_id",
        "contusion",
        "exudate_severity",
        "eye_affected",
        "eye_issue",
        "fiber_implant1",
        "fiber_implant1_dv",
        "fiber_implant2",
        "fiber_implant2_dv",
        "first_round_ionto_issue",
        "guid",
        "hp_durotomy",
        "hp_requestor_comments_plaintext",
        "hp_surgeon_comments",
        "hp_inj",
        "headpost_type",
        "hemisphere_2nd_inj",
        "hp_loc",
        "hp_perf",
        "hp_prev_inject",
        "hp_work_station",
        "iacuc_protocol",
        "inj1_alternating_time",
        "inj1_round",
        "inj1_storage_location",
        "inj1_type",
        "inj1_virus_strain_rt",
        "inj2_alternating_time",
        "inj2_round",
        "inj2_storage_location",
        "inj2_type",
        "inj2_virus_strain_rt",
        "ionto_number_hpinj",
        "ionto_number_inj1",
        "ionto_number_inj2",
        "issue",
        "lims_link",
        "lims_task_flow1",
        "lims_required",
        "labtracks_group",
        "labtracks_id",
        "labtracks_requestor",
        "light_cycle",
        "lims_project_code",
        "long_1st_round_inj_cmts",
        "long_2nd_rnd_inj_cmts",
        "long_requestor_comments",
        "long_surgeon_comments",
        "nanoject_number_inj10",
        "nanoject_number_inj2",
        "odata_ui_version_string",
        "odata_hp_requestor",
        "pi_string_id",
        "pedigree_name",
        "procedure",
        "project_id_te",
        "scabbing",
        "second_round_ionto_issue",
        "surgery_status",
        "touch_up_status",
        "touch_up_surgeon_string_id",
        "virus_hemisphere",
        "workstation_1st_injection",
        "workstation_2nd_injection",
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
        "implant_id_coverslip_type",
        "virus_ap",
        "virus_dv",
        "virus_ml",
        pre=True,
    )
    def parse_numeric_with_notes(
        cls, v: Union[str, None]
    ) -> Optional[Tuple[float, Optional[str]]]:
        """Match like '0.25' or '-4.72, rostral to lambda' or
        '5mm stacked coverslip' or '30 degrees'"""
        pattern1 = r"^([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))$"
        pattern2 = r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))([,\w].*)"
        if type(v) is str and re.match(pattern1, v):
            return re.match(pattern1, v).group(1), None
        elif type(v) is str and re.match(pattern2, v):
            return (
                re.match(pattern2, v).group(1),
                re.match(pattern2, v).group(2),
            )
        else:
            return None

    @validator("craniotomy_type", pre=True)
    def parse_string_with_numeric(
        cls, v: Optional[str]
    ) -> Optional[Tuple[str, float]]:
        """Match like 'Visual Cortex 5mm'"""
        pattern = r"(.*)\s+(\d+)mm$"
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1), re.match(pattern, v).group(2)
        else:
            return None

    @validator(
        "inj1_angle_v2",
        "inj1_angle0",
        "inj2_angle_v2",
        "inj2_angle0",
        pre=True,
    )
    def parse_angle_str_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
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

    @validator("inj1_current", "inj2_current", pre=True)
    def parse_current_str_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        pattern = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))(\s*uA\s*)*$"
        )
        if type(v) is str and re.match(pattern, v):
            return re.match(pattern, v).group(1)
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    @validator("inj1_length_of_time", "inj2_length_of_time", pre=True)
    def parse_time_length_str_float(
        cls, v: Union[str, int, float, None]
    ) -> Optional[float]:
        pattern1 = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))\s*"
            r"(?:min|mins|minute|minutes){0,1}\s*$"
        )
        pattern2 = (
            r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))\s*"
            r"(?:min|mins|minute|minutes){1}\s*(\d+)"
            r"(?:sec|secs|second|seconds)(?:/depth|/location)*$"
        )
        if type(v) is str and re.match(pattern1, v):
            return re.match(pattern1, v).group(1)
        elif type(v) is str and re.match(pattern2, v):
            minutes = re.match(pattern2, v).group(1)
            seconds = re.match(pattern2, v).group(2)
            total_time = (
                float(minutes) + (float(seconds) / 60)
                if float(minutes) > 0
                else float(minutes) - (float(seconds) / 60)
            )
            return total_time
        elif type(v) is int or type(v) is float:
            return v
        else:
            return None

    def has_hp_procedure(self):
        return "HP" in self.procedure

    def has_inj_procedure(self):
        return "INJ" in self.procedure or "Injection" in self.procedure

