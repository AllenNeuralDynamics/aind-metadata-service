"""Models for SLIMS data"""

from enum import Enum


class SlimsWashNames(str, Enum):
    """Enum class of Slims Wash Names"""

    WASH_1 = "Wash 1"
    WASH_2 = "Wash 2"
    WASH_3 = "Wash 3"
    WASH_4 = "Wash 4"
    REFRACTIVE_INDEX_MATCHING = "Refractive Index Matching Wash"
    PRIMARY_ANTIBODY_WASH = "Primary Antibody Wash"
    SECONDARY_ANTIBODY_WASH = "Secondary Antibody Wash"
    MBS_WASH = "MBS Wash"
    GELATION_PBS_WASH = "Gelation PBS Wash"
    STOCK_X_VA = "Stock X + VA-044 Equilibration"
    GELATION_PROK = "Gelation + ProK RT"
    GELATION_ADDL = "Gelation + Add'l ProK 37C"
    FINAL_PBS_WASH = "Final PBS Wash"


class SlimsExperimentTemplateNames(str, Enum):
    """Enum class of Experiment Template Names"""

    SMARTSPIM_DELIPIDATION = "SmartSPIM Delipidation"
    SMARTSPIM_LABELING = "SmartSPIM Labeling"
    SMARTSPIM_RI_MATCHING = "SmartSPIM Refractive Index Matching"
    EXASPIM_DELIPIDATION = "ExaSPIM Delipidation"
    EXASPIM_LABELING = "ExaSPIM Labeling"
    EXASPIM_GELATION = "ExaSPIM Gelation"
    EXASPIM_EXPANSION = "ExaSPIM Expansion"
