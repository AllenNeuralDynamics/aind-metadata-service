"""Configuration and settings for the ExaSPIM procedures generation pipeline."""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


# Default sheet IDs for the ExaSPIM pipeline
DEFAULT_SHEET_IDS: dict[str, int] = {
    "Mouse Tracker": 4574277042917252,
    "Sample Tracking": 3142827793928068,
    "Imaging Queue": 2709792011276164,
    "QC Sheet": 93261067669380,
}


class SheetName(str, Enum):
    """Canonical names for each Smartsheet used by the ExaSPIM pipeline."""

    MOUSE_TRACKER = "Mouse Tracker"
    SAMPLE_TRACKING = "Sample Tracking"
    IMAGING_QUEUE = "Imaging Queue"
    QC_SHEET = "QC Sheet"


class Settings(BaseModel):
    """Runtime settings including the Smartsheet token and sheet ID lookup.

    Attributes
    ----------
    smartsheet_access_token : str
        API access token for Smartsheet.
    sheet_lookup : dict[str, int]
        Mapping from SheetName values to Smartsheet numeric IDs.
    """

    smartsheet_access_token: str = Field(..., min_length=1)
    sheet_lookup: dict[str, int]

    @field_validator("sheet_lookup")
    @classmethod
    def validate_sheet_lookup(cls, value: dict[str, int]) -> dict[str, int]:
        """Ensure all required sheet names are present in the lookup."""
        missing = [
            sheet.value for sheet in SheetName if sheet.value not in value
        ]
        if missing:
            raise ValueError(f"Missing required sheet IDs: {missing}")
        return value

    def get_sheet_id(self, sheet_name: SheetName) -> int:
        """Return the Smartsheet ID for a given sheet name."""
        return self.sheet_lookup[sheet_name.value]


def load_settings(config_path: str | Path | None = None) -> Settings:
    """Load Settings from the environment and optional JSON config file.

    Parameters
    ----------
    config_path : str | Path | None
        Path to a JSON file mapping sheet names to IDs.
        If None, uses the built-in DEFAULT_SHEET_IDS.

    Returns
    -------
    Settings
        Validated settings object.

    Raises
    ------
    ValueError
        If SMARTSHEET_ACCESS_TOKEN is not set, or if config file is missing.
    """
    token = os.getenv("SMARTSHEET_ACCESS_TOKEN", "")
    if not token:
        raise ValueError(
            "SMARTSHEET_ACCESS_TOKEN environment variable is required."
        )

    if config_path is not None:
        path = Path(config_path)
        if not path.exists():
            raise ValueError(f"Sheet lookup file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            sheet_lookup = json.load(f)
    else:
        sheet_lookup = DEFAULT_SHEET_IDS.copy()

    return Settings(smartsheet_access_token=token, sheet_lookup=sheet_lookup)
