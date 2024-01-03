"""Module contains the expected data models in SmartSheet response"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, field_validator


class FundingColumnNames(str, Enum):
    """These are the expected columns we expect in the Funding SmartSheet"""

    PROJECT_CODE = "Project Code"
    FUNDING_SOURCE = "Funding Source"
    PROJECT_NAME = "Project Name"
    PROJECT_CODE_AND_NAME = "Project Code & Name"
    INSTITUTION = "Institution"
    GRANT_NUMBER = "Grant Number"
    INVESTIGATORS = "Investigators"


# TODO: This is probably a generic SmartSheet model and not specific to the
#  Funding sheet. We can probably move these elsewhere.


class FundingColumn(BaseModel):
    """SmartSheet column information"""

    id: int
    index: int
    title: str
    type: str
    validation: bool
    version: int
    width: int
    options: List[str] = []
    primary: bool = False


class FundingRowCell(BaseModel):
    """SmartSheet 'row.cell' information"""

    columnId: int
    displayValue: Optional[str] = None
    value: Optional[str] = None


class FundingRow(BaseModel):
    """SmartSheet row information"""

    cells: List[FundingRowCell]
    createdAt: datetime
    expanded: bool
    id: int
    modifiedAt: datetime
    rowNumber: int

    @field_validator("createdAt", "modifiedAt", mode="before")
    def parse_datetime_str(cls, value: Any) -> datetime:
        """Adds handling of datetime strings that end with both offset and Z"""
        if isinstance(value, str) and value.endswith("+00:00Z"):
            return datetime.fromisoformat(value.replace("+00:00Z", "+00:00"))
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value


class FundingSheet(BaseModel):
    """SmartSheet information"""

    columns: List[FundingColumn]
    accessLevel: str
    createdAt: datetime
    dependenciesEnabled: bool
    effectiveAttachmentOptions: List[str]
    ganttEnabled: bool
    hasSummaryFields: bool
    id: int
    modifiedAt: datetime
    name: str
    permalink: str
    readOnly: bool
    resourceManagementEnabled: bool
    rows: List[FundingRow]
    totalRowCount: int
    userPermissions: dict
    userSettings: dict
    version: int
    workspace: dict

    @field_validator("createdAt", "modifiedAt", mode="before")
    def parse_datetime_str(cls, value: Any) -> datetime:
        """Adds handling of datetime strings that end with both offset and Z"""
        if isinstance(value, str) and value.endswith("+00:00Z"):
            return datetime.fromisoformat(value.replace("+00:00Z", "+00:00"))
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value
