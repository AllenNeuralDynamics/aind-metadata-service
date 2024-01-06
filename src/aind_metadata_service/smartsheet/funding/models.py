"""Module contains the expected data models in SmartSheet response"""

from enum import Enum


class FundingColumnNames(str, Enum):
    """These are the expected columns we expect in the Funding SmartSheet"""

    PROJECT_CODE = "Project Code"
    FUNDING_SOURCE = "Funding Source"
    PROJECT_NAME = "Project Name"
    PROJECT_CODE_AND_NAME = "Project Code & Name"
    INSTITUTION = "Institution"
    GRANT_NUMBER = "Grant Number"
    INVESTIGATORS = "Investigators"
