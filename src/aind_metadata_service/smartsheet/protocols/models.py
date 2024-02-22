"""Module contains the expected data models in SmartSheet response"""

from enum import Enum


class ProtocolsColumnNames(str, Enum):
    """These are the expected columns we expect in the Protocols SmartSheet"""

    PROTOCOL_TYPE = "Protocol Type"
    PROCEDURE_NAME = "Procedure name"
    PROTOCOL_NAME = "Protocol name"
    DOI = "DOI"
    VERSION = "Version"
    PROTOCOL_COLLECTION = "Protocol collection"
    PRIORITY = "Priority "
