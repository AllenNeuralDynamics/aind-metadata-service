"""Module contains the expected data models in SmartSheet response"""

from enum import Enum


class PerfusionsColumnNames(str, Enum):
    """These are the expected columns we expect in the Perfusions SmartSheet"""

    SUBJECT_ID = "subject id"
    DATE = "date"
    EXPERIMENTER = "experimenter"
    IACUC_PROTOCOL = "iacuc protocol"
    ANIMAL_WEIGHT_PRIOR = "animal weight prior (g)"
    OUTPUT_SPECIMEN_ID = "Output specimen id(s)"
    POSTFIX_SOLUTION = "Postfix solution"
    NOTES = "Notes"


# TODO: Import this from somewhere
class PerfusionProtocol(str, Enum):
    """Protocol ids"""

    ID_10_17504 = "dx.doi.org/10.17504/protocols.io.bg5vjy66"
