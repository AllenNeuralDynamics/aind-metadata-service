"""Module for Generic SmartSheet API data models"""

from datetime import datetime
from typing import Any, List, Optional, Union

from pydantic import BaseModel, field_validator


class SheetColumn(BaseModel):
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
    hidden: Optional[bool] = None


class SheetRowCell(BaseModel):
    """SmartSheet 'row.cell' information"""

    columnId: int
    displayValue: Optional[str] = None
    value: Optional[Union[str, float]] = None


class SheetRow(BaseModel):
    """SmartSheet row information"""

    cells: List[SheetRowCell]
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


class SheetFields(BaseModel):
    """SmartSheet information"""

    columns: List[SheetColumn]
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
    rows: List[SheetRow]
    totalRowCount: int
    userPermissions: dict
    userSettings: dict
    version: int
    workspace: dict = {}

    @field_validator("createdAt", "modifiedAt", mode="before")
    def parse_datetime_str(cls, value: Any) -> datetime:
        """Adds handling of datetime strings that end with both offset and Z"""
        if isinstance(value, str) and value.endswith("+00:00Z"):
            return datetime.fromisoformat(value.replace("+00:00Z", "+00:00"))
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value
