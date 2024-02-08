"""Module contains the expected data models in SmartSheet response"""

from enum import Enum


class FundingColumnNames(str, Enum):
    """These are the expected columns we expect in the Funding SmartSheet"""

    PROJECT_NAME = "Project Name"
    PROJECT_CODE = "Project Code"
    FUNDING_INSTITUTION = "Funding Institution"
    GRANT_NUMBER = "Grant Number"
    INVESTIGATORS = "Investigators"
