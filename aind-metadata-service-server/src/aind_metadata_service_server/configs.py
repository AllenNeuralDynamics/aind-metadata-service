"""Module for settings to connect to backend"""

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    ### Settings needed to connect to a database or website.
    We will just connect to an example website.
    """

    model_config = SettingsConfigDict(env_prefix="AIND_METADATA_SERVICE_")

    labtracks_host: HttpUrl = Field(
        ..., description="Host address for labtracks endpoint"
    )
    smartsheet_host: HttpUrl = Field(
        ..., description="Host address for smartsheet endpoint"
    )


def get_settings():
    """Return Settings object"""
    return Settings()
