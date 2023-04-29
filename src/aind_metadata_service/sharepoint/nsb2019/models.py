"""Data Models for NSB 2019 Sharepoint ListItem"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Extra, Field, SecretStr, validator


class After1StInjection(Enum):
    BLEEDING = "Bleeding"
    BLEEDINGFLUID_COMING_UP = "Bleeding/Fluid coming up"
    FLUID_COMING_UP = "Fluid coming up"
    NA = "N/A"
    NO_ISSUES = "No Issues"
    SELECT = "Select..."
    SWELLING = "Swelling"


class After2NdInjection(Enum):
    BLEEDING = "Bleeding"
    BLEEDINGFLUID_COMING_UP = "Bleeding/Fluid coming up"
    FLUID_COMING_UP = "Fluid coming up"
    NA = "N/A"
    NO_ISSUES = "No Issues"
    SELECT = "Select..."
    SWELLING = "Swelling"


class Contusion(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NA = "N/A"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class CraniotomyType(Enum):
    FRONTAL_WINDOW_3MM = "Frontal Window 3mm"
    SELECT = "Select..."
    VISUAL_CORTEX_5MM = "Visual Cortex 5mm"
    WHC_2P = "WHC 2P"
    WHC_NP = "WHC NP"


class During1StInjection(Enum):
    BLEEDING = "Bleeding"
    BLEEDINGFLUID_COMING = "Bleeding/Fluid coming"
    FLUID_COMING_UP = "Fluid coming up"
    NA = "N/A"
    NO_ISSUES = "No Issues"
    PIPETTE_CLOGGEDBROKE_TIP = "Pipette clogged/broke tip"
    SELECT = "Select..."
    SWELLING = "Swelling"


class During2NdInjection(Enum):
    BLEEDING = "Bleeding"
    BLEEDINGFLUID_COMING_UP = "Bleeding/Fluid coming up"
    FLUID_COMING_UP = "Fluid coming up"
    NA = "N/A"
    NO_ISSUES = "No Issues"
    PIPETTE_CLOGGEDBROKE_TIP = "Pipette clogged/broke tip"
    SELECT = "Select..."
    SWELLING = "Swelling"


class Durotomy(Enum):
    COMPLETE = "Complete"
    NA = "N/A"
    NO = "No"
    PARTIAL = "Partial"
    SELECT = "Select..."
    TORN__COMPLETE = "Torn & Complete"
    UNINTENTIONAL = "Unintentional"


class EdemaSwelling(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NA = "N/A"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class ExudateSeverity(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class EyeAffected(Enum):
    BOTH = "Both"
    LEFT = "Left"
    NEITHER = "Neither"
    RIGHT = "Right"
    SELECT = "Select..."


class EyeIssue(Enum):
    CLOUDPOSSIBLY_BLIND = "Cloud/Possibly Blind"
    NONE = "None"
    OTHERSEE_COMMENTS = "Other...(See comments)"
    PUFFYSWOLLEN = "Puffy/Swollen"
    SELECT = "Select..."
    SLIGHTLY_CLOSED = "Slightly Closed"
    WEEPY = "Weepy"


class FirstRoundInjIsoLevel(Enum):
    N_025 = "0.25"
    N_050 = "0.50"
    N_075 = "0.75"
    N_100 = "1.00"
    N_125 = "1.25"
    N_150 = "1.50"
    N_175 = "1.75"
    N_200 = "2.00"
    N_225 = "2.25"
    N_250 = "2.50"
    N_275 = "2.75"
    N_300 = "3.00+"
    SELECT = "Select..."


class FirstRoundInjWorkstation(Enum):
    SELECT = "Select..."
    SWS_1 = "SWS 1"
    SWS_2 = "SWS 2"
    SWS_3 = "SWS 3"
    SWS_4 = "SWS 4"
    SWS_5 = "SWS 5"
    SWS_6 = "SWS 6"
    SWS_7 = "SWS 7"
    SWS_8 = "SWS 8"
    SWS_9 = "SWS 9"


class Firstroundiontoissue(Enum):
    NA = "N/A"
    NO = "No"
    SELECT = "Select..."
    YES = "Yes"


class Firstroundiontonumber(Enum):
    IONTO_1 = "Ionto #1"
    IONTO_10 = "Ionto #10"
    IONTO_2 = "Ionto #2"
    IONTO_3 = "Ionto #3"
    IONTO_4 = "Ionto #4"
    IONTO_5 = "Ionto #5"
    IONTO_6 = "Ionto #6"
    IONTO_7 = "Ionto #7"
    IONTO_8 = "Ionto #8"
    IONTO_9 = "Ionto #9"
    NA = "N/A"
    SELECT = "Select..."


class Firstroundnanojectnumber(Enum):
    NA = "N/A"
    NJ1 = "NJ#1"
    NJ2 = "NJ#2"
    NJ3 = "NJ#3"
    NJ4 = "NJ#4"
    NJ5 = "NJ#5"
    NJ6 = "NJ#6"
    NJ7 = "NJ#7"
    NJ8 = "NJ#8"
    SELECT = "Select..."


class HeadpostType(Enum):
    AI_STRAIGHT_HEADBAR = "AI Straight Headbar"
    CAMSTYLE_HEADFRAME_016010010_REV_A = (
        "CAM-style headframe (0160-100-10 Rev A)"
    )
    MESOSCOPESTYLE_WELL_WITH_NGCSTYLE_HEADFRAME_016020020016010010 = (
        "Mesoscope-style well with NGC-style headframe "
        "(0160-200-20/0160-100-10)"
    )
    NEUROPIXELSTYLE_HEADFRAME_016010010016020036 = (
        "Neuropixel-style headframe (0160-100-10/0160-200-36)"
    )
    NGCSTYLE_HEADFRAME_NO_WELL_016010010 = (
        "NGC-style headframe, no well (0160-100-10)"
    )
    SELECT = "Select..."
    WHC_42_WITH_NEUROPIXEL_WELL_AND_WELL_CAP = (
        "WHC #42 with Neuropixel well and well cap"
    )


class Hematoma(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NA = "N/A"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class HpDurotomy(Enum):
    NO = "No"
    SELECT = "Select..."
    YES = "Yes"


class HpIsoLevel(Enum):
    N_025 = "0.25"
    N_050 = "0.50"
    N_075 = "0.75"
    N_100 = "1.00"
    N_125 = "1.25"
    N_15 = "1.5"
    N_175 = "1.75"
    N_200 = "2.00"
    N_225 = "2.25"
    N_250 = "2.50"
    N_275 = "2.75"
    N_300 = "3.00+"
    SELECT = "Select..."


class HpLocation(Enum):
    CENTER = "Center"
    LEFT = "Left"
    RIGHT = "Right"
    SELECT = "Select..."


class HpPerferations(Enum):
    LEFT = "Left"
    NA = "NA"
    RIGHT = "Right"
    SELECT_IF_APPLICABLE = "Select if applicable..."


class HpWorkStation(Enum):
    SELECT = "Select..."
    SWS_1 = "SWS 1"
    SWS_2 = "SWS 2"
    SWS_3 = "SWS 3"
    SWS_4 = "SWS 4"
    SWS_5 = "SWS 5"
    SWS_6 = "SWS 6"
    SWS_7 = "SWS 7"
    SWS_8 = "SWS 8"
    SWS_9 = "SWS 9"


class IacucProtocol(Enum):
    N_2001 = "2001"
    N_2002 = "2002"
    N_2003 = "2003"
    N_2004 = "2004"
    N_2005 = "2005"
    N_2006 = "2006"
    N_2011 = "2011"
    N_2102 = "2102"
    N_2103 = "2103"
    N_2104 = "2104"
    N_2105 = "2105"
    N_2106 = "2106"
    N_2107 = "2107"
    N_2108 = "2108"
    N_2109 = "2109"
    N_2110 = "2110"
    N_2113 = "2113"
    N_2115 = "2115"
    N_2117 = "2117"
    N_2201 = "2201"
    N_2202 = "2202"
    N_2205 = "2205"
    N_2212 = "2212"
    SELECT = "Select..."


class ImplantIdCoverslipType(Enum):
    CUSTOM_IMPLANT_ADD_DETAILS_IN_COMMENTS_SECTION = (
        "Custom Implant (add details in comments section)"
    )
    N_2001 = "2001"
    N_2002 = "2002"
    N_3001 = "3001"
    N_5MM_STACKED_COVERSLIP = "5mm stacked coverslip"
    N_5MM_STACKED_COVERSLIP_WITH_SILICONE_COATING_FOR_NEUROPIXEL = (
        "5mm stacked coverslip (with silicone coating for Neuropixel)"
    )
    SELECT = "Select..."


class Inj1Angle(Enum):
    N_0_DEGREES = "0 degrees"
    N_10_DEGREES = "10 degrees"
    N_15_DEGREES = "15 degrees"
    N_20_DEGREES = "20 degrees"
    N_30_DEGREES = "30 degrees"
    N_40_DEGREES = "40 degrees"
    SELECT = "Select..."


class Inj1Hemisphere(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    SELECT = "Select..."


class Inj1Retsetting(Enum):
    OFF = "Off"
    ON = "On"


class Inj1Round(Enum):
    NA = "NA"
    N_1ST = "1st"
    N_2ND = "2nd"
    SELECT = "Select..."


class Inj1Type(Enum):
    IONTOPHORESIS = "Iontophoresis"
    NANOJECT_PRESSURE = "Nanoject (Pressure)"
    SELECT = "Select..."


class Inj2Angle(Enum):
    N_0_DEGREES = "0 degrees"
    N_10_DEGREES = "10 degrees"
    N_15_DEGREES = "15 degrees"
    N_20_DEGREES = "20 degrees"
    N_30_DEGREES = "30 degrees"
    N_40_DEGREES = "40 degrees"
    SELECT = "Select..."


class Inj2Hemisphere(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    SELECT = "Select..."


class Inj2Retsetting(Enum):
    OFF = "Off"
    ON = "On"


class Inj2Round(Enum):
    NA = "NA"
    N_1ST = "1st"
    N_2ND = "2nd"
    SELECT = "Select..."


class Inj2Type(Enum):
    IONTOPHORESIS = "Iontophoresis"
    NANOJECT_PRESSURE = "Nanoject (Pressure)"
    SELECT = "Select..."


class Iontonumberhpinj(Enum):
    IONTO_1 = "Ionto #1"
    IONTO_2 = "Ionto #2"
    IONTO_3 = "Ionto #3"
    IONTO_4 = "Ionto #4"
    IONTO_5 = "Ionto #5"
    IONTO_6 = "Ionto #6"
    IONTO_7 = "Ionto #7"
    IONTO_8 = "Ionto #8"
    IONTO_9 = "Ionto #9"


class Issue(Enum):
    EXUDATE = "Exudate"
    EYE_ISSUE = "Eye Issue"
    METABOND = "Metabond"
    MULTIPLE_ISSUES_NOTES_IN_COMMENTS = "Multiple Issues (Notes In comments)"
    NONSURGICAL_ISSUE = "Non-Surgical Issue"
    OTHERWRITE_IN_COMMENTS = "Other..(write in comments)"
    REPLACEMENT_COVERSLIP = "Replacement: Coverslip"
    REPLACEMENT_KWIKCAST = "Replacement: Kwikcast"
    REPLACEMENT_ORING = "Replacement: O-ring"
    SCABBING = "Scabbing"
    SELECT = "Select..."
    ZMOTION = "Z-Motion"


class Laceration(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NA = "N/A"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class LightCycle(Enum):
    NORMAL_6AM_TO_8PM = "Normal (6am to 8pm)"
    REVERSE_9PM_TO_9AM = "Reverse (9pm to 9am)"
    SELECT = "Select..."


class LimsProjectCode(Enum):
    AINDDISCOVERY = "aind-discovery"
    AINDEPHYS = "aind-ephys"
    AINDMSMA = "aind-msma"
    AINDOPHYS = "aind-ophys"
    BRAINTVVIRALSTRATEGIES = "BraintvViralStrategies"
    CELLTYPESTRANSGENICCHARACTERIZATIONGCAMP = (
        "CelltypesTransgenicCharacterizationGCaMP"
    )
    CITRICACIDPILOT = "Citricacidpilot"
    DYNAMICROUTINGBEHAVIORDEV = "DynamicRoutingBehaviorDev"
    DYNAMICROUTINGSURGICALDEVELOPMENT = "DynamicRoutingSurgicalDevelopment"
    DYNAMICROUTINGTASK1PRODUCTION = "DynamicRoutingTask1Production"
    DYNAMICROUTINGULTRAOPTOTAGGINGBEHAVIOR = (
        "DynamicRoutingUltraOptotaggingBehavior"
    )
    ISIX = "ISIx"
    LEARNINGMFISHDEVELOPMENT = "LearningmFISHDevelopment"
    LEARNINGMFISHTASK1A = "LearningmFISHTask1A"
    MINDSCOPETRANSGENICCHARACTERIZATIONGCAMP = (
        "MindscopeTransgenicCharacterizationGCaMP"
    )
    MIVSCCMET = "mIVSCC-MET"
    MIVSCCMETX = "mIVSCC-METx"
    MMPATCH = "mMPatch"
    MMPATCHX = "mMPATCHx"
    MOUSEBRAINCELLATLASTRANSSYNAPTIC = "MouseBrainCellAtlasTranssynaptic"
    MOUSEGENETICTOOLSPROJECTIONMAPPING = "MouseGeneticToolsProjectionMapping"
    OMFISHCOREGISTRATIONPILOT = "omFISHcoregistrationpilot"
    OMFISHCUX2MESO = "omFISHCux2Meso"
    OMFISHGAD2MESO = "omFISHGad2Meso"
    OMFISHGAD2PILOT = "omFISHGad2Pilot"
    OMFISHROBINJECTIONVIRUSPILOT = "omFISHROBinjectionviruspilot"
    OMFISHRORBPILOT = "omFISHRorbPilot"
    OPENSCOPEDENDRITECOUPLING = "OpenScopeDendriteCoupling"
    OPENSCOPEDEVELOPMENT = "OpenscopeDevelopment"
    OPENSCOPEGLOBALLOCALODDBALL = "OpenScopeGlobalLocalOddball"
    OPENSCOPEILLUSION = "OpenScopeIllusion"
    OPENSCOPEINJECTIONPILOT = "OpenScopeInjectionPilot"
    SELECT = "Select..."
    SURGERYX = "SurgeryX"
    T301T = "T301t"
    TASKTRAINEDNETWORKSMULTISCOPE = "TaskTrainedNetworksMultiscope"
    TASKTRAINEDNETWORKSNEUROPIXEL = "TaskTrainedNetworksNeuropixel"
    TINYBLUEDOTBEHAVIOR = "TinyBlueDotBehavior"
    VARIABILITYAIM1 = "VariabilityAim1"
    VARIABILITYAIM1PILOT = "VariabilityAim1Pilot"
    VARIABILITYSPONTANEOUS = "VariabilitySpontaneous"
    VIPAXONALV1PHASE1 = "VipAxonalV1Phase1"
    VIPSOMATICV1MESO = "VIPSomaticV1Meso"
    VIPSOMATICV1PHASE1 = "VipSomaticV1Phase1"
    VIPSOMATICV1PHASE2 = "VipSomaticV1Phase2"


class LimsRequired(Enum):
    NO = "No"
    SELECT = "Select..."
    YES = "Yes"


class Limstaskflow(Enum):
    AIND_EPHYS_PASSIVE_BEHAVIOR = "AIND Ephys (Passive Behavior)"
    AIND_EPHYS_SURGERY_ONLY = "AIND Ephys (Surgery only)"
    AIND_U19_THALAMUS = "AIND U19 Thalamus"
    BRAIN_LARGE_SCALE_RECORDING = "BRAIN Large Scale Recording"
    BRAIN_MOUSE_BRAIN_CELL_ATLAS_TRANSSYNAPTIC = (
        "BRAIN Mouse Brain Cell Atlas trans-synaptic"
    )
    BRAIN_OBSERVATORY_TRANSGENIC_CHARACTERIZATION = (
        "Brain Observatory Transgenic Characterization"
    )
    BTV_BRAIN_VIRAL_STRATEGIES = "BTV BRAIN Viral Strategies"
    CITRIC_ACID_PILOT = "Citric Acid Pilot"
    EPHYS_TASK_DEV_DYNAMIC_ROUTING_NSB_BEH = (
        "Ephys Task Dev Dynamic Routing (NSB Beh)"
    )
    EPHYS_TASK_DEV_DYNAMIC_ROUTING_SC_BEH = (
        "Ephys Task Dev Dynamic Routing (S/C Beh)"
    )
    EPHYS_TAS_DEV_DYNAMIC_ROUTING_DOC_LEFT_EYE = (
        "Ephys Tas Dev Dynamic Routing DOC Left Eye"
    )
    IVSCCM_INJECTION = "IVSCCm injection"
    IVSCC_HVA_RETRO_PATCHSEQ = "IVSCC HVA Retro PatchSeq"
    IVSPCM_INJECTION = "IVSPCm Injection"
    MGT_ANTEROGRADE_PROJECTION_MAPPING = "MGT Anterograde Projection Mapping"
    MGT_LAB = "MGT Lab"
    MGT_TISSUECYTE = "MGT TissueCyte"
    MSP_DYNAMIC_ROUTING_SURGICAL_DEVELOPMENT = (
        "MSP Dynamic Routing Surgical Development"
    )
    MSP_DYNAMIC_ROUTING_TASK_1_PRODUCTION = (
        "MSP Dynamic Routing Task 1 Production"
    )
    MSP_DYNAMIC_ROUTING_ULTRA_OPTOTAGGING_BEHAVIOR = (
        "MSP Dynamic Routing Ultra Optotagging Behavior"
    )
    MSP_LEARNING__MFISH_DEVELOPMENT = "MSP Learning & mFISH Development"
    MSP_LEARNING__MFISH_DEVELOPMENT_DOX = (
        "MSP Learning & mFISH Development (Dox)"
    )
    MSP_LEARNING__MFISH_FRONTAL_WINDOW_DEV = (
        "MSP Learning & mFISH Frontal Window Dev"
    )
    MSP_LEARNING__MFISH_VIRUS_TESTING = "MSP Learning & mFISH Virus Testing"
    MSP_OMFISH_COREGISTRATION_PILOT = "MSP omFISH Co-Registration Pilot"
    MSP_OMFISH_CUX2_PILOT = "MSP omFISH Cux2 Pilot"
    MSP_OMFISH_GAD2_PILOT = "MSP omFISH Gad2 Pilot"
    MSP_OMFISH_ROB_INJECTION_VIRUS_PILOT = (
        "MSP omFISH ROB Injection Virus Pilot"
    )
    MSP_OMFISH_RORB_PILOT = "MSP omFISH Rorb Pilot"
    MSP_OPENSCOPE_DENDRITE_COUPLING = "MSP OpenScope Dendrite Coupling"
    MSP_OPENSCOPE_GLOBAL_LOCAL_ODDBALLS_COHORT_1 = (
        "MSP OpenScope Global Local Oddballs (Cohort 1)"
    )
    MSP_OPENSCOPE_GLOBAL_LOCAL_ODDBALLS_COHORT_2 = (
        "MSP OpenScope Global Local Oddballs (Cohort 2)"
    )
    MSP_OPENSCOPE_ILLUSION = "MSP OpenScope Illusion"
    MSP_TASK_TRAINED_NETWORKS_MULTISCOPE = (
        "MSP Task Trained Networks Multiscope"
    )
    MSP_TASK_TRAINED_NETWORKS_NEUROPIXEL = (
        "MSP Task Trained Networks Neuropixel"
    )
    MSP_VARIABILITY_AIM_1 = "MSP Variability Aim 1"
    MSP_VARIABILITY_AIM_1_PILOT = "MSP Variability Aim 1 Pilot"
    MSP_VARIABILITY_SPONTANEOUS = "MSP Variability Spontaneous"
    MSP_VIP_AXONAL_V1 = "MSP VIP Axonal V1"
    MSP_VIP_SOMATIC_V1 = "MSP VIP Somatic V1"
    NA = "N/A"
    OPENSCOPE_VIRUS_VALIDATION = "Openscope Virus Validation"
    TINY_BLUE_DOT_BEHAVIOR = "Tiny Blue Dot Behavior"
    TRANSGENIC_CHARACTERIZATION_PASSIVE = (
        "Transgenic Characterization (Passive)"
    )
    VGT_ENHANCERS_TRANSSYNAPTIC = "VGT Enhancers Transsynaptic"


class PreviouslyInjected(Enum):
    NO = "No"
    SELECT = "Select..."
    YES = "Yes"


class Procedure(Enum):
    CUSTOM = "Custom"
    HPC_CAM = "HP+C CAM"
    HPC_MULTISCOPE = "HP+C Multiscope"
    HPC_NEUROPIXEL_STYLE = "HP+C Neuropixel style"
    HPINJ = "HP+INJ"
    HPINJECTIONOPTIC_FIBER_IMPLANT = "HP+Injection+Optic Fiber Implant"
    HP_ONLY = "HP only"
    HP_TRANSCRANIAL_FOR_ISI = "HP Transcranial (for ISI)"
    INJHPC = "INJ+HP+C"
    INJWHC_NP = "INJ+WHC NP"
    SELECT = "Select..."
    STEREOTAXIC_INJECTION = "Stereotaxic Injection"
    TRAINING_SURGERY = "Training Surgery"
    WHC_NP = "WHC NP"


class ProjectId(Enum):
    CAMC506 = "CAM-C506"
    CONT503 = "CON-T503"
    CTYT504 = "CTY-T504"
    LOCC500 = "LOC-C500"
    N_1020100910_CTYMORPHOLOGY = "102-01-009-10: CTY-Morphology"
    N_1020101010_CTYSYNAPTIC_PHYS = "102-01-010-10: CTY-Synaptic Phys"
    N_1020101410_CTY_GENTOOLS_MOUSE = "102-01-014-10: CTY GenTools Mouse"
    N_1020102120_CTYBRAIN_MOUSE_BRAIN_CELL_ATLAS_SEG_1 = (
        "102-01-021-20: CTY-BRAIN Mouse Brain Cell Atlas Seg 1"
    )
    N_1020102120_CTYBRAIN_MOUSE_BRAIN_CELL_ATLAS_SEG_2_ANATOMY = (
        "102-01-021-20: CTY-BRAIN Mouse Brain Cell Atlas Seg 2 Anatomy"
    )
    N_1020103620_DISSEMINATION_OF_3PHOTON_IMAGING = (
        "102-01-036-20 Dissemination of 3-photon Imaging"
    )
    N_1020104320_OPTICAL_INTERROGATION_OF_VENULAR_FUNCTION = (
        "102-01-043-20 Optical Interrogation of Venular Function"
    )
    N_1020104410_CTY_GENOMICS = "102-01-044-10 CTY Genomics"
    N_1020104510_IVSCC = "102-01-045-10 IVSCC"
    N_1020104720_3P_NHP_CORTICAL_IMAGING_R34 = (
        "102-01-047-20 3P NHP cortical imaging R34"
    )
    N_1020104810_CTY_BARCODED_CONNECTOMICS = (
        "102-01-048-10 CTY Barcoded Connectomics"
    )
    N_1020105520_CTY_EM_MOTOR_CORTEX = "102-01-055-20 CTY EM Motor Cortex"
    N_1020199910_CTY_PROGRAM_ADMIN = "102-01-999-10 CTY Program Admin"
    N_1020201220_BRAIN_VIRAL_STRATEGIES = (
        "102-02-012-20: BRAIN Viral Strategies"
    )
    N_1020201720_BRAIN_NEUROPIXELS_ULTRA = (
        "102-02-017-20 BRAIN Neuropixels Ultra"
    )
    N_1020400620_OTH_MEASURING_CONSCIOUSNESS = (
        "102-04-006-20: OTH Measuring Consciousness"
    )
    N_1020400710_TARGETED_CNS_GENE_THERAPY = (
        "102-04-007-10 Targeted CNS Gene Therapy"
    )
    N_1020401010_CTY_SR_SLC6A1 = "102-04-010-10 CTY SR: SLC6A1"
    N_1020401410_CTY_PARKINSONS_DISEASE = (
        "102-04-014-10 CTY Parkinsons Disease"
    )
    N_1028800410_XPG_CORE_VIRUS_PROD_TASK_CVS_PRODUCTION = (
        "102-88-004-10 XPG Core Virus Prod, Task: CVS Production"
    )
    N_1028800410_XPG_CORE_VIRUS_PROD_TASK_RD = (
        "102-88-004-10 XPG Core Virus Prod, Task: R&D"
    )
    N_1210100410_VIP_REGULATED_STABILIZED_NETWORKS = (
        "121-01-004-10 VIP Regulated Stabilized Networks"
    )
    N_1210100710_TASK_TRAINED_NETWORKS = "121-01-007-10 Task Trained Networks"
    N_1210100810_NEURAL_ENSEMBLE_VARIABILITY = (
        "121-01-008-10 Neural Ensemble Variability"
    )
    N_1210101010_V1_OMFISH = "121-01-010-10 V1 omFISH"
    N_1210101110_DYNAMIC_ROUTING = "121-01-011-10 Dynamic Routing"
    N_1210101210_LEARNING_MFISH = "121-01-012-10 Learning mFISH"
    N_1210101320_MSP_TEMPLETON = "121-01-013-20 MSP Templeton"
    N_1210101620_BRAIN_OPENSCOPE = "121-01-016-20 BRAIN OpenScope"
    N_1210102320_MSP_TEMPLETON__TESTING_THEORIES_OF_CONSCIOUSNESS = (
        "121-01-023-20 MSP Templeton - Testing Theories of Consciousness"
    )
    N_1210199910_MINDSCOPE_MSP_CROSS_PROGRAM = (
        "121-01-999-10 Mindscope (MSP) Cross Program"
    )
    N_1220100110_NEURAL_DYNAMICS_SCIENTIFIC_ACTIVITIES = (
        "122-01-001-10 Neural Dynamics Scientific Activities"
    )
    N_1220100220_NEURAL_DYNAMICS_U19_PROJECT_1_PERIOD_1 = (
        "122-01-002-20 Neural Dynamics U19- Project 1: Period 1"
    )
    N_1220100220_NEURAL_DYNAMICS_U19_PROJECT_2_PERIOD_1 = (
        "122-01-002-20 Neural Dynamics U19- Project 2: Period 1"
    )
    N_1229999910_NEURAL_DYNAMICS_ADMIN_DIRECT = (
        "122-99-999-10 Neural Dynamics Admin (Direct)"
    )
    SELECT = "Select..."


class Scabbing(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class SecondRoundInjIsoLevel(Enum):
    N_025 = "0.25"
    N_050 = "0.50"
    N_075 = "0.75"
    N_100 = "1.00"
    N_125 = "1.25"
    N_150 = "1.50"
    N_175 = "1.75"
    N_200 = "2.00"
    N_225 = "2.25"
    N_250 = "2.50"
    N_275 = "2.75"
    N_300 = "3.00+"
    SELECT = "Select..."


class SecondRoundIontoIssue(Enum):
    NA = "N/A"
    NO = "No"
    SELECT = "Select..."
    YES = "Yes"


class SecondRoundWorkstation(Enum):
    SELECT = "Select..."
    SWS_1 = "SWS 1"
    SWS_2 = "SWS 2"
    SWS_3 = "SWS 3"
    SWS_4 = "SWS 4"
    SWS_5 = "SWS 5"
    SWS_6 = "SWS 6"
    SWS_7 = "SWS 7"
    SWS_8 = "SWS 8"
    SWS_9 = "SWS 9"


class Secondroundiontonumber(Enum):
    IONTO_1 = "Ionto #1"
    IONTO_10 = "Ionto #10"
    IONTO_2 = "Ionto #2"
    IONTO_3 = "Ionto #3"
    IONTO_4 = "Ionto #4"
    IONTO_5 = "Ionto #5"
    IONTO_6 = "Ionto #6"
    IONTO_7 = "Ionto #7"
    IONTO_8 = "Ionto #8"
    IONTO_9 = "Ionto #9"
    NA = "N/A"
    SELECT = "Select..."


class Secondroundnanojectnumber(Enum):
    NA = "N/A"
    NJ1 = "NJ#1"
    NJ2 = "NJ#2"
    NJ3 = "NJ#3"
    NJ4 = "NJ#4"
    NJ5 = "NJ#5"
    NJ6 = "NJ#6"
    NJ7 = "NJ#7"
    NJ8 = "NJ#8"
    SELECT = "Select..."


class Sex(Enum):
    FEMALE = "Female"
    MALE = "Male"
    SELECT = "Select..."


class SinusBleed(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    NA = "N/A"
    NONE = "None"
    SELECT = "Select..."
    SEVERE = "Severe"


class SurgeryStatus(Enum):
    INJECTION_PENDING = "Injection Pending"
    NEW = "New"
    NO_SURGERY = "No Surgery"
    PHASE_2_PENDING = "Phase 2 Pending"
    PLANNED_ACUTE = "Planned Acute"
    READY_FOR_FEEDBACK = "Ready for Feedback"
    UNPLANNED_ACUTE = "Unplanned Acute"


class TouchUpStatus(Enum):
    COMPLETE = "Complete"
    PENDING = "Pending"
    SCHEDULED = "Scheduled"
    SELECT = "Select..."
    UNDER_OBSERVATION = "Under Observation"


class WindowClarity(Enum):
    ANTERIOR = "Anterior"
    CENTRAL = "Central"
    LATERAL = "Lateral"
    MEDIAL = "Medial"
    NA = "N/A"
    OTHER_IN_COMMENTS = "Other (In comments)"
    POSTERIOR = "Posterior"
    SELECT = "Select..."


@dataclass
class HeadPostInfo:
    """Container for head post information"""

    headframe_type: Optional[str] = None
    headframe_part_number: Optional[str] = None
    well_type: Optional[str] = None
    well_part_number: Optional[str] = None

    @classmethod
    def from_headpost_type(cls, headpost_type: Optional[HeadpostType]):
        """Builds HeadPostInfo from HeadPostType"""
        if headpost_type is None:
            return cls()
        elif headpost_type == HeadPostType.CAM:
            return cls(
                headframe_type="CAM-style",
                headframe_part_number="0160-100-10 Rev A",
                well_type="CAM-style",
            )
        elif headpost_type == HeadPostType.NEUROPIXEL:
            return cls(
                headframe_type="Neuropixel-style",
                headframe_part_number="0160-100-10",
                well_type="Neuropixel-style",
                well_part_number="0160-200-36",
            )
        elif headpost_type == HeadPostType.MESO_NGC:
            return cls(
                headframe_type="NGC-style",
                headframe_part_number="0160-100-10",
                well_type="Mesoscope-style",
                well_part_number="0160-200-20",
            )
        elif headpost_type == HeadPostType.WHC_NP:
            return cls(
                headframe_type="WHC #42",
                headframe_part_number="42",
                well_type="Neuropixel-style",
                well_part_number="0160-200-36",
            )
        elif headpost_type == HeadPostType.NGC:
            return cls(
                headframe_type="NGC-style", headframe_part_number="0160-100-10"
            )
        elif headpost_type == HeadPostType.AI_HEADBAR:
            return cls(headframe_type="AI Straight Headbar")
        else:
            return cls()


@dataclass
class NumberWithNotes:
    """Container to hold a parsed number from a string"""

    raw_input: Optional[str] = None
    number: Optional[float] = None
    notes: Optional[str] = None


# noinspection PyMethodParameters
class NSBList2019(BaseModel, extra=Extra.allow):
    """Data model for NSB 2019 ListItem"""

    _view_title = "New Request"

    ap_2nd_inj: None = Field(default=None, alias="AP2ndInj")
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
    craniotomy_type: Optional[CraniotomyType] = Field(
        default=None, alias="CraniotomyType"
    )
    created: Optional[datetime] = Field(default=None, alias="Created")
    dv_2nd_inj: None = Field(default=None, alias="DV2ndInj")
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
    fiber_implant1_dv: None = Field(default=None, alias="FiberImplant1DV")
    fiber_implant2: Optional[str] = Field(default=None, alias="FiberImplant2")
    fiber_implant2_dv: None = Field(default=None, alias="FiberImplant2DV")
    file_system_object_type: Optional[int] = Field(
        default=None, alias="FileSystemObjectType"
    )
    first_inj_recovery: Optional[int] = Field(
        default=None, alias="FirstInjRecovery"
    )
    first_injection_iso_duration: None = Field(
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
    hp_durotomy: Optional[bool] = Field(default=None, alias="HPDurotomy")
    hp_iso_level: Optional[float] = Field(default=None, alias="HPIsoLevel")
    hp_recovery: Optional[float] = Field(default=None, alias="HPRecovery")
    hp_requestor_comments_plaintext: Optional[str] = Field(
        default=None, alias="HPRequestorCommentsPlaintext"
    )
    hp_surgeon_comments: Optional[str] = Field(
        default=None, alias="HPSurgeonComments"
    )
    hp_ap: None = Field(default=None, alias="HP_x0020_A_x002f_P")
    hp_diameter: Optional[float] = Field(
        default=None, alias="HP_x0020_Diameter"
    )
    hp_ml: None = Field(default=None, alias="HP_x0020_M_x002f_L")
    hp_inj: Optional[str] = Field(
        default=None, alias="HP_x0020__x0026__x0020_Inj"
    )
    headpost_type: Optional[HeadPostType] = Field(
        default=None, alias="HeadpostType"
    )
    hemisphere_2nd_inj: Optional[Hemisphere] = Field(
        default=None, alias="Hemisphere2ndInj"
    )
    hp_loc: Optional[Hemisphere] = Field(default=None, alias="HpLoc")
    hp_perf: Optional[str] = Field(default=None, alias="HpPerf")
    hp_prev_inject: Optional[str] = Field(default=None, alias="HpPrevInject")
    hp_work_station: Optional[str] = Field(default=None, alias="HpWorkStation")
    iacuc_protocol: Optional[str] = Field(
        default=None, alias="IACUC_x0020_Protocol_x0020__x002"
    )
    id1: Optional[int] = Field(default=None, alias="ID")
    id2: Optional[int] = Field(default=None, alias="Id")
    implant_id_coverslip_type: Optional[NumberWithNotes] = Field(
        default=None, alias="ImplantIDCoverslipType"
    )
    inj1_alternating_time: None = Field(
        default=None, alias="Inj1AlternatingTime"
    )
    inj1_angle_v2: None = Field(default=None, alias="Inj1Angle_v2")
    inj1_current: None = Field(default=None, alias="Inj1Current")
    inj1_length_of_time: None = Field(default=None, alias="Inj1LenghtofTime")
    inj1_round: Optional[str] = Field(default=None, alias="Inj1Round")
    inj1_storage_location: Optional[str] = Field(
        default=None, alias="Inj1StorageLocation"
    )
    inj1_type: Optional[InjectionType] = Field(default=None, alias="Inj1Type")
    inj1_virus_strain_rt: None = Field(
        default=None, alias="Inj1VirusStrain_rt"
    )
    inj1_vol: None = Field(default=None, alias="Inj1Vol")
    inj1_angle0: None = Field(default=None, alias="Inj1angle0")
    inj2_alternating_time: None = Field(
        default=None, alias="Inj2AlternatingTime"
    )
    inj2_angle_v2: None = Field(default=None, alias="Inj2Angle_v2")
    inj2_current: None = Field(default=None, alias="Inj2Current")
    inj2_length_of_time: None = Field(default=None, alias="Inj2LenghtofTime")
    inj2_round: Optional[str] = Field(default=None, alias="Inj2Round")
    inj2_storage_location: Optional[str] = Field(
        default=None, alias="Inj2StorageLocation"
    )
    inj2_type: Optional[InjectionType] = Field(default=None, alias="Inj2Type")
    inj2_virus_strain_rt: None = Field(
        default=None, alias="Inj2VirusStrain_rt"
    )
    inj2_vol: None = Field(default=None, alias="Inj2Vol")
    inj2_angle0: None = Field(default=None, alias="Inj2angle0")
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
    labtracks_requestor: Optional[SecretStr] = Field(
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
    ml_2nd_inj: None = Field(default=None, alias="ML2ndInj")
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
    pi_id: Optional[int] = Field(default=None, alias="PIId")
    pi_string_id: Optional[str] = Field(default=None, alias="PIStringId")
    pedigree_name: Optional[str] = Field(default=None, alias="PedigreeName")
    procedure: Optional[str] = Field(default=None, alias="Procedure")
    project_id_te: Optional[str] = Field(
        default=None, alias="Project_x0020_ID_x0020__x0028_te"
    )
    round1_inj_iso_level: None = Field(default=None, alias="Round1InjIsolevel")
    round2_inj_iso_level: None = Field(default=None, alias="Round2InjIsolevel")
    scabbing: Optional[str] = Field(default=None, alias="Scabbing")
    second_inj_recovery: Optional[int] = Field(
        default=None, alias="SecondInjRecover"
    )
    second_injection_iso_duration: None = Field(
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
    sex: Optional[Sex] = Field(default=None, alias="Sex")
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
    virus_ap: None = Field(default=None, alias="Virus_x0020_A_x002f_P")
    virus_dv: None = Field(default=None, alias="Virus_x0020_D_x002f_V")
    virus_hemisphere: Optional[Hemisphere] = Field(
        default=None, alias="Virus_x0020_Hemisphere"
    )
    virus_ml: None = Field(default=None, alias="Virus_x0020_M_x002f_L")
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
    inj1_vol_per_depth: None = Field(default=None, alias="inj1volperdepth")
    inj2_vol_per_depth: None = Field(default=None, alias="inj2volperdepth")
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
        "first_injection_weight_after",
        "first_injection_weight_before",
        "hp_iso_level",
        "hp_recovery",
        "hp_diameter",
        "second_injection_weight_after",
        "second_injection_weight_before",
        "touch_up_weight",
        "weight_after_surgery",
        "weight_before_surgery",
        "field30",
        "field50",
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
        "fiber_implant2",
        "first_round_ionto_issue",
        "guid",
        "hp_requestor_comments_plaintext",
        "hp_surgeon_comments",
        "hp_inj",
        "hp_perf",
        "hp_prev_inject",
        "hp_work_station",
        "iacuc_protocol",
        "inj1_round",
        "inj1_storage_location",
        "inj2_round",
        "inj2_storage_location",
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
        "implant_id_coverslip_type",
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

    @validator("craniotomy_type", pre=True)
    def parse_craniotomy_type(
        cls, v: Optional[str]
    ) -> Optional[CraniotomyType]:
        """Match like 'Visual Cortex 5mm'"""
        if type(v) is str and v in [e.value for e in CraniotomyType]:
            return CraniotomyType(v)
        else:
            return None

    @validator("headpost_type", pre=True)
    def parse_headpost_type(cls, v: Optional[str]) -> Optional[HeadPostType]:
        """Parses string into a HeadPostType"""
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

    @validator("hemisphere_2nd_inj", "hp_loc", "virus_hemisphere", pre=True)
    def parse_hemisphere_type(cls, v: Optional[str]) -> Optional[Hemisphere]:
        """Parses string into Hemisphere model"""
        if type(v) is str and v in [e.value for e in Hemisphere]:
            return Hemisphere(v)
        else:
            return None

    @validator("inj1_type", "inj2_type", pre=True)
    def parse_injection_type(cls, v: Optional[str]) -> Optional[InjectionType]:
        """Parses string into InjectionType"""
        if type(v) is str and v in [e.value for e in InjectionType]:
            return InjectionType(v)
        else:
            return None

    @validator("hp_durotomy", pre=True)
    def parse_str_to_bool(cls, v: Optional[str]) -> Optional[bool]:
        """Parses string like 'Yes', 'No', etc. into a bool"""
        if v is None:
            return None
        elif type(v) == str and v.upper() in (
            [
                "YES",
                "Y",
                "1",
                "T",
                "TRUE",
            ]
        ):
            return True
        elif type(v) == str and v.upper() in (
            [
                "NO",
                "N",
                "0",
                "F",
                "FALSE",
            ]
        ):
            return False
        else:
            return None

    # TODO: Add special parsing for following fields
    @validator(
        "ap_2nd_inj",
        "dv_2nd_inj",
        "fiber_implant1_dv",
        "fiber_implant2_dv",
        "first_injection_iso_duration",
        "hp_ap",
        "hp_ml",
        "inj1_alternating_time",
        "inj1_angle_v2",
        "inj1_current",
        "inj1_length_of_time",
        "inj1_virus_strain_rt",
        "inj1_vol",
        "inj1_angle0",
        "inj2_alternating_time",
        "inj2_angle_v2",
        "inj2_current",
        "inj2_length_of_time",
        "inj2_virus_strain_rt",
        "inj2_vol",
        "inj2_angle0",
        "ml_2nd_inj",
        "round1_inj_iso_level",
        "round2_inj_iso_level",
        "second_injection_iso_duration",
        "virus_ap",
        "virus_dv",
        "virus_ml",
        "inj1_vol_per_depth",
        "inj2_vol_per_depth",
        pre=True,
    )
    def parse_inconsistent_inputs(cls, _: Optional[str]) -> None:
        """Placeholder method that maps strings to None. Will need to add
        special handling of these fields down the road."""
        return None

    def has_hp_procedure(self) -> bool:
        """Is there a headpost procedure?"""
        return self.procedure is not None and (
            "HP" in self.procedure or "Headpost" in self.procedure
        )

    def has_inj_procedure(self) -> bool:
        """Is there an injection procedure?"""
        return self.procedure is not None and (
            "INJ" in self.procedure or "Injection" in self.procedure
        )

    def has_2nd_inj_procedure(self) -> bool:
        """Is there a 2nd injection procedure?"""
        return self.has_inj_procedure() and self.inj2_round is not None

    def has_cran_procedure(self) -> bool:
        """Is there a craniotomy procedure?"""
        return self.procedure is not None and (
            "HP+C" in self.procedure
            or "WHC NP" in self.procedure
            or "C CAM" in self.procedure
        )

    def has_fiber_implant_procedure(self) -> bool:
        """Is there a fiber implant procedure?"""
        return self.procedure is not None and "Fiber Implant" in self.procedure
