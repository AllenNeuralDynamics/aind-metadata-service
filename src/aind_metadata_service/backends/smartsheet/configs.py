"""Module to handle settings"""

from aind_smartsheet_api.client import SmartsheetSettings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmartsheetAppConfigs(BaseSettings):
    """Smartsheet configs with client settings and sheet IDs"""

    client_settings: SmartsheetSettings = Field(
        ..., description="Settings for Smartsheet client."
    )
    funding_id: int = Field(..., description="SmartSheet ID of funding info")
    perfusions_id: int = Field(
        ..., description="SmartSheet ID of perfusions info"
    )
    protocols_id: int = Field(
        ..., description="SmartSheet ID of protocols info"
    )
    model_config = SettingsConfigDict(env_prefix="SMARTSHEET_")


def get_settings() -> SmartsheetAppConfigs:
    """Utility method to return a settings object."""
    client_settings = SmartsheetSettings()
    return SmartsheetAppConfigs(client_settings=client_settings)
